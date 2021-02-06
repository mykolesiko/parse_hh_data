from parse_hh_data import download, parse
import json
import os

dirname = 'resume_html'
if not os.path.exists(dirname):
    os.makedirs(dirname)

dirname2 = dirname + '_reduced'
if not os.path.exists(dirname2):
    os.makedirs(dirname2)



ids = download.resume_ids(
    area_id=113, #Russia https://github.com/hhru/api/blob/master/docs/areas.md
    specialization_id=1, #"Информационные технологии, интернет, телеком" https://api.hh.ru/specializations
    search_period=1, 
    num_pages=1,
    )
n = len(ids)
print('len(ids)={}'.format(len(ids)))

for k, id in enumerate(ids):
    resume_soup = download.resume(id)

    filepath = os.path.join(dirname, str(id) + '.html')
    with open(filepath, 'w') as fin:
        fin.write(str(resume_soup))

    to_extract = resume_soup.findAll('script')
    for i, item in enumerate(to_extract):
        if i not in [0,6,7,8,9,10]:
            item.extract()

    filepath = os.path.join(dirname2, str(id) + '.html')
    with open(filepath, 'w') as fin:
        fin.write(str(resume_soup))

    print(f'write {k} of {n} resume with id = {id}')
