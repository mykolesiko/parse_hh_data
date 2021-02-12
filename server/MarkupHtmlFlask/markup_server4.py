import os
import csv

from flask import Flask, redirect, url_for, request
import logging
from logging import config
import yaml
import download1
import pandas as pd
import pickle
from urllib.parse import parse_qs, urlparse
import numpy as np
from flask import send_file
import parse_saved_html as psh

HOST = "138.68.99.110"
PORT = "5002"
ROOT_DIR = "html_files"
#FILE_RESUME_MARKED = 'resume_info.csv'
FILE_RESUME_DATA = 'resume_data.csv'


PREV = 0
NEXT = 1
FIRST = 2

SPAM = 0
SOSO = 1
COOL = 2

NO_RESUME = '666'


#checked_spam = ""
#checked_soso = ""
#checked_cool = ""
#checked_not_marked = ""



def setup_logging():
   """ description """
   with open(DEFAULT_LOGGING_CONFIG_FILEPATH) as file:
       logging.config.dictConfig(yaml.safe_load(file))


def read_resumes(root_dir):
    files_data = pd.DataFrame(columns = ['resume_id', 'folder'])	
    folders = sorted([f for f in os.listdir(root_dir)])
    s = 0	
    
    print(folders)
    #options = []

#    for value in sorted(values.keys()):
 #       options.append("<option value='" + value + "'>" + values[value] + "</option>")
    for folder in folders:
        if (folder.find('.') != -1):
            continue
        files = sorted([f for f in os.listdir(root_dir + "/" + folder) if f.endswith('.html')])
        for hfile in files:
            #print(hfile)
            resume_id, ext = hfile.split(".")
            files_data.loc[s, 'resume_id'] = resume_id
            files_data.loc[s, 'folder'] = folder
            #files_data.loc[s, 'mark'] = "Not_marked"
            #files_data.loc[s, 'comment'] = ""

            s += 1
    return files_data					

def get_resume_data() :
    resumes = read_resumes(ROOT_DIR) 
    print("****************************************")
    print(resumes.info())
    resumes_marked = pd.read_csv(FILE_RESUME_DATA, dtype={'resume_id':str,'folder': str, 'mark':str, 'comment':str})
    print(resumes_marked.info())
    print("2********************************************************")
    #resume_all = pd.join(resumes_marked, how = 'left', on=['resume_id','folder'])
    resume_all = pd.merge(resumes, resumes_marked, on=['resume_id', 'folder'], how='left')
    resume_all['mark'].fillna('Not_marked',inplace=True)
    resume_all['comment'].fillna(' ',inplace=True)

    return resume_all	



DEFAULT_LOGGING_CONFIG_FILEPATH = 'logging.conf.yml'
APPLICATION_NAME = 'markup_server'
logger = logging.getLogger(APPLICATION_NAME)
print("********************************")
setup_logging()
resume_data = get_resume_data()	
print(resume_data.info())
#resume_data['mark'] = resume_data['mark'].apply(lambda x: 'Not_marked' if x == "" else x) 
#resume_data['mark'].replace(np.nan, "Not_marked", regex = True)
#resume_data['mark'].fillna('Not_marked',inplace=True)
#resume_data['comment'].fillna(' ',inplace=True)


folders = sorted([f for f in os.listdir(ROOT_DIR)])
resume_data.to_csv(FILE_RESUME_DATA, header = True, index = False)
mark_list = ['checked','checked','checked','checked',f'{folders[0]}' ]
checks_file = open("checks.pkl","wb")
pickle.dump(mark_list, checks_file)
checks_file.close()
 
app = Flask(__name__,static_folder='static')


def get_resume(resume_id, folder, mark, command):
    global resume_data
    print(resume_id, folder, mark, command)
    print(resume_data.head())
    data = resume_data[(resume_data.folder == folder)]
    print(data.shape)
    data = data[data['mark'].isin(mark)]
    print(data.shape)
    #print(data.info())
    resumes = data['resume_id'].to_list()
    size = len(resumes)
    print(size)
    if size == 0:
        return NO_RESUME
    try:
        if command == PREV:
            print ("PREV")
            ind = ind_new = resumes.index(resume_id)
            print(ind)
            ind_new =  (ind - 1 + size) % size 
            print(ind_new)
            resume_id_new = data.iloc[ind_new, 0]


        elif command == NEXT:
            print("NEXT")
            ind = ind_new = resumes.index(resume_id)
            ind_new =  (ind + 1 + size) % size
            print(ind_new)
            resume_id_new = data.iloc[ind_new, 0]


        else:
            print("else")
            ind_new = 0;
            resume_id_new = data.iloc[0, 0]
            print(resume_id_new)
    except ValueError:
        return NO_RESUME
    return resume_id_new
	
	

@app.route('/')
def start():
    logger.info("start")
    return redirect(url_for('markup_html', folder = "Default",  resume_id = "0"))

