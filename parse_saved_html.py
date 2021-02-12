import download, parse
import json
import os
from bs4 import BeautifulSoup
import csv

#dirname = 'html_data'
#files = os.listdir(dirname)
#print(files)

#print('*********************************************************************************')
def get_csv_json(resume_data):
    
    for i in resume_data.shape[0]
        resume_id = resume_data.loc[i, 'resume_id']
        folder = resume_data.loc[i, 'folder']
        filepath = folder + '//' + resume_id + '.html'
        with open(filepath, 'r', encoding = 'utf8') as fhtml:
            html = fhtml.read()
            #print(html)
            data = parse.resume(BeautifulSoup(html, "html.parser"))
            print(data)
            data_all.append(data)   
    keys = data_all[0].keys()
    with open('json.csv', 'w', newline='', encoding = 'utf8')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_all)


