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

        # Create HOLIDAYS table
        logger.info("Creating table HOLIDAYS...")
        cursor.execute("""
            CREATE TABLE holidays (
                id SERIAL PRIMARY KEY,
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


def add_holiday_DB(name, day, month, users, text):
    # Serialize the list of users to JSON format
    users_json = json.dumps(users, ensure_ascii=False)

    logger.info(f"Adding holiday '{name}' to HOLIDAYS table...")
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
            INSERT INTO holidays (name, day, month, users, text)
            VALUES (%s, %s, %s, %s, %s);
        """, (name, day, month, users_json, text))

        connection.commit()
        logger.info(f"Holiday '{name}' added successfully")

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


def remove_holiday_DB(holiday_id):
    """
    Remove a holiday from the HOLIDAYS table by its name.
    """
    logger.info(f"Removing holiday '{holiday_id}' from HOLIDAYS table...")
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logger.info("Database connection established for removing holiday.")

    try:
        cursor = connection.cursor()

        # Delete the holiday by name
        cursor.execute(f"""
            DELETE FROM holidays WHERE id = %s;
        """, (holiday_id,))

        connection.commit()
        logger.info(f"Holiday '{holiday_id}' removed successfully.")

    except Exception as e:
        # Handle specific errors
        if isinstance(e, errors.ForeignKeyViolation):
            logger.error(
                "ForeignKeyViolation: Cannot delete holiday due to dependent records.")
        else:
            logger.error(f"An error occurred: {e}")
        if connection:
            connection.rollback()  # Rollback transaction in case of an error
        raise e

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after removing holiday.")


def fetch_holidays_by_date_DB(dd_mm):
    """
    Fetch holidays for a specific date (dd-mm format) from the HOLIDAYS table.
    """
    day, month = map(int, dd_mm.split("-"))

    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logger.info(
        f"Database connection established for fetching holidays on {dd_mm}.")

    try:
        cursor = connection.cursor()

        # Query to fetch holidays matching the given day and month
        cursor.execute("""
            SELECT id, name, text, users
            FROM holidays
            WHERE day = %s AND month = %s;
        """, (day, month))

        # Fetch all matching rows
        rows = cursor.fetchall()

        holidays = []
        for row in rows:
            holiday_id, name, text, users = row

            # If 'users' is already a list (deserialized), no need to use json.loads
            if isinstance(users, str):
                # Deserialize only if it's a JSON string
                users = json.loads(users)

            holidays.append({
                'id': holiday_id,
                "name": name,
                "message": text,
                "greeted_users": users
            })

        logger.info(f"Fetched {len(holidays)} holidays for {dd_mm}.")
        return holidays

    except Exception as e:
        logger.error(
            f"An error occurred while fetching holidays for {dd_mm}: {e}")
        if connection:
            connection.rollback()
        return []

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after fetching holidays.")


def fetch_all_holidays_DB():
    """
    Fetch all holidays from the HOLIDAYS table.
    """
    connection = pg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE")
    )
    logger.info("Database connection established for fetching all holidays.")

    try:
        cursor = connection.cursor()

        # Query to fetch all holidays
        cursor.execute("""
            SELECT id, name, day, month, users, text
            FROM holidays;
        """)

        # Fetch all rows
        rows = cursor.fetchall()

        holidays = []
        for holiday_id, name, day, month, users, text in rows:
            # Deserialize 'users' JSON if needed
            users = json.loads(users) if isinstance(users, str) else users
            holidays.append({
                'id': holiday_id,
                "name": name,
                "day": day,
                "month": month,
                "greeted_users": users,
                "message": text
            })

        logger.info(f"Fetched {len(holidays)} holidays from the database.")
        return holidays

    except Exception as e:
        logger.error(f"An error occurred while fetching all holidays: {e}")
        if connection:
            connection.rollback()
        return []

    finally:
        cursor.close()
        connection.close()
        logger.info("Database connection closed after fetching all holidays.")
