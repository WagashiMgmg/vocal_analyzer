from dotenv import load_dotenv
import os
import json

load_dotenv()
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
main_table = os.getenv('MAIN_TABLE')

table_name = main_table

note_order = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
octave = ['1','2','3','4','5','6','7']
all_note  =['A0','A#0','B0']
for oc in octave:
    for note in note_order:
        all_note.append(note+oc)
all_note.append('C8')

col_name=[]
for i in range(len(all_note)):
   col_name.append('col'+str(i))

def create_sql_script(frequdic, notedic, filename):
    freq_json = json.dumps(frequdic)
    json_str = str(freq_json)
    new_dic = {}
    cols = f"(title,FREQ_TIME,"
    vals = f"('{filename}','{json_str}',"
    for key, value in notedic.items():
        #serch key in col_name
        index = all_note.index(key)
        new_key = col_name[index]
        new_dic[new_key] = value
        cols += new_key + ","
        vals += str(value) + ","
    cols = cols.rstrip(',') + ")"
    vals = vals.rstrip(',') + ")"

    script = f"INSERT INTO {table_name} {cols} VALUES {vals};"
    return script