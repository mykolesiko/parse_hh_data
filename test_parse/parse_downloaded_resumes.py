import download, parse
import json
import os
from bs4 import BeautifulSoup

dirname = 'html_data'
files = os.listdir(dirname)
print(files)

#print('*********************************************************************************')

data_all = []
for file in files:
    filepath = dirname + '//' + file 
    with open(filepath, 'r', encoding = 'utf8') as fhtml:
        html = fhtml.read()
        #print(html)
        data = parse.resume(BeautifulSoup(html, "html.parser"))
        name, ext = file.split(".")
        with open("json_data//" + name + '.json', 'w', encoding ='utf8') as outjson:
            json.dump(data, outjson, indent=4, ensure_ascii=False)
        data_all.append(data)   



import csv
keys = data_all[0].keys()
with open('resume.csv', 'w', newline='', encoding = 'utf8')  as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data_all)


