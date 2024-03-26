from dotenv import load_dotenv
import os
import mysql.connector
import logging
logging.basicConfig(filename='main_running.log', encoding='utf-8')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

def run_sql(sql_lang) -> int:
    """Returns 0 or 1.
    there is no row affected by the sql_lang: 0
    there is at least 1 row affected : 1
    """
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
    # 結果セットがある場合は読み込む
    try:
        result = cursor.fetchall()
    except mysql.connector.errors.InternalError:
        pass
    cnx.commit()
    affected_rows = cursor.rowcount
    logger.info(f"affected rows: {affected_rows}")

    cursor.close()
    cnx.close()

    return affected_rows > 0