@app.route('/callback/<string:folder>/<string:resume_id>', methods = ['POST', 'GET'])
def markup_callback(folder, resume_id):
    print(request.form)    
    mark = []
    checked_spam = " "
    checked_soso = " "
    checked_cool = " "
    checked_not_marked = " "
    global resume_data
    resume_data = pd.read_csv(FILE_RESUME_DATA) 
    
    print("*************************")
    print(resume_data.head())
    if "spam" in request.form.keys():
        print("checkbox spam")
        mark.append("Spam")
        checked_spam = "checked"
    if "soso" in request.form.keys():
        print("checkbox soso")
        mark.append("So-so")
        checked_soso = "checked"
    if "cool" in request.form.keys():
        print("checkbox cool")
        checked_cool = "checked"
        mark.append("Cool")
    if "not_marked" in request.form.keys():
        print("checkbox not_marked")
        mark.append("Not_marked")
        checked_not_marked = "checked"
    folder = request.form['folder']
    print(folder)

    mark_list = []
    mark_list.append(checked_spam)
    mark_list.append(checked_soso)
    mark_list.append(checked_cool)
    mark_list.append(checked_not_marked)
    mark_list.append(request.form['folder'])
    checks_file = open("checks.pkl","wb")
    print(mark_list)
    print("before pickle {checks_file}")
    pickle.dump(mark_list, checks_file)
    print("after pickle {checks_file}")

    checks_file.close()
    if request.method == 'POST':
        print(request.form)
        if (request.form['markup_button'] == 'Prev'):
            logger.info("Prev")
            print("Prev")
            resume_id_prev = get_resume(resume_id, folder, mark, PREV)
            print(resume_id, resume_id_prev)
            return redirect(url_for('markup_html', folder = folder,  resume_id = resume_id_prev))

        if (request.form['markup_button'] == 'Next'):
            logger.info("Next")
            print("Next")
            resume_id_next = get_resume(resume_id, folder, mark, NEXT)
            print(resume_id, resume_id_next)
            return redirect(url_for('markup_html', folder = folder,  resume_id = resume_id_next ))


        elif (request.form['markup_button'] == 'Search'):
            return redirect(url_for('search'))
  
        elif (request.form['markup_button'] == 'Cool') | (request.form['markup_button'] == 'So-so') | (request.form['markup_button'] == 'Spam'):
            print("next cool spam")
            try:
                ind = resume_data['resume_id'].to_list().index(resume_id)
            except ValueError:
                return redirect(url_for('markup_html', folder = folder,  resume_id = RESUME_NO ))

            print(ind)
            print(f"resume_id = {resume_id}")
   
            temp_mark = resume_data.loc[ind, 'mark'] =  request.form['markup_button']
            temp_comment = resume_data.loc[ind, 'comment'] =  request.form['comment']
            print(f"temp_mark = {temp_mark}")
            print(f"temp_comment = {temp_comment}")
            print(resume_data.head())    
            resume_data.to_csv(FILE_RESUME_DATA, index = False)    
            logger.info("Mark")
            resume_id_next = get_resume(resume_id, folder, mark, NEXT)
            return redirect(url_for('markup_html', folder = folder,  resume_id = resume_id_next ))

        elif (request.form['markup_button'] == 'Refresh'):
            logger.info("Refresh")
            print("Refresh")
            resume_id_first = get_resume(resume_id, folder, mark, FIRST)
            return redirect(url_for('markup_html', folder = folder,  resume_id = resume_id_first ))
        elif (request.form['markup_button'] == 'Download CSV'):
            print("download")
            #filename = request.form['csv']
            #print(filename)
            return redirect(url_for('download')) 

