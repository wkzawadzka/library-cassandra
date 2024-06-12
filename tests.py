import api
import setup
import unittest
from uuid import UUID, uuid4
from tqdm import tqdm
import random
import threading
import time
from typing import Optional, Dict, List
import concurrent.futures


class Tests(unittest.TestCase):
    def test1_same_request(self) -> None:
        '''
        The client makes the same request very quickly min (10000 times).
        '''
        api.delete_all_reservations()  # clean up
        user_id: UUID = uuid4()  # random user_id
        # some book from the library
        book_id: UUID = UUID("144802ea-d54c-45eb-98e5-9533497e6998")

        successful_reservations: int = 0
        unsuccessful_reservations: int = 0
        lock = threading.Lock()  # access to shared variables

        def make_reservation() -> None:
            # to work with variables inside nested functions
            nonlocal successful_reservations, unsuccessful_reservations
            try:
                reservation: Optional[api.ReservationResponse] = api.make_reservation(
                    api.ReservationRequest(user_id=user_id, book_id=book_id)
                )
                if reservation:
                    with lock:
                        successful_reservations += 1
            except Exception as e:
                with lock:
                    unsuccessful_reservations += 1
                pass

        threads = []
        for _ in tqdm(range(10000), desc="Making Reservations"):
            t = threading.Thread(target=make_reservation)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        api.delete_all_reservations()  # clean up
        print(f"Made {successful_reservations} successful reservations")
        print(f"Made {unsuccessful_reservations} unsuccessful reservations")
        self.assertEqual(successful_reservations, 1, "Test 1 failed.")

    def test2_random_requests(self) -> None:
        ''' Two or more clients make the possible requests randomly (10000 times) '''
        user_id1: UUID = uuid4()
        user_id2: UUID = uuid4()
        book_ids: List[str] = api.get_all_book_ids()[:1000]

        successful_reservations: Dict[UUID, int] = {
            user_id1: 0, user_id2: 0}
        unsuccessful_reservations: Dict[UUID, int] = {
            user_id1: 0, user_id2: 0}
        lock = threading.Lock()

        def make_reservation(user_id: UUID) -> None:
            for _ in tqdm(range(5000), desc="Making Reservations"):
                book_id: str = random.choice(book_ids)
                try:
                    reservation: Optional[api.ReservationResponse] = api.make_reservation(
                        api.ReservationRequest(
                            user_id=user_id, book_id=book_id)
                    )
                    if reservation:
                        with lock:
                            successful_reservations[user_id] += 1
                except Exception:
                    with lock:
                        unsuccessful_reservations[user_id] += 1

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(make_reservation, user_id1), executor.submit(
                make_reservation, user_id2)]

            for future in concurrent.futures.as_completed(futures):
                future.result()

        # clean up after test
        api.delete_all_reservations()
        print(
            f"User 1 made {successful_reservations[user_id1]} successful reservations and {unsuccessful_reservations[user_id1]} unsuccessful reservations")
        print(
            f"User 2 made {successful_reservations[user_id2]} successful reservations and {unsuccessful_reservations[user_id2]} unsuccessful reservations")

    def test3_all_seats(self) -> None:
        """
        Immediate occupancy of all seats/reservations by 2 clients.
        """
        user_id1: UUID = uuid4()
        user_id2: UUID = uuid4()
        api.delete_all_reservations()  # clean up
        reservations_pool: List[str] = api.get_all_book_ids()
        successful_claims: Dict[UUID, int] = {user_id1: 0, user_id2: 0}
        unsuccessful_claims: Dict[UUID, int] = {user_id1: 0, user_id2: 0}

        global reservations_pool_lock
        reservations_pool_lock = threading.Lock()

        def claim_reservations(user_id: UUID, reservations_pool: List[str], successful_claims: Dict[UUID, int], unsuccessful_claims: Dict[uuid.UUID, int]) -> None:
            while reservations_pool:
                book_id = random.choice(reservations_pool)
                try:
                    reservation: Optional[api.ReservationResponse] = api.make_reservation(
                        api.ReservationRequest(
                            user_id=user_id, book_id=book_id)
                    )
                    if reservation:
                        successful_claims[user_id] += 1
                        with reservations_pool_lock:
                            reservations_pool.remove(book_id)
                except Exception as e:
                    pass
                    # print(f"An error occurred for user {user_id}: {e}")

        threads = [
            threading.Thread(target=claim_reservations, args=(
                user_id1, reservations_pool, successful_claims, unsuccessful_claims)),
            threading.Thread(target=claim_reservations, args=(
                user_id2, reservations_pool, successful_claims, unsuccessful_claims))
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        api.delete_all_reservations()  # clean up

        print(
            f"User {user_id1} claimed {successful_claims[user_id1]} reservations and {unsuccessful_claims[user_id1]} unsuccessful claims")
        print(
            f"User {user_id2} claimed {successful_claims[user_id2]} reservations and {unsuccessful_claims[user_id2]} unsuccessful claims")

    def test4_reserve_cancel(self):
        user_id1 = uuid4()
        user_id2 = uuid4()
        # some book from the library
        book_id: UUID = UUID("144802ea-d54c-45eb-98e5-9533497e6998")

        api.delete_all_reservations()  # clean up

        def make_reservation(user_id, user="A") -> None:
            for _ in range(5000):
                # reserve
                try:
                    reservation: Optional[api.ReservationResponse] = api.make_reservation(
                        api.ReservationRequest(
                            user_id=user_id, book_id=book_id)
                    )
                    if reservation:
                        print(f"User {user} successfully reserved the book")
                        time.sleep(random.uniform(0.05, 0.3))
                        try:
                            delete_operation = api.delete_reservation(book_id)
                            if delete_operation:
                                print(f"User {user} cancelled the reservation")
                        except Exception as e:
                            print(f"User {user} failed to cancell reservation")
                except Exception as e:
                    print(f"User {user} failed to reserve the book")

        threads = []
        for user_id, user in zip([user_id1, user_id2], ["A", "B"]):
            t = threading.Thread(target=make_reservation, args=(user_id, user))
            t.start()
            threads.append(t)
            print(f"Thread for user {user_id} started")

        for t in threads:
            t.join()

        api.delete_all_reservations()  # clean up

    def test5_udates(self):
        api.delete_all_reservations()
        reservations_pool: List[str] = api.get_all_book_ids()[:1000]

        def make_reservations(book_id) -> None:
            try:
                api.make_reservation(
                    api.ReservationRequest(user_id=uuid4(), book_id=book_id)
                )
            except Exception as e:
                pass

        threads = []
        for book_id in tqdm(reservations_pool, desc="Adding Reservations..."):
            t = threading.Thread(target=make_reservations, args=(book_id,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        successful_updates: int = 0
        lock = threading.Lock()

        def make_update():
            nonlocal successful_updates
            for book_id in tqdm(reservations_pool, desc="Making Updates"):
                new_user_id = uuid4()
                update = api.Update(old_book_id=book_id,
                                    user_id=new_user_id, book_id=book_id)
                # update user_id
                try:
                    update = api.update_reservation(update)
                    if update:
                        with lock:
                            successful_updates += 1
                except Exception as e:
                    print(e)
                    pass

        t = threading.Thread(target=make_update)
        t.start()
        t.join()

        api.delete_all_reservations()
        print(f"Made {successful_updates} updates")
