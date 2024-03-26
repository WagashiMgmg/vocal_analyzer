import os
import numpy as np
import matplotlib.pyplot as plt
from vocal_extraction import Vocal_extracter
from SQL_script.SQL_check_music import check_bd
import scipy.io.wavfile as wav
from scipy.fftpack import fft
from scipy.signal import find_peaks
import logging
import json
from dotenv import load_dotenv
import time
import datetime
load_dotenv()
working_dir = os.getenv('WORK_DIR')

#with open('./log_config.json') as f:
#    log_conf = json.load(f)
#config.dictConfig(log_conf)
logging.basicConfig(filename='main_running.log', encoding='utf-8')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info('start running')

# 最小の音量
min_vol_rate = 0.05 #最大値*min_vol_rateより大きい音のみ取り出す。大きいほど条件がきつい. 0 <=min_vol_rate <=1

# 人間の声域の周波数範囲
min_freq = 90
max_freq = 1244.508 #D6#

# 区間
flagment = 0.17

# 音声ファイルのパス

def look_back(window_size, sample_rate, peaks, idx, largest, largestfreq, freq_range, th = 0.4, step = 1): #一つまえのピークが良い感じの高さだったらそれにする
    one_befor = peaks[idx - step]
    max_enel_index = one_befor + int(min_freq * window_size / sample_rate)
    max_enel_freq = max_enel_index * sample_rate / window_size
    max_enel = freq_range[one_befor]
    if max_enel > largest * th:
        logger.debug("step back!"+str(step))
        return max_enel_freq, max_enel,idx-step
    else:
        return largestfreq, largest,idx

def peak_finder(window_size, sample_rate, freq_range, maximum_vol):
    suspect_freq=880 #A5
    peaks, _ = find_peaks(freq_range, distance=50, prominence=10)
    if len(peaks) < 1: #peakが無いなら0
        return 0
    else:
        largest = 0
        largestfreq = 0
        for idx, peak in enumerate(peaks):
            max_enel_index = peak + int(min_freq * window_size / sample_rate)
            max_enel_freq = max_enel_index * sample_rate / window_size
            max_enel = freq_range[peak]
            if max_enel > largest:
                largest = max_enel
                largestfreq = max_enel_freq
                p_idx = idx
        if (len(peaks) > 3) and (p_idx == len(peaks)-1): #最後が選ばれていて、かつpeakが4つあったら二個前も見る
            largestfreq, largest, p_idx = look_back(window_size, sample_rate, peaks, p_idx, largest, largestfreq, freq_range, th=0.2, step=2)
        th = 0.15 #一個前のピークを選ぶ時の閾値
        if len(peaks) > 1:
            while (largestfreq > suspect_freq) and (p_idx >= 0):
                temp = largest
                largestfreq, largest, p_idx = look_back(window_size, sample_rate, peaks, p_idx, largest, largestfreq, freq_range, th=th)
                if largest==temp:
                    logger.debug("small peak is too small")
                    break
                th -= 0.05
        logger.debug([(p + int(min_freq * window_size / sample_rate)) * sample_rate / window_size for p in peaks])
        logger.debug(largestfreq)
        if ( len(freq_range) > 0 ) and ( largest > min_vol_rate * maximum_vol) : #閾値こえたら値を入れる
            return largestfreq
        else:
            return 0

