import pymysql

# Connect to the database
connection = pymysql.connect(
    host="localhost",          # Your database host (default is localhost)
    user="root",      # Your MySQL username
    password="root",  # Your MySQL password
    database="pro1",  # Your database name
    port=3306 
)

try:
    with connection.cursor() as cursor:
        # Execute a query
        cursor.execute("SELECT VERSION()")
        # Fetch the result
        result = cursor.fetchone()
        print("Database version:", result)
finally:
    connection.close()
