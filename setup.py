import pandas as pd
from cassandra.cluster import Cluster
import uuid
import requests
from tqdm import tqdm


def download_dataset(url, local_filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            f.write(response.content)
    else:
        print("Failed to download the dataset")
        exit(1)


def setup_cassandra(n_books=15000):
    cluster = Cluster(['127.0.0.1', '127.0.0.2', '127.0.0.3'])
    session = cluster.connect()

    # check if connected
    session.execute("SELECT now() FROM system.local")
    print("Connected to the cassandra cluster successfully.")

    session.execute("""
    CREATE KEYSPACE IF NOT EXISTS library WITH REPLICATION = 
    { 'class' : 'SimpleStrategy', 'replication_factor' : 3 };
    """)

    # reservations: partition on book_id (unique - cannot reserve the same book twice)
    session.execute("""
    CREATE TABLE IF NOT EXISTS library.reservations (
        user_id UUID,
        book_id UUID,
        reserved_at TIMESTAMP,
        id UUID,
        PRIMARY KEY ((book_id))
    );
    """)

    # session.execute("""
    # CREATE TABLE IF NOT EXISTS library.users (
    #     id UUID PRIMARY KEY,
    #     name TEXT,
    #     email TEXT
    # );
    # """)

    session.execute("""
    CREATE TABLE IF NOT EXISTS library.books (
        category TEXT,
        title TEXT,
        id UUID,
        author TEXT,
        image_url TEXT,
        PRIMARY KEY ((id))
    );
    """)

    # check
    rows = session.execute(
        "SELECT table_name FROM system_schema.tables WHERE keyspace_name = 'library'")
    tables_created = [row.table_name for row in rows]
    if 'reservations' in tables_created and 'users' in tables_created and 'books' in tables_created:
        print("Tables created successfully.")
    else:
        print("Error: Tables could not be created.")

    # populate the books table
    local_filename = 'books.csv'
    books_df = pd.read_csv(local_filename, header=None, encoding="ISO-8859-1")
    books_df.columns = ["isbn", "image_filename",
                        "image_url", "title", "author", "_", "category"]
    # filter
    books_df.replace('', pd.NA, inplace=True)
    filtered_books_df = books_df.dropna().head(n_books)

    for index, row in tqdm(filtered_books_df.iterrows(), total=filtered_books_df.shape[0], desc="Inserting books..."):
        session.execute("""
            INSERT INTO library.books (id, title, author, image_url, category)
            VALUES (%s, %s, %s, %s, %s)
            """, (uuid.uuid4(), row['title'], row['author'], row['image_url'], row['category']))

    # check if inserted
    rows = session.execute("SELECT count(*) FROM library.books")
    count = rows.one()[0]
    if count > 0:
        print("Books table populated successfully.")
    else:
        print("Error: Books table is empty.")


if __name__ == "__main__":
    # download the dataset
    dataset_url = 'https://raw.githubusercontent.com/uchidalab/book-dataset/master/Task1/book30-listing-train.csv'
    local_filename = 'books.csv'
    download_dataset(dataset_url, local_filename)

    # setup cassandra and populate books
    setup_cassandra(n_books=1000)
