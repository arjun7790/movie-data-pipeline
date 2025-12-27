#python db_connect.py
import pymysql

connector = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    port=3306
)

cursor = connector.cursor()
print("Connected successfully")

connector.close()
