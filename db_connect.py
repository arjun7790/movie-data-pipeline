import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    port=3306
)

cursor = conn.cursor()

with open("schema.sql", "r") as file:
    sql_script = file.read()

for statement in sql_script.split(";"):
    if statement.strip():
        cursor.execute(statement)

conn.commit()
conn.close()

print("Database tables created successfully")
