# Import required libraries and modules
import uuid
import sqlite3
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import StoreSchema
from db import get_db_connection

# Create blueprint for store operations
blp = Blueprint("Stores", __name__, description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        """Get a single store by ID"""
        try:
            # Connect to database and execute SELECT query
            with get_db_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM stores WHERE id = ?",  # Query to find store by ID
                    (store_id,),  # Parameters to prevent SQL injection
                )
                store = cursor.fetchone()  # Get the store record

                # Return 404 if store not found
                if store is None:
                    abort(404, message="Store not found!")

                return dict(store)  # Return store data as dictionary
        except Exception as e:
            # Handle any database errors
            abort(500, message=str(e))

    def delete(self, store_id):
        """Delete a store by ID"""
        try:
            # Connect to database and execute DELETE query
            with get_db_connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM stores WHERE id = ?",  # Query to delete store
                    (store_id,),  # Parameters to prevent SQL injection
                )
                # Check if store was actually deleted
                if cursor.rowcount == 0:
                    abort(404, message="Store not found!")

                conn.commit()  # Commit the deletion
                return {"message": "Store deleted!"}
        except Exception as e:
            # Handle any database errors
            abort(500, message=str(e))


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        """Get all stores"""
        try:
            # Connect to database and get all stores
            with get_db_connection() as conn:
                cursor = conn.execute("SELECT * FROM stores")
                stores = [
                    dict(row) for row in cursor.fetchall()
                ]  # Convert all rows to dictionaries
                return stores
        except Exception as e:
            # Handle any database errors
            abort(500, message=str(e))

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        """Create a new store"""
        try:
            # Generate unique ID for new store
            store_id = uuid.uuid4().hex
            # Connect to database and insert new store
            with get_db_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO stores (id, name) VALUES (?, ?)",  # Insert query
                    (store_id, store_data["name"]),  # Store data with new ID
                )
                conn.commit()  # Commit the insertion

                # Fetch the newly created store
                cursor = conn.execute("SELECT * FROM stores WHERE id = ?", (store_id,))
                new_store = dict(cursor.fetchone())
                return new_store, 201  # Return new store with 201 status

        except sqlite3.IntegrityError:
            # Handle duplicate store name error
            abort(400, message="A store with that name already exists.")
        except Exception as e:
            # Handle any other database errors
            abort(500, message=str(e))
