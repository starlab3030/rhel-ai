from sqlalchemy import create_engine, text
from tabulate import tabulate

import config


def run_query(query):
    engine = create_engine(config.DB_CONN_STRING)
    with engine.connect() as connection:
        result = connection.execute(text(query))
        return tabulate(tabular_data=result.fetchall(), headers=result.keys(), tablefmt='grid')


def get_db_tables_schema():
    return """
CREATE TABLE Movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    year INT
);

CREATE TABLE Actors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    salary NUMERIC(10, 2)
);

CREATE TABLE Movies_Actors (
    movie_id INT REFERENCES Movies(id) ON DELETE CASCADE,
    actor_id INT REFERENCES Actors(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, actor_id)
);
"""