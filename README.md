authors: Weronika Zawadzka & Eliza Czaplicka

Final project for **Big data and distributed processing** class at Poznan Univerity of Technology.

# Cassandra Library Reservation System

This project is a distributed library reservation system using Apache Cassandra. It supports creating, updating, viewing, and canceling reservations, and includes stress tests to evaluate system performance under load.

## Prerequisites

- Python 3.6+
- Apache Cassandra 3.11+
- `cassandra-driver` Python package

### Step 1: Create a docker network & run clusters

Run `docker-compose up -d`

Wait a minute or two after this command :)

### Step 2: Create tables and populate books

Run `python setup.py`

### Step 3: Start app

Run `uvicorn api:app --reload`

Then in another terminal: `npm start`
