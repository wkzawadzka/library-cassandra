from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from uuid import UUID, uuid4
from pydantic import BaseModel, UUID4
import datetime
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from cassandra import Unauthorized, ConsistencyLevel
from typing import List

cluster = Cluster(['127.0.0.1', '127.0.0.2', '127.0.0.3'])
session = cluster.connect('library')

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# global prepared statements
check_statement = session.prepare("SELECT * FROM books WHERE id = ?")
insert_statement = session.prepare("""
    INSERT INTO reservations (id, user_id, book_id, reserved_at)
    VALUES (?, ?, ?, ?)
    IF NOT EXISTS
    """)
update_stmt = session.prepare(
    "UPDATE reservations SET user_id = ? WHERE book_id = ? IF EXISTS")
select_stmt = session.prepare(
    "SELECT id, reserved_at FROM reservations WHERE book_id = ?")
reservation_statement = session.prepare(
    "SELECT * FROM reservations WHERE book_id = ?")
delete_stmt = session.prepare(
    "DELETE FROM reservations WHERE book_id = ? IF EXISTS")


class ReservationRequest(BaseModel):
    user_id: UUID4
    book_id: UUID4


class Reservation(BaseModel):
    id: UUID4
    user_id: UUID4
    book_id: UUID4
    reserved_at: datetime.datetime


class Update(BaseModel):
    old_book_id: UUID4
    user_id: UUID4
    book_id: UUID4


@app.post("/reservations/", response_model=Reservation)
def make_reservation(reservation_request: ReservationRequest):
    user_id = reservation_request.user_id
    book_id = reservation_request.book_id
    reservation_id = uuid4()
    reserved_at = datetime.datetime.now()

    # check if the book in the library
    book_exists = session.execute(check_statement, (book_id,)).one()
    if not book_exists:
        raise HTTPException(
            status_code=404, detail="Book not in the library")

    # insert the reservation
    result = session.execute(insert_statement, (reservation_id,
                                                user_id, book_id, reserved_at))
    if not result.one().applied:
        raise HTTPException(
            status_code=400, detail="This book is already reserved")

    reservation = Reservation(
        id=reservation_id,
        user_id=user_id,
        book_id=book_id,
        reserved_at=reserved_at
    )
    return reservation


@app.put("/reservations/update/", response_model=Reservation)
def update_reservation(reservation_change: Update):
    # 2 cases:
    #   user_id is changed, book_id unchanged -> use UPDATE
    #   book_id changed -> DELETE & INSERT
    old_book_id = reservation_change.old_book_id
    user_id = reservation_change.user_id
    book_id = reservation_change.book_id

    # check if the book in the library
    book_exists = session.execute(check_statement, (book_id,)).one()
    if not book_exists:
        raise HTTPException(
            status_code=404, detail="Book not in the library")

    if old_book_id != book_id:
        # book_id (primary key) changed
        delete_reservation(old_book_id)
        reservation_request = ReservationRequest(
            user_id=user_id, book_id=book_id)
        reservation = make_reservation(reservation_request)

    else:
        # book_id did not change
        result = session.execute(update_stmt, (user_id, old_book_id))
        if not result.one().applied:
            raise HTTPException(
                status_code=400, detail="Reservation not found")
        reservation = session.execute(select_stmt, (old_book_id,)).one()

    updated_reservation = Reservation(
        id=reservation.id,
        user_id=user_id,
        book_id=book_id,
        reserved_at=reservation.reserved_at
    )

    return updated_reservation


@app.get("/api/reservations")
async def get_reservations(paging_state=None):
    '''
    Get all the reservations with pagination
    '''
    statement = SimpleStatement("SELECT * FROM reservations", fetch_size=25)

    if paging_state:
        statement = statement.set_paging_state(bytes.fromhex(paging_state))

    rows = session.execute(statement)
    reservations = []

    for row in rows:
        reservation = {
            "id": row.id,
            "user_id": row.user_id,
            "book_id": row.book_id,
            "reserved_at": row.reserved_at
        }
        reservations.append(reservation)

    next_paging_state = None
    if rows.has_more_pages:
        next_paging_state = rows.paging_state.hex()

    return {
        "reservations": reservations,
        "next_paging_state": next_paging_state
    }


@app.get("/api/reservations/{book_id}")
async def get_reservation_details(book_id: UUID):
    reservation = session.execute(reservation_statement, (book_id,)).one()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    book = session.execute(check_statement, (reservation.book_id,)).one()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    reservation_details = {
        "id": reservation.id,
        "user_id": reservation.user_id,
        "book_id": reservation.book_id,
        "reserved_at": reservation.reserved_at,
        "book": {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "image_url": book.image_url,
            "category": book.category
        }
    }
    return reservation_details


@app.delete("/reservations/{book_id}")
def delete_reservation(book_id: UUID):
    result = session.execute(delete_stmt, (book_id,))
    if not result.one().applied:
        raise HTTPException(status_code=400, detail="Reservation not found")
    return {"detail": "Reservation deleted"}


def delete_all_reservations():
    # just for testing
    session.execute("TRUNCATE reservations")
    return {"detail": "All reservations deleted"}


def get_all_book_ids() -> List[str]:
    query = "SELECT id FROM books"
    rows = session.execute(query)

    book_ids = [row.id for row in rows]

    return book_ids


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
