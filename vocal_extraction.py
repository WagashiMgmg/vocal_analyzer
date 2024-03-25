import os
from spleeter.separator import Separator
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

separator = Separator('spleeter:2stems')
class Vocal_extracter:
    def __init__(self) -> None:
        self.separator = Separator('spleeter:2stems')

    def extract_vocals(self, audio_file, working_dir):
        # 出力ファイルのパスを生成
        output_path = working_dir
        os.makedirs(output_path, exist_ok=True)
        audio_name = os.path.splitext(os.path.basename(audio_file))[0]
        vocal_file = os.path.join(output_path, audio_name, 'vocals.wav')

        # 2ステムモデル（ボーカルとその他の楽器）を使用
        print(audio_file)

        # 音声ファイルを分離
        print(audio_file)
        self.separator.separate_to_file(audio_file, output_path)
        os.remove(os.path.join(output_path, audio_name, 'accompaniment.wav')) #vocal以外パートの削除

        #BPFの適用
        #bpf_file   = os.path.join(output_path, audio_name, 'vocals_bpf.wav')
        #BPF_for_vocal(vocal_file, bpf_file)
        #return bpf_file
        return vocal_file

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def BPF_for_vocal(input_file, output_file):

    # 低域と高域のカットオフ周波数を指定（Hz）
    lowcut = 85.0
    highcut = 1100.0

    # 入力ファイルを読み込む
    fs, data = wavfile.read(input_file)

    # ステレオの場合は、左右のチャンネルを別々に処理
    if len(data.shape) > 1:
        left_channel = data[:, 0]
        right_channel = data[:, 1]
    
        filtered_left = butter_bandpass_filter(left_channel, lowcut, highcut, fs, order=5)
        filtered_right = butter_bandpass_filter(right_channel, lowcut, highcut, fs, order=5)
        
        filtered_data = np.column_stack((filtered_left, filtered_right))
    else:
        filtered_data = butter_bandpass_filter(data, lowcut, highcut, fs, order=5)

    # 出力ファイルに書き込む
    wavfile.write(output_file, fs, filtered_data.astype(np.int16))
    return output_file

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    working_dir = os.getenv('WORK_DIR')
    path = "/home/tkusumoto/music/music/0/STEINS_GATE_0_Original_Soundtrack_-_Gate_Of_Steiner_[FLAC]/[ASL] Abo Takeshi - STEINS;GATE 0 Original Soundtrack - Gate Of Steiner [FLAC] [w Scans]/02 Messenger -main theme-.flac"
    VE = Vocal_extracter()

    result = VE.extract_vocals(path, working_dir)
    print(result)