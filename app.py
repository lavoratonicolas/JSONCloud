from flask import Flask, request, jsonify
from psycopg2 import connect, errors, extras
from flask_bcrypt import Bcrypt

from dotenv import load_dotenv
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)

load_dotenv()

host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")


def get_connection():
    try:
        return connect(
            host=host, port=port, dbname=dbname, user=user, password=password
        )
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None


@app.get("/")
def home():
    db_connection = get_connection()
    cursor = db_connection.cursor()

    cursor.execute("Select 1+1")
    result = cursor.fetchone()

    print(result)
    return "Hello word"


@app.get("/api/users")
def get_users():

    db_connection = get_connection()

    if db_connection is None:
        return {
            "success": False,
            "message": "An internal error has occurred, try again later",
        }, 500
    try:
        cursor = db_connection.cursor(cursor_factory=extras.RealDictCursor)

        cursor.execute(
            """
            SELECT id, username, email
            FROM users
            """
        )

        users = cursor.fetchall()

        return (
            jsonify(
                {
                    "success": True,
                    "message": users,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Unexpected error when retrieving users: {e}")
        return {
            "success": False,
            "message": "Unexpected error when retrieving users",
        }, 500

    finally:
        cursor.close()
        db_connection.close()


@app.post("/api/users")
def create_user():

    new_user = request.get_json()
    username = new_user["username"]
    email = new_user["email"]
    password = new_user["password"]
    password_bytes = password.encode("utf-8")

    hashed_password = bcrypt.generate_password_hash(password_bytes, rounds=12).decode(
        "utf-8"
    )

    # Valido contraseña para el login
    # print(bcrypt.check_password_hash(hashed_password, b"nicopass"))

    db_connection = get_connection()

    if db_connection is None:
        return {
            "success": False,
            "message": "An internal error has occurred, try again later",
        }, 500

    try:
        cursor = db_connection.cursor(cursor_factory=extras.RealDictCursor)

        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, username, email
            """,
            (
                username,
                email,
                hashed_password,
            ),
        )

        new_created_user = cursor.fetchone()
        db_connection.commit()

        # cursor.execute("truncate table users restart IDENTITY")
        # db_connection.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "User successfully created",
                    "user_data": new_created_user,
                }
            ),
            201,
        )

    except errors.UniqueViolation as e:
        if "users_username_key" in str(e):
            return {
                "success": False,
                "message": "The username is already registered, please use a different one",
            }, 409
        elif "users_email_key" in str(e):
            return {
                "success": False,
                "message": "The email is already registered, please use a different one",
            }, 409
        else:
            return {
                "success": False,
                "message": "Username and/or password already registered, please use different information",
            }, 409

    except Exception as e:
        print(f"Unexpected error when trying to create the user: {e}")
        return {
            "success": False,
            "message": "Unexpected error when trying to create the user",
        }, 500

    finally:
        cursor.close()
        db_connection.close()


@app.delete("/api/users/<id>")
def delete_user(id):

    db_connection = get_connection()

    if db_connection is None:
        return {
            "success": False,
            "message": "An internal error has occurred, try again later",
        }, 500
    try:
        cursor = db_connection.cursor(cursor_factory=extras.RealDictCursor)

        cursor.execute(
            """
            DELETE
            FROM users
            WHERE id = %s
            RETURNING id, username, email
            """,
            (id,),
        )

        users = cursor.fetchone()
        db_connection.commit()

        if users is None:
            return jsonify({"success": False, "message": "User not found"}), 404
        else:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": users,
                    }
                ),
                200,
            )

    except Exception as e:
        print(f"Unexpected error when retrieving users: {e}")
        return {
            "success": False,
            "message": "Unexpected error when deleting user",
        }, 500

    finally:
        cursor.close()
        db_connection.close()


@app.put("/api/users/<id>")
def update_user(id):

    new_user = request.get_json()
    username = new_user["username"]
    email = new_user["email"]
    password = new_user["password"]
    password_bytes = password.encode("utf-8")

    hashed_password = bcrypt.generate_password_hash(password_bytes, rounds=12).decode(
        "utf-8"
    )

    # Valido contraseña para el login
    # print(bcrypt.check_password_hash(hashed_password, b"nicopass"))

    db_connection = get_connection()

    if db_connection is None:
        return {
            "success": False,
            "message": "An internal error has occurred, try again later",
        }, 500

    try:
        cursor = db_connection.cursor(cursor_factory=extras.RealDictCursor)

        cursor.execute(
            """
            UPDATE users
            SET username = %s, email = %s, password_hash = %s
            WHERE id = %s
            RETURNING id, username, email
            """,
            (
                username,
                email,
                hashed_password,
                id,
            ),
        )

        updated_user = cursor.fetchone()
        db_connection.commit()

        if updated_user is None:
            return jsonify({"success": False, "message": "User not found"}), 404
        else:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "User successfully updated",
                        "user_data": updated_user,
                    }
                ),
                201,
            )

    except errors.UniqueViolation as e:
        if "users_username_key" in str(e):
            return {
                "success": False,
                "message": "The username is already exists, please use a different one",
            }, 409
        elif "users_email_key" in str(e):
            return {
                "success": False,
                "message": "The email is already exists, please use a different one",
            }, 409
        else:
            return {
                "success": False,
                "message": "Username and/or password already exists, please use different information",
            }, 409

    except Exception as e:
        print(f"Unexpected error when trying to update the user: {e}")
        return {
            "success": False,
            "message": "Unexpected error when trying to update the user",
        }, 500

    finally:
        cursor.close()
        db_connection.close()


@app.get("/api/users/<id>")
def get_user(id):

    db_connection = get_connection()

    if db_connection is None:
        return {
            "success": False,
            "message": "An internal error has occurred, try again later",
        }, 500
    try:
        cursor = db_connection.cursor(cursor_factory=extras.RealDictCursor)

        cursor.execute(
            """
            SELECT id, username, email
            FROM users
            WHERE id = %s
            """,
            (id,),
        )

        users = cursor.fetchone()

        if users is None:
            return jsonify({"success": False, "message": "User not found"}), 404
        else:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": users,
                    }
                ),
                200,
            )

    except Exception as e:
        print(f"Unexpected error when retrieving users: {e}")
        return {
            "success": False,
            "message": "Unexpected error when retrieving user",
        }, 500

    finally:
        cursor.close()
        db_connection.close()


if __name__ == "__main__":
    app.run(debug=True)
