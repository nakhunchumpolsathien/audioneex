# Use this script in POC production scale

import os
import codecs
import subprocess
from tqdm import tqdm
from glob import glob


def get_number_of_file_in_dir(directory):
    mp3s = glob(f'{directory}/*.mp3')
    return len(mp3s)


if __name__ == '__main__':
    mini_mp3_dir = '/home/poctest/Documents/data/miniADsMp3'
    database_dir = '/home/poctest/nakhun/miniADsDB'
    program = '/home/poctest/nakhun/audioneex/_build/linux-x64-gnu940/release/example1'
    log_path = '/home/poctest/nakhun/miniADsDB/fingerprint_log.txt'
    # mp3_dirs = [os.path.normpath(f.path) for f in os.scandir(mini_mp3_dir) if f.is_dir()]
    number_of_files = 0
    dir_index = 0
    lasted_id = 0

    for dir in tqdm(range(187, -1, -1)):
        current_dir = os.path.join(mini_mp3_dir, str(dir))
        current_dir = os.path.normpath(current_dir)

        if dir_index == 0:
            f = 0
        else:
            f = lasted_id

        number_of_files = get_number_of_file_in_dir(current_dir)
        cmd = [program, "-u", database_dir, "-m", "MSCALE", "-f", str(lasted_id), current_dir]
        results = subprocess.run(cmd, capture_output=True, text=True).stdout

        codecs.open(log_path, "a", encoding="utf-8").write(results)
        lasted_id = lasted_id + number_of_files
        dir_index = dir_index + 1

        if "Invalid FID have been assigned" in str(results):
            raise Exception('Invalid FID Error')
