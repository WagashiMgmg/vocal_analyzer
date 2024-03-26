from dotenv import load_dotenv
import os
import json
import re
from executeSQL import run_sql

def sanitize_filename(filename): # ' -> ''
    return re.sub(r"'", r"''", filename)
load_dotenv()

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

def insert_music_db(music_length,frequdic, note_time, notedic, filename):
    filename = sanitize_filename(filename)
    freq_json = json.dumps(frequdic)
    json_str = str(freq_json)
    note_json = str(json.dumps(note_time))
    new_dic = {}
    cols = f"(title,music_length,FREQ_TIME,NOTE_TIME,"
    vals = f"('{filename}',{music_length},'{json_str}','{note_json}',"
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
    try:
        run_sql(script)
    except Exception as e:
        return "error when INSERT"
    else:
        return