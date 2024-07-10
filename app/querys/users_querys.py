get_users_query = """
            SELECT id, username, email
            FROM users
            """

create_user_query = """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, username, email
            """

delete_user_query = """
            DELETE
            FROM users
            WHERE id = %s
            RETURNING id, username, email
            """

update_user_query = """
            UPDATE users
            SET username = %s, email = %s, password_hash = %s
            WHERE id = %s
            RETURNING id, username, email
            """

get_user_query = """
            SELECT id, username, email
            FROM users
            WHERE id = %s
            """
