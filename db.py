import mysql.connector

# MySQL configurations
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'priyamysql@30'  # Replace with your MySQL password
}

# Function to create the database and tables
def create_database_and_tables():
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create the database
        cursor.execute("CREATE DATABASE IF NOT EXISTS gym_trainer")
        print("Database 'gym_trainer' created successfully.")

        # Switch to the gym_trainer database
        cursor.execute("USE gym_trainer")

        # Create the 'users' table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(100) NOT NULL
            )
        """)
        print("Table 'users' created successfully.")

        # Create the 'exercise_plans' table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise_plans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                plan_type ENUM('Push', 'Pull', 'Legs') NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("Table 'exercise_plans' created successfully.")

        # Create the 'diet_charts' table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diet_charts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                diet_type ENUM('Weight Loss', 'Muscle Gain', 'Maintenance') NOT NULL,
                diet_details TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("Table 'diet_charts' created successfully.")

        # Commit changes
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("MySQL connection closed.")

# Run the function
create_database_and_tables()