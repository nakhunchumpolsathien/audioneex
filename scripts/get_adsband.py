from confidential import Confidential
from tqdm import tqdm
import os
import re
import pandas as pd
import codecs
import mariadb
from datetime import datetime, timedelta


def db_connection():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user=Confidential.iwads_username,
            password=Confidential.iwads_password,
            host=Confidential.iwads_host,
            port=Confidential.iwads_port,
            database=Confidential.iwads_db_name

        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        os.exit(1)
    return conn


def clean_text(text):
    text = text.replace('\n', '')
    text = text.replace("'", '')
    text = text.replace('"', '')
    text = text.replace('\t', '')
    text = text.replace('  ', ' ')
    text = text.replace(',', '')
    text = text.replace('...', '')
    return text

def if_empty_match(_list):
    if len(_list) < 1:
        return None
    else:
        return _list[0]


def get_brand_info(db_conn, afpid):
    cur = db_conn.cursor()
    cur.execute(Confidential.query_brand_command.format(afid=afpid))
    records = cur.fetchall()
    record = if_empty_match(records)

    if record is not None:
        return {'ads_brand': record[2], 'ads_title': clean_text(record[3]), 'ads_type': record[4]}
    else:
        return {'ads_brand': None, 'ads_title': None, 'ads_type': None}


def get_fid_file_name(fingerprint_log_file):
    ref = {}
    with codecs.open(fingerprint_log_file, encoding='utf-8') as f:
        for line in f:
            fid_ = re.findall('\[FID:(.*?)\]', line)
            filename = re.findall('\s\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\.mp3\s', line)

            if len(fid_) > 0:
                fid = fid_[0]
            else:
                continue

            if len(filename) > 0:
                filename_ = filename[0]
            ref[fid] = filename_.replace('.mp3', '')
    return ref


if __name__ == '__main__':
    ads_db = get_fid_file_name(Confidential.xscale_fingerprinting_log)
    log_file = Confidential.classify_log_path
    output_csv_path = Confidential.output_csv
    conn = db_connection()
    log = codecs.open(log_file, 'r', encoding='utf-8').read().strip()

    if os.path.isfile(output_csv_path):
        os.remove(output_csv_path)

    splitter = '=========================================================\n'
    raw_res = log.split(splitter)
    index = 0

    for result in tqdm(raw_res):
        if result == '' or 'Not eno' in result:
            continue

        file_name = if_empty_match(re.findall('(?<=Identifying\s)(.*)(?=\s\.\.\.)', result))
        if file_name is None:
            continue
        matched_fid = if_empty_match(re.findall('(?<=IDENTIFIED\s\sFID:\s)(.*)(?=\n)', result))
        matched_mp3 = ads_db.get(matched_fid)
        score = if_empty_match(re.findall('(?<=Score:\s)(.*)(?=,\sConf)', result))
        if float(score) < 50:
            continue
        confidence = if_empty_match(re.findall('(?<=,\sConf.:\s)(.*)(?=,\sId\.)', result))
        query_time = if_empty_match(re.findall('(?<=Id\.Time:\s)(.*)(?=s)', result))

        output_df = pd.DataFrame()
        output_df.loc[index, 'file_name'] = file_name
        output_df.loc[index, 'matched_fid'] = matched_fid
        output_df.loc[index, 'matched_mp3'] = matched_mp3
        output_df.loc[index, 'score'] = score
        output_df.loc[index, 'confidence'] = confidence
        output_df.loc[index, 'query_time'] = query_time

        brand_info = get_brand_info(conn, matched_mp3)
        output_df.loc[index, 'ads_brand'] = brand_info['ads_brand']
        output_df.loc[index, 'ads_title'] = brand_info['ads_title']
        output_df.loc[index, 'ads_type'] = brand_info['ads_type']

        if not os.path.isfile(output_csv_path):
            output_df.to_csv(output_csv_path, index=False, encoding='utf-8', header=output_df.columns)
        else:
            output_df.to_csv(output_csv_path, index=False, encoding='utf-8', mode='a', header=False)
        index = + 1

