import os
import shutil
from tqdm import tqdm
from glob import glob
from confidential import Confidential

if __name__ == '__main__':
    audios_dir = Confidential.fm_archive_dir
    channel = str(Confidential.channel_id)
    save_local_dir = Confidential.local_archive_dir
    files = glob(os.path.join(audios_dir, f'*-{channel}.mp3'))

    if not os.path.isdir(save_local_dir):
        os.mkdir(save_local_dir)

    for file in tqdm(files):
        save_path = os.path.join(save_local_dir, os.path.basename(file))
        shutil.copyfile(file, save_path)
