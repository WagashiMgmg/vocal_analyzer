#SELECT 1
#FROM table_name
#WHERE colA = 'ABCDE' AND colB = 343434
#LIMIT 1

import os
from dotenv import load_dotenv
from executeSQL import run_sql
import re
import logging
logging.basicConfig(filename='main_running.log', encoding='utf-8')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def sanitize_filename(filename): # ' -> ''
    return re.sub(r"'", r"''", filename)


load_dotenv()
main_table = os.getenv('MAIN_TABLE')

table_name = main_table
def check_bd(audio_file, music_length):
    title = os.path.splitext(os.path.basename(audio_file))[0]
    title = sanitize_filename(title)
    script = f"SELECT 1 FROM {table_name} WHERE title = '{title}' AND music_length = {music_length} LIMIT 1;"
    logger.info(script)
    check_result = run_sql(script)
    logger.info(f"CHECK SQL result: {check_result}")
    return check_result