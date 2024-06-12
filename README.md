authors: Weronika Zawadzka & Eliza Czaplicka

Final project for **Big data and distributed processing** class at Poznan Univerity of Technology.

# Cassandra Library Reservation System

This project is a distributed library reservation system using Apache Cassandra. It supports creating, updating, viewing, and canceling reservations, and includes stress tests to evaluate system performance under load. This project is built using FastAPI for the backend and React with Material-UI (MUI) for the frontend.

## Table of Contents

- [Prerequisites](#prerequisites)
- [How to Run](#how-to-run)
- [Database structure](#database-structure)
- [Dataset](#dataset)
- [Demo](#demo)

## Prerequisites

- Python 3.6+
- Apache Cassandra 3.11+
- `cassandra-driver` Python package

## How to run

### Step 0

`pip install -r requirements.txt`

### Step 1: Create a docker network & run clusters

Run `docker-compose up -d`

Wait a minute or two after this command :)

### Step 2: Create tables and populate books

Run `python setup.py`

### Step 3: Start app

Run `uvicorn api:app --reload`

Then in another terminal: `npm start`

## Database structure

1. **books**: This table stores information about books available in the library. We ensure that each book has a unique identifier. The `books` table has columns for `category`, `title`, `id`, `author`, and `image_url`.

2. **reservations**: This table stores information about book reservations made by users. A book with given book_id can be reserved only once. The `reservations` table has columns for `user_id`, `book_id`, `reserved_at`, and `id`.

| Table Name           | Column      | Type      | Key     |
| -------------------- | ----------- | --------- | ------- |
| library.books        | category    | TEXT      |         |
|                      | title       | TEXT      |         |
|                      | id          | UUID      | Primary |
|                      | author      | TEXT      |         |
|                      | image_url   | TEXT      |         |
| library.reservations | user_id     | UUID      |         |
|                      | book_id     | UUID      | Primary |
|                      | reserved_at | TIMESTAMP |         |
|                      | id          | UUID      |         |

## Dataset

[Books Cover Dataset](https://github.com/uchidalab/book-dataset) has been used in this project to populate books table. All the other data is randomly generated.

## Tests

Some tests has been prepared in `tests.py` and runned in `testing.ipynb`, those include:

| Test          | Description                                                                                                                                                                                                   |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stress Test 1 | The client makes the same request very quickly (10000 times).                                                                                                                                                 |
| Stress Test 2 | Two or more clients make the possible requests randomly (10000 times).                                                                                                                                        |
| Stress Test 3 | Immediate occupancy of all seats/reservations by 2 clients. Idea is we have one pool for reservation and 2 clients want to claim as much as possible. A situation where one client claims all is undesirable. |
| Stress Test 4 | Constant cancellations and seat occupancy. (For same seat 10000 times)                                                                                                                                        |
| Stress Test 5 | Update of 1000 reservations. (We change user_id of the reservation)                                                                                                                                           |

## Demo


https://github.com/wkzawadzka/library-cassandra/assets/49953771/9cc3be13-c125-46cd-8dc1-9373c4532959


