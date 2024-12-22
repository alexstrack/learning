# Import required libraries
import sqlite3
from sqlite3 import Error
from contextlib import contextmanager

# Define the database file name
DATABASE_NAME = "stores.sqlite"


def init_db():
    """Initialize the database with the required tables"""
    # SQL query to create the stores table with constraints
    create_stores_table = """
    CREATE TABLE IF NOT EXISTS stores (
        id TEXT PRIMARY KEY,                                    -- Unique identifier for each store
        name TEXT NOT NULL UNIQUE CHECK(length(name) <= 80)     -- Store name with max 80 chars
    );
    """

    # SQL query to create the items table with constraints
    create_items_table = """
    CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY,                                    -- Unique identifier for each item
        name TEXT NOT NULL CHECK(length(name) <= 50),          -- Item name with max 50 chars
        price REAL NOT NULL,                                   -- Price as float with 2 decimals
        store_id TEXT NOT NULL,                               -- Foreign key to stores table
        FOREIGN KEY (store_id) REFERENCES stores (id),        -- Establish relationship with stores
        UNIQUE(name, store_id)                                -- Prevent duplicate items in same store
    );
    """

    try:
        # Get database connection and create tables
        with get_db_connection() as conn:
            conn.execute(create_stores_table)
            conn.execute(create_items_table)
            conn.commit()
    except Error as e:
        print(f"Error initializing database: {e}")
        raise


@contextmanager
def get_db_connection():
    """Context manager for database connections to ensure proper handling"""
    conn = None
    try:
        # Create connection and set row factory for dictionary-like rows
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        # Ensure connection is closed even if an error occurs
        if conn:
            conn.close()
