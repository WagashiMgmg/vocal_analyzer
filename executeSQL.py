from dotenv import load_dotenv
import os
import mysql.connector
from SQL_script.SQL_insert_music import create_sql_script

load_dotenv()
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

def run_sql(frequdic, notedic, filename):
    sql_lang = create_sql_script(frequdic, notedic, filename)
    print(sql_lang)
    config ={
        'user': db_user,
        'password': db_pass,
        'host': db_host,
        'database': db_name,
    }

    cnx = mysql.connector.connect(**config)

    cursor = cnx.cursor()

    cursor.execute(sql_lang)
    cnx.commit()

    cursor.close()
    cnx.close()

