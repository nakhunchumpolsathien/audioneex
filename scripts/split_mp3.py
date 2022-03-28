import os
from glob import glob
from tqdm import tqdm
from pydub import AudioSegment
from confidential import Confidential
from datetime import timedelta, datetime


def check_if_dir_not_exist(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)


def get_frame_date(date, milisec):
    frame_date = date + timedelta(milliseconds=milisec)
    frame_date = frame_date.strftime("%Y%m%dT%H%M%S")
    return frame_date


def sec_to_milsec(sec):
    milsec = sec * 1000
    return milsec


if __name__ == '__main__':
    audio_dir = Confidential.audios_24_hour_dir
    output_dir = Confidential.output_dir

    overlap = sec_to_milsec(5)
    chunk_length = sec_to_milsec(10)

    audios = glob(f'{audio_dir}/*.mp3')
    file_index = 1

    for audio_path in audios:
        audio = AudioSegment.from_mp3(audio_path)
        aired_date = os.path.basename(audio_path)[:10]
        sub_dir = os.path.join(output_dir, aired_date[8:10])
        check_if_dir_not_exist(sub_dir)
        aired_date = datetime(int(aired_date[:4]), int(aired_date[4:6]), int(aired_date[6:8]),
                              int(aired_date[8:10]))

        start = 0
        end = chunk_length
        audio_length = int(sec_to_milsec(audio.duration_seconds))
        number_of_files = range(int(audio_length / (chunk_length - overlap)))

        for frame in tqdm(number_of_files):
            if frame != number_of_files[-1]:
                frame = audio[start:end]
                file_name = f"{get_frame_date(aired_date, start)}_{get_frame_date(aired_date, end)}.mp3"
                output_path = os.path.join(sub_dir, file_name)
                frame.export(output_path, format="mp3")

                start = end - overlap
                end = start + chunk_length

            else:
                end = audio_length
                frame = audio[start:end]
                file_name = f"{get_frame_date(aired_date, start)}_{get_frame_date(aired_date, end)}.mp3"
                output_path = os.path.join(sub_dir, file_name)
                frame.export(output_path, format="mp3")

            file_index = file_index + 1

