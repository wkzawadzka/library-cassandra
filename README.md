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

## Parameters

▪ N - The number of replicas 3
▪ W - The number of replicas that must respond to a write
operation in order to consider that operation a success - 2
▪ R - The number of replicas that must respond to a read
operation - 2

3/2/2 ratio was chosen as it is characterized by good durability and good R/W latency.
