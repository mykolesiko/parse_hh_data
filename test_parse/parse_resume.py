from parse_hh_data import download, parse
import json

ids = download.resume_ids(
    area_id=113, #Russia https://github.com/hhru/api/blob/master/docs/areas.md
    specialization_id=1, #"Информационные технологии, интернет, телеком" https://api.hh.ru/specializations
    search_period=1, 
    num_pages=1,
    )

data = []
s = 0
for id in ids:#[:5]:
    resume = download.resume(id)
    #print(id)
    s = s + 1
    data.append(parse.resume(resume))
print(s)

with open('resume.json', 'w', encoding ='utf8') as outfile:
    json.dump(data, outfile, indent=4, ensure_ascii=False)

import csv
keys = data[0].keys()
with open('resume.csv', 'w', newline='')  as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data)


