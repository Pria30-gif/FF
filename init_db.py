import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MySQL configurations from environment variables
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),
    'auth_plugin': 'mysql_native_password'
}

def create_database_and_tables():
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create the database
        cursor.execute("CREATE DATABASE IF NOT EXISTS gym_trainer")
        print("Database 'gym_trainer' created successfully or already exists.")

        # Switch to the gym_trainer database
        cursor.execute("USE gym_trainer")

        # Table definitions
        tables = {
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(100) NOT NULL,
                    age INT,
                    weight DECIMAL(5,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'admins': """
                CREATE TABLE IF NOT EXISTS admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'exercise_plans': """
                CREATE TABLE IF NOT EXISTS exercise_plans (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    plan_type ENUM('Push', 'Pull', 'Legs', 'Cardio', 'Core', 'Full Body') NOT NULL,
                    exercises JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """,
            'diet_charts': """
                CREATE TABLE IF NOT EXISTS diet_charts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    diet_type ENUM('Weight Loss', 'Muscle Gain', 'Maintenance') NOT NULL,
                    diet_details TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """
        }

        # Create tables
        for table_name, table_query in tables.items():
            try:
                cursor.execute(table_query)
                print(f"Table '{table_name}' created successfully.")
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print(f"Table '{table_name}' already exists.")
                else:
                    print(f"Failed creating table '{table_name}': {err}")

        # Create default admin if not exists
        cursor.execute("""
            INSERT IGNORE INTO admins (username, email, password)
            VALUES ('Admin', 'admin@fitforge.com', 'admin123')
        """)
        print("Default admin created (if didn't exist).")

        # Commit changes
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("MySQL connection closed.")

if __name__ == "__main__":
    create_database_and_tables()