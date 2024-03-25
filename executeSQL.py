from dotenv import load_dotenv
import os
import mysql.connector
from SQL_script.SQL_insert_music import create_sql_script
import logging
logging.basicConfig(filename='main_running.log', encoding='utf-8')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

def run_sql(music_length, frequdic, note_time, notedic, filename):
    sql_lang = create_sql_script(music_length, frequdic, note_time, notedic, filename)
    logger.debug(sql_lang)
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

