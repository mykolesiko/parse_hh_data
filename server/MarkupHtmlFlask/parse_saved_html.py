import download, parse
import json
import os
from bs4 import BeautifulSoup
import csv
import pandas as pd

ROOT_DIR = 'html_files'
#files = os.listdir(dirname)
#print(files)

#print('*********************************************************************************')
def get_csv_json(resume_data):
    print("in get_csv_json")
    data_all=[]
    for i in range(resume_data.shape[0]):
        resume_id = resume_data.loc[i, 'resume_id']
        folder = resume_data.loc[i, 'folder']
        filepath = ROOT_DIR + '/' + folder + '/' + resume_id + '.html'
        print(filepath)
        s = 0
        with open(filepath, 'r', encoding = 'utf8') as fhtml:
            print("******************************************")
            print(filepath)
            html = fhtml.read()
            #print(html)
            try:
                data = parse.resume(BeautifulSoup(html, "html.parser"))
                data.update({'resume_id':resume_id})
                data.update({'folder':folder})
                filepath_json = ROOT_DIR + '/' + folder + '/' + resume_id + '.json'
                with open(filepath_json, 'w', encoding = 'utf8') as fjson:
                    json.dump(data, fjson, indent=4, ensure_ascii=False)
            #print(data)
                data_all.append(data)   
            except Exception:
                print("COULDN't PROCESS ")
    keys = data_all[0].keys()
    #print("ertretertretertret")
    print(keys)
    #print(data_all[0])
    with open('json.csv', 'w', newline='', encoding = 'utf8')  as output_file:

       csv_file = csv.writer(output_file, delimiter = "$")
       print(keys)
       csv_file.writerow(keys)	
       print("1*************")
       s = 0	
       for item in data_all:
             print(s)
             s = s + 1
             csv_file.writerow(item.values())
        #dict_writer = csv.DictWriter(output_file, keys)
        #dict_writer.writeheader()
        #dict_writer.writerows(data_all)
    print("2*************") 
    json_data=pd.read_csv('json.csv',  delimiter = "$")
    print("3*************")
    print(json_data.head())
    print("4*************")
    all_data = pd.merge(resume_data, json_data, on=['resume_id', 'folder'], how='inner')
    print("5*************")    
    all_data.to_csv("resume_data_all.csv")
    print(all_data.head())
    	 	
    


