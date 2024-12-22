# Import required libraries and modules
import uuid
import sqlite3
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import ItemSchema, ItemUpdateSchema
from db import get_db_connection

# Create blueprint for item operations
blp = Blueprint("Items", __name__, description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        """Get a single item by ID"""
        try:
            # Connect to database and execute SELECT query
            with get_db_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM items WHERE id = ?",  # Query to find item by ID
                    (item_id,),  # Parameters to prevent SQL injection
                )
                item = cursor.fetchone()  # Get the item record

                # Return 404 if item not found
                if item is None:
                    abort(404, message="Item not found!")

                return dict(item)  # Return item data as dictionary
        except Exception as e:
            # Handle any database errors
            abort(500, message=str(e))

    def delete(self, item_id):
        """Delete an item by ID"""
        try:
            # Connect to database and execute DELETE query
            with get_db_connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM items WHERE id = ?",  # Query to delete item
                    (item_id,),  # Parameters to prevent SQL injection
                )
                # Check if item was actually deleted
                if cursor.rowcount == 0:
                    abort(404, message="Item not found!")

                conn.commit()  # Commit the deletion
                return {"message": "Item deleted."}
        except Exception as e:
            # Handle any database errors
            abort(500, message=str(e))

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        """Update an item by ID"""
        try:
            # Connect to database and perform update
            with get_db_connection() as conn:
                # First check if item exists
                cursor = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
                if cursor.fetchone() is None:
                    abort(404, message="Item not found!")

                # Update the item with new data
                update_query = """
                    UPDATE items 
                    SET name = ?, price = ?
                    WHERE id = ?
                """
                conn.execute(
                    update_query, (item_data["name"], item_data["price"], item_id)
                )
                conn.commit()  # Commit the update

                # Return the updated item
                cursor = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
                return dict(cursor.fetchone())
        except sqlite3.IntegrityError:
            # Handle duplicate item name error
            abort(400, message="An item with that name already exists in this store.")
        except Exception as e:
            # Handle any other database errors
            abort(500, message=str(e))


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        """Get all items"""
        try:
            # Connect to database and get all items
            with get_db_connection() as conn:
                cursor = conn.execute("SELECT * FROM items")
                items = [
                    dict(row) for row in cursor.fetchall()
                ]  # Convert all rows to dictionaries
                return items
        except Exception as e:
            # Handle any database errors
            abort(500, message=str(e))

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        """Create a new item"""
        try:
            # Generate unique ID for new item
            item_id = uuid.uuid4().hex
            # Connect to database and insert new item
            with get_db_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO items (id, name, price, store_id)
                    VALUES (?, ?, ?, ?)
                    """,  # Insert query
                    (
                        item_id,
                        item_data["name"],  # Item data with new ID
                        item_data["price"],
                        item_data["store_id"],
                    ),
                )
                conn.commit()  # Commit the insertion

                # Fetch the newly created item
                cursor = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
                new_item = dict(cursor.fetchone())
                return new_item, 201  # Return new item with 201 status

        except sqlite3.IntegrityError as e:
            # Handle foreign key and unique constraint violations
            if "FOREIGN KEY" in str(e):
                abort(404, message="Store not found.")
            abort(400, message="An item with that name already exists in this store.")
        except Exception as e:
            # Handle any other database errors
            abort(500, message=str(e))
