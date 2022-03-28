# Use this script in POC production scale

import os
import codecs
import subprocess
from tqdm import tqdm
from confidential import Confidential


if __name__ == '__main__':
    database_dir = Confidential.xscale_db
    test_audio_dir = Confidential.split_overlap_dir
    classify_log = Confidential.classify_log_path
    program = Confidential.classifier
    hour_dirs = [os.path.normpath(f.path) for f in os.scandir(test_audio_dir) if f.is_dir()]

    # os.chdir(Confidential.classifier)

    for hour_dir in tqdm(hour_dirs, desc=f"FUZZY EASY XSCALE"):
        cmd = [program, "-u", database_dir, '-m', 'XSCALE', '-i', 'FUZZY', '-d', 'EASY', '-s', '0', hour_dir]
        results = subprocess.run(cmd, capture_output=True, text=True).stdout
        codecs.open(classify_log, 'a', encoding='utf-8').write(results)