@app.route('/markup/<string:folder>/<string:resume_id>')
def markup_html(folder, resume_id):
    logger.info("start markup_html")
    global resume_data
    resume_data = pd.read_csv(FILE_RESUME_DATA) 
    print(resume_data.head())    

    print(folder, resume_id)

    checks_file = open("checks.pkl", "rb")
    checked_spam, checked_soso, checked_cool, checked_not_marked, folder = pickle.load(checks_file)
    checks_file.close()
    print(checked_spam)
    print(checked_soso)
    print(checked_cool)
    print(checked_not_marked)

    print(checked_spam)
    marks= "Not_marked"
    comment = " "
    
    if (resume_id != NO_RESUME):
        if (resume_id == '0'):
            print("********")
            resume_id = get_resume(resume_id, folder, ["Spam", "So-so", "Cool","Not_marked"], FIRST)
            print(resume_id)
            return redirect(url_for('markup_html', folder = folder,  resume_id = resume_id))
        if resume_id != NO_RESUME:
            logger.info("start get_result_file")

            ind = resume_data['resume_id'].to_list().index(resume_id) 	
            print(resume_data.head())
            print(ind)
            if ind is not None:
                marks = resume_data.loc[ind, 'mark']
                comment = resume_data.loc[ind, 'comment'] 
                folder = resume_data.loc[ind, 'folder']
                if comment == "":
                    comment = " "
            print(resume_id, marks, comment, folder)

    print("111")
    folders = sorted([f for f in os.listdir(ROOT_DIR)])
    print(folders)
    folders_list = " "
    for fol in folders:
        print(fol)
        if fol == folder:
            folders_list += f"<option selected value={fol}>{fol}</option>"
        else :   
            folders_list += f"<option>{fol}</option>"

    print(folders_list)    
    markup_insertion = (
        f''' <form action = "{url_for('markup_callback', folder=folder, resume_id=resume_id)}" method = "POST">
                  <p>
                    <input type="submit" name="markup_button" value="Cool" style="height:100px;width:200px;background-color:green;color:white">
                    <input type="submit" name="markup_button" value="So-so" style="height:100px;width:200px;background-color:yellow;">
                    <input type="submit" name="markup_button" value="Spam" style="height:100px;width:200px;background-color:red;">
                    <input type="submit" name="markup_button" value="Prev" style="height:50px;width:100px;">
                    <input type="submit" name="markup_button" value="Next" style="height:50px;width:100px;">
                    <textarea name="comment" rows="5" cols="50" style="margin: auto">{comment}</textarea>
                    <input type="checkbox" name="spam" value="checked" {checked_spam} style="height:50px;width:50px">SPAM   </input>
		    <input type="checkbox" name="soso" value="checked" {checked_soso} style="height:50px;width:50px">SO-SO  </input>
		    <input type="checkbox" name="cool" value="checked" {checked_cool} style="height:50px;width:50px">COOL   </input>
		    <input type="checkbox" name="not_marked" value="checked" {checked_not_marked} style="height:50px;width:50px">NO MARKED   </input>
		    <select name="folder" style="height:50px;width:300px">
                        {folders_list}		  
	   	    </select>
 
                    <input type="submit" name="markup_button" value="Refresh" style="height:50px;width:100px;">
                    <input type="submit" name="markup_button" value="Search" style="height:50px;width:100px;">
               
                    <input type="submit" name="markup_button" value="Download CSV" style="height:50px;width:200px;">
               	            		


                </p>
                <p> Marks: {marks} </p>
              
            </form>
        '''
    )
#                    <textarea name="comment" rows="5" cols="50" style="aligh:bottom">{comment}</textarea>



#		    <input type="checkbox" name="spam">Spam<Br>
#		    <input type="checkbox" name="soso">Soso<Br>
#		    <input type="checkbox" name="cool">Cool<Br>
#		    <select>
#			  <option>Default</option>
#			  <option>First</option>
#	   	    </select>
 
    print("222")
    if resume_id != NO_RESUME:

        path = ROOT_DIR + "/" + folder + "/" + resume_id + ".html"
        print(path)        
        with open(path, 'r') as fin:    
            resume_html = fin.read()

        body_idx = resume_html.find('<body') 
        body_idx = resume_html.find('>', body_idx) + 1

        markup_html = resume_html[:body_idx] + markup_insertion + resume_html[body_idx:]
        logger.info("end markup_html")
        
    else:
        markup_html = markup_insertion 
    return markup_html

@app.route('/search/')
def search():
    logger.info("start search")
    return redirect(url_for('static', filename='search_resume.html'))



@app.route('/search/resume')
def search_resume():
    logger.info("search_resume")
    print("in search resumes")
    

    
    

    url = request.url
    new_folder = parse_qs(urlparse(url).query)['new_folder']
    print(new_folder[0])
    path = ROOT_DIR + "/" + new_folder[0]
    os.makedirs(path)
 
    url.replace(f"&new_folder={new_folder}","")
    url = url.replace(f"{HOST}:{PORT}","hh.ru")
    url = url + "&page=1"
    print(url)
    ids = download1.search_resume_ids(url)
    
    #dirname = 'resume_html'
    #if not os.path.exists(dirname):
    #    os.makedirs(dirname)

    #dirname2 = dirname + '_reduced'
    #if not os.path.exists(dirname2):
    #    os.makedirs(dirname2)



    print('len(ids)={}'.format(len(ids)))
    for k, id in enumerate(ids):
         resume_soup = download1.resume(id)

         #filepath = os.path.join(dirname, str(id) + '.html')
         #with open(filepath, 'w') as fin:
         #    fin.write(str(resume_soup))
         #to_extract = resume_soup.findAll('script')
         #for i, item in enumerate(to_extract):
         #    if i not in [0,6,7,8,9,10]:
         #         item.extract()
         print(path)
         filepath = os.path.join(path, str(id) + '.html')
         with open(filepath, 'w') as fin:
	      #print(f"write resume with id = {id}")	      	
              print("write")
              fin.write(str(resume_soup))
         
    resume_data = get_resume_data()	
    resume_data.to_csv(FILE_RESUME_DATA, header = True, index = False)
  
    return redirect(url_for('start'))

     
@app.route('/download/', methods=['GET', 'POST'])
def download():
    #print(app.config['UPLOAD_FOLDER'])
    print("in download")
    resume_data = get_resume_data()
    print("3************")
    psh.get_csv_json(resume_data)
    return send_file("resume_data_all.csv",as_attachment = True)
