from parse_hh_data import download, parse
import json
import os

dirname = 'html_data'
if not os.path.exists(dirname):
    os.makedirs(dirname)

ids = download.resume_ids(
    area_id=113, #Russia https://github.com/hhru/api/blob/master/docs/areas.md
    specialization_id=1, #"Информационные технологии, интернет, телеком" https://api.hh.ru/specializations
    search_period=1, 
    num_pages=1,
    )

for id in ids:
    resume = download.resume(id)
    filepath = os.path.join(dirname, str(id) + '.html')
    with open(filepath, 'w',encoding = 'utf8') as fin:
        fin.write(str(resume))
        print(f'write file {filepath}')

'''

data = []
for id in ids[:5]:
    resume = download.resume(id)
    data.append(parse.resume(resume))


with open('resume.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, ensure_ascii=False)

import csv
keys = data[0].keys()
with open('resume.csv', 'w', newline='')  as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data)
'''

