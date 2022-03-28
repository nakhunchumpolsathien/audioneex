from tqdm import tqdm
import os
import pandas as pd
from datetime import datetime
from confidential import Confidential


def delete_date(date):
    return date.strftime('%H:%M:%S')


def get_time(file_name):
    names = file_name.replace('.mp3', '').split('_')
    start = names[0]
    end = names[1]
    return {'start_time': datetime.strptime(start, "%Y%m%dT%H%M%S"),
            'end_time': datetime.strptime(end, "%Y%m%dT%H%M%S")}


if __name__ == '__main__':
    score_csv_path = Confidential.score_csv
    output_csv_path = Confidential.output_csv
    score_df = pd.read_csv(score_csv_path, encoding='utf-8')
    score_df = score_df.sort_values(by='file_name', ascending=True).reset_index(drop=True)
    score_threshold = 200
    conf_threshold = 0.8
    mode = 'internet'

    if mode == 'internet':
        score_threshold = 200
        conf_threshold = 0.80
    elif mode == 'radio':
        score_threshold = 250
        conf_threshold = 0.85

    res = []
    score_df_len = len(score_df)
    precessed_rows = []
    for index, row in score_df.iterrows():
        current_afid = row['matched_fid']
        current_times = get_time(row['file_name'])

        if index == 0:
            previous_afid = None
        else:
            previous_afid = score_df.iloc[index - 1]['matched_fid']

        if index + 1 < score_df_len:
            next_afid = score_df.iloc[index + 1]['matched_fid']
        else:
            next_afid = None

        if index in precessed_rows:
            continue

        if (current_afid != next_afid) and (current_afid != previous_afid):
            if (row['score'] >= score_threshold) and (row['confidence'] >= conf_threshold):
                ads_info = {'start': current_times['start_time'], 'end': current_times['end_time'],
                            'ads_brand': row['ads_brand'], 'ads_description': row['ads_title'],
                            'ads_type': row['ads_type'], 'afpid': row['matched_mp3'],
                            'score': row['score'], 'confidence': row['confidence'],
                            'matched_time': row['query_time']}
                res.append(ads_info)
                # print(f'score: {row["score"]}, confi: {row["confidence"]}', row["query_time"])
                print(f"{current_times['start_time']} → {current_times['end_time']} → {row['ads_brand']}")
                precessed_rows.append(index)
                continue
            else:
                continue
        # else:
        #     continue

        if current_afid == next_afid:
            is_repeated = True
            start = current_times['start_time']
            current_index = index
            next_index = current_index + 1
            ads_brand = row['ads_brand']

            while is_repeated:
                if (get_time(score_df.iloc[current_index]['file_name'])['end_time']
                    - get_time(score_df.iloc[next_index]['file_name'])['start_time']).seconds > 15:
                    is_repeated = False
                    final_end_time = get_time(score_df.iloc[current_index]['file_name'])['end_time']

                if is_repeated is not False:
                    precessed_rows.append(next_index)
                    final_end_time = get_time(score_df.iloc[next_index]['file_name'])['end_time']
                    next_index = next_index + 1
                    current_index = current_index + 1

                    if not score_df.iloc[current_index]['matched_fid'] == score_df.iloc[next_index]['matched_fid']:
                        is_repeated = False

            ads_info = {'start': current_times['start_time'], 'end': current_times['end_time'],
                        'ads_brand': row['ads_brand'], 'ads_description': row['ads_title'],
                        'ads_type': row['ads_type'], 'afpid': row['matched_mp3'],
                        'score': row['score'], 'confidence': row['confidence'],
                        'matched_time': row['query_time']}
            res.append(ads_info)
            print(f'{start} → {final_end_time} → {row["ads_brand"]}')

    if os.path.isfile(output_csv_path):
        os.remove(output_csv_path)
    out_index = 0

    for match in tqdm(res):

        output_df = pd.DataFrame()
        output_df.loc[out_index, 'start'] = delete_date(match['start'])
        output_df.loc[out_index, 'end'] = delete_date(match['end'])
        output_df.loc[out_index, 'ads_brand'] = match['ads_brand']
        output_df.loc[out_index, 'score'] = round(match['score'], 3)
        output_df.loc[out_index, 'confidence'] = round(match['confidence'], 3)
        output_df.loc[out_index, 'matched_time'] = round(match['matched_time'], 1)
        output_df.loc[out_index, 'ads_description'] = match['ads_description'].replace(',', '') \
            .replace('\n', '').strip().replace('\r', '')
        output_df.loc[out_index, 'ads_type'] = match['ads_type']

        if not os.path.isfile(output_csv_path):
            output_df.to_csv(output_csv_path, index=False, encoding='utf-8', header=output_df.columns)
        else:
            output_df.to_csv(output_csv_path, index=False, encoding='utf-8', mode='a', header=False)

        out_index = out_index + 1
