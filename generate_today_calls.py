
import mysql.connector
from datetime import datetime

host = "localhost"
user = "..."
password = "..."
database = "..."

# Create a connection
connection = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

cursor = connection.cursor()

# Get today's date
today = datetime.today().date()

frequent_query = f"SELECT personne, numero FROM frequent_calls WHERE date = '{today}'"
ponctual_query = f"SELECT personne, numero, raison FROM ponctual_calls WHERE date = '{today}'"

cursor.execute(frequent_query)
# Fetch rows from the frequent_calls table
rows = []
for row in cursor.fetchall():
    rows += [[e for e in row] + ["Prendre des nouvelles"]]

cursor.execute(ponctual_query)
# Fetch rows from the ponctual_calls table
for row in cursor.fetchall():
    rows.append([e for e in row])
    
    
delete_query = "DELETE FROM today_calls WHERE was_called = 'OUI'"
cursor.execute(delete_query)
connection.commit()  # Commit the transaction
    
insert_query = "INSERT INTO today_calls (personne, numero, raison, was_called) VALUES (%s, %s, %s, 'NON')"
for row in rows:
    cursor.execute(insert_query, row)
    connection.commit()  # Commit after each insertion

cursor.close()
connection.close()

