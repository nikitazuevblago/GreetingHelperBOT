import psycopg2 as pg2
from psycopg2 import errors
import os
import json
from custom_logging import logger
from dotenv import load_dotenv

load_dotenv()


def create_tables_DB():
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )

    try:
        cursor = connection.cursor()

        # Create logs table
        cursor.execute("""
            CREATE TABLE logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                message TEXT NOT NULL
            );
        """)
        connection.commit()
        logger.info("Table logs created successfully.")

        # Create USERS table
        logger.info("Creating table USERS...")
        cursor.execute("""
            CREATE TABLE USERS (
                TELEGRAM_ID BIGINT UNIQUE,
                API_ID BIGINT,
                API_HASH TEXT
            );
        """)
        logger.info("Table USERS created successfully.")
        connection.commit()

        # Create HOLIDAYS table
        logger.info("Creating table HOLIDAYS...")
        cursor.execute("""
            CREATE TABLE holidays (
                TELEGRAM_ID BIGINT PRIMARY KEY,
                name TEXT NOT NULL,
                day INT NOT NULL CHECK (day BETWEEN 1 AND 31),
                month INT NOT NULL CHECK (month BETWEEN 1 AND 12),
                users JSONB,
                text TEXT NOT NULL
            );
        """)
        logger.info("Table HOLIDAYS created successfully.")
        connection.commit()

    except Exception as error:
        logger.error(f"An error occurred while creating tables: {error}")
        if connection:
            connection.rollback()

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after table creation.")


def drop_tables_DB():
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT tablename FROM pg_tables WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()

        for table_name, in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        connection.commit()

    except Exception as error:
        print(f"An error occurred while dropping tables: {error}")
        if connection:
            connection.rollback()
        

    finally:
        cursor.close()
        connection.close()


def add_user_DB(telegram_id, api_id, api_hash):
    logger.info(f"Adding user {telegram_id} to USERS table...")
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logger.info("Database connection established for adding user.")

    try:
        cursor = connection.cursor()
        cursor.execute(f"""
            INSERT INTO USERS (TELEGRAM_ID, API_ID, API_HASH)
            VALUES ({telegram_id}, {api_id}, '{api_hash}');
        """)
        connection.commit()
        logger.info(f"User {telegram_id} added successfully.")

    except Exception as e:
        # Handle specific errors first
        if isinstance(e, errors.UniqueViolation):
            logger.error("UniqueViolation: The user already exists.")
        else:
            # Handle all other exceptions
            logger.error(f"An error occurred: {e}")
        if connection:
            connection.rollback()  # Rollback transaction in case of an error

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after adding user.")


def add_holiday_DB(telegram_id, name, day, month, users, text):
    # Serialize the list of users to JSON format
    users_json = json.dumps(users, ensure_ascii=False)
    print(telegram_id, name, day, month, users_json, text)

    logger.info(f"Adding holiday '{name}' for Telegram user {telegram_id} to HOLIDAYS table...")
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logger.info("Database connection established for adding holiday.")

    try:
        cursor = connection.cursor()

        # Insert holiday into the table
        cursor.execute(f"""
            INSERT INTO holidays (TELEGRAM_ID, name, day, month, users, text)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (telegram_id, name, day, month, users_json, text))

        connection.commit()
        logger.info(f"Holiday '{name}' added successfully for Telegram user {telegram_id}.")

    except Exception as e:
        # Handle specific errors
        if isinstance(e, errors.UniqueViolation):
            logger.error("UniqueViolation: The holiday already exists.")
        else:
            logger.error(f"An error occurred: {e}")
        if connection:
            connection.rollback()  # Rollback transaction in case of an error
        raise e

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after adding holiday.")


# def remove_user_DB(telegram_id):
#     logger.info(f"Removing user {telegram_id} from USERS table...")
#     connection = pg2.connect(
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASSWORD"),
#         host=os.getenv("DB_HOST"),
#         port=os.getenv("DB_PORT"),
#         database=os.getenv("DB_DATABASE")
#     )
#     logger.info("Database connection established for removing user.")

#     try:
#         cursor = connection.cursor()
#         cursor.execute(f"""
#             DELETE FROM USERS
#             WHERE TELEGRAM_ID = {telegram_id};
#         """)
#         connection.commit()
#         logger.info(f"User {telegram_id} removed successfully.")

#     except Exception as e:
#         logger.error(f"An error occurred: {e}")
#         if connection:
#             connection.rollback()  # Rollback transaction in case of an error

#     finally:
#         cursor.close()
#         connection.close()
#         logger.info("Database connection closed after removing user.")


# def get_all_users_DB():
#     logger.info("Fetching all users from USERS table...")
#     connection = pg2.connect(
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASSWORD"),
#         host=os.getenv("DB_HOST"),
#         port=os.getenv("DB_PORT"),
#         database=os.getenv("DB_DATABASE")
#     )
#     logger.info("Database connection established for fetching users.")

#     try:
#         cursor = connection.cursor()
#         cursor.execute("SELECT * FROM USERS;")
#         records = cursor.fetchall()
#         logger.info(f"Fetched {len(records)} users.")
#         return records

#     except Exception as error:
#         logger.error(f"An error occurred while fetching users: {error}")
#         if connection:
#             connection.rollback()

#     finally:
#         cursor.close()
#         connection.close()
#         logger.info("Database connection closed after fetching users.")