# 周波数を音階に変換する関数
def freq_to_note(freq):
    if freq == 0:
        return 'Silence'
    notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    note_number = round(12 * np.log2(freq / 440) + 48)
    note_index = int(round(note_number) % 12) 
    octave = int((note_number + 9) // 12)
    return notes[note_index] + str(octave)

def main(path, VE):
    audio_file  = path #.flac .wav

    # ボーカル抽出
    logger.info("extract: start")
    vocal_file = VE.extract_vocals(audio_file, working_dir)
    logger.info("extract: done")
    # vocalパートの読み込み
    sample_rate, data = wav.read(vocal_file)
    # vocalパートの削除
    os.remove(vocal_file)
    music_length = data.shape[0]/sample_rate
    music_length = round(music_length, 3)
    # 既にある曲は処理しない
    music_already_in_db = check_bd(audio_file, music_length)
    logger.info(f"chcked as {music_already_in_db}")

    if music_already_in_db:
        logger.info("music is in already in database")
        return
    else:
        pass
    # flagment秒ごとに区切るためのパラメータ
    window_size = int(sample_rate * flagment)
    hop_size = window_size

    # 周波数と時間のリストを初期化
    frequencies = []
    times = []
    # 最大振幅を検出
    maximum_vol = 0
    for i in range(0, len(data) - window_size, hop_size):
        window = data[i:i+window_size]
        window = [(window[j][0]+window[j][1]) for j in range (len(window))]
        freq = fft(window)
        freq = np.abs(freq)[:window_size//2]
        freq_range = freq[int(min_freq * window_size / sample_rate):int(max_freq * window_size / sample_rate)]
        if len(freq_range) > 0:
            if np.max(freq_range) > maximum_vol:
                maximum_vol = np.max(freq_range)

    # flagment秒ごとに区切ってフーリエ変換
    for i in range(0, len(data) - window_size, hop_size):
        window = data[i:i+window_size]
        window = [(window[j][0]+window[j][1]) for j in range (len(window))]
        freq = fft(window)
        freq = np.abs(freq)[:window_size//2]
        freq_range = freq[int(min_freq * window_size / sample_rate)+1:int(max_freq * window_size / sample_rate)+1]
        result = peak_finder(window_size, sample_rate, freq_range, maximum_vol) #0か周波数を返す関数
        frequencies.append(result)
        times.append(i / sample_rate)

    """
    # 時間と周波数のグラフを作成
    plt.figure(figsize=(12, 6))
    plt.plot(times, frequencies)
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title('Frequency over Time')
    plt.savefig("./freqs.png")
    plt.show()
    """

    # 周波数を音階に変換
    notes = [freq_to_note(freq) for freq in frequencies]

    # freq-time, note-timeをjsonに変換
    freq_time={}
    freq_time["time"] = times
    freq_time["freq"] = frequencies

    note_time={}
    note_time["time"] = times
    note_time["note"] = notes

    # 音階の存在時間を計算
    note_durations = {}
    current_note = notes[0]
    start_time = times[0]

    for i in range(1, len(notes)):
        if notes[i] != current_note:
            duration = times[i] - start_time
            if current_note in note_durations:
                note_durations[current_note] += duration
            else:
                note_durations[current_note] = duration
            start_time = times[i]
        current_note = notes[i]

    #最後の音階の処理
    duration = times[-1] - start_time
    if current_note in note_durations:
        note_durations[current_note] += duration
    else:
        note_durations[current_note] = duration

    from collections import OrderedDict
    # 音階の順序を定義
    note_order = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # 'Silence'を除外し、数字が含まれるキーのみを抽出して音階と数字に分割
    keys_split = [(key[:-1], int(key[-1])) for key in note_durations.keys() if key != 'Silence' and key[-1].isdigit()]

    # 音階と数字でソート
    sorted_keys = sorted(keys_split, key=lambda x: (x[1], note_order.index(x[0])))

    # ソートされたキーを文字列に戻す
    sorted_keys_str = [note + str(octave) for note, octave in sorted_keys]

    # 新しい順序付き辞書を作成
    new_dict = OrderedDict()
    for key in sorted_keys_str:
        new_dict[key] = note_durations[key]

    #with open(os.path.join(working_dir,os.path.splitext(os.path.basename(audio_file))[0],"note.json"), "w") as fp:
    #    json.dump(new_dict, fp, indent=2)

    from SQL_script.SQL_insert_music import insert_music_db
    message = insert_music_db(music_length, freq_time, note_time, new_dict, os.path.splitext(os.path.basename(audio_file))[0])
    logger.info(f"message from insert function: {message}")

    """
    #音階の存在時間のヒストグラムを作成
    plt.figure(figsize=(12, 6))
    plt.bar(new_dict.keys(), new_dict.values())
    plt.xlabel('Note')
    plt.ylabel('Duration (s)')
    plt.title('Note Durations')
    plt.xticks(rotation=45)
    plt.savefig("./note.png")
    """
def search_files(directory, extensions):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(tuple(extensions)):
                file_list.append(os.path.join(root, file))
    return file_list

if __name__ == "__main__":
    music_dir = os.getenv('MUSIC_DIR')
    extensions = ['.wav', '.flac', 'mp3']
    music_files = search_files(music_dir, extensions)
    num_music_files = len(music_files)
    logger.info(f"Music file: {num_music_files} files")
    VE = Vocal_extracter()
    processed = 0
    start = time.time()
    for music in music_files:
        main(music,VE)
        processed+=1
        progress = processed/num_music_files * 100
        logger.info(f"processed {progress}%. ({processed}/{num_music_files})")
        now = time.time()
        logger.info(f"spend {now-start}")
        finish = now + (now-start)/processed * (num_music_files - processed)
        dt = datetime.datetime.fromtimestamp(finish)
        logger.info(f"finish time estimated at {dt}")
    logger.info('finish running')