import os
import csv

from flask import Flask, redirect, url_for, request
import logging
from logging import config
import yaml
import download1
import pandas as pd

HOST = "138.68.99.110"
PORT = "5002"
ROOT_DIR = "html_files"
FILE_RESUME_MARKED = 'resume_info.csv'


PREV = 0
NEXT = 1
FIRST = 2

SPAM = 0
SOSO = 1
COOL = 2

NO_RESUME = '666'


def setup_logging():
   """ description """
   with open(DEFAULT_LOGGING_CONFIG_FILEPATH) as file:
       logging.config.dictConfig(yaml.safe_load(file))


def read_resumes(root_dir):
    files_data = pd.DataFrame(columns = ['resume_id', 'folder','mark', 'comment'])	
    folders = sorted([f for f in os.listdir(root_dir)])
    s = 0	
    
    #options = []

#    for value in sorted(values.keys()):
 #       options.append("<option value='" + value + "'>" + values[value] + "</option>")
    for folder in folders:
        files = sorted([f for f in os.listdir(root_dir + "/" + folder) if f.endswith('.html')])
        for hfile in files:
            print(hfile)
            resume_id, ext = hfile.split(".")
            files_data.loc[s, 'resume_id'] = resume_id
            files_data.loc[s, 'folder'] = folder
            files_data.loc[s, 'mark'] = "Not_marked"
            files_data.loc[s, 'comment'] = ""

            s += 1
    return files_data					

def get_resume_data() :
    resumes = read_resumes(ROOT_DIR) 
    print(resumes.info())
    resumes_marked = pd.read_csv(FILE_RESUME_MARKED)	
    print(resumes_marked.info())
    resume_all = resumes#join(resumes_marked, how = 'left')#, on=['resume_id','folder'])

    return resume_all	



DEFAULT_LOGGING_CONFIG_FILEPATH = 'logging.conf.yml'
APPLICATION_NAME = 'markup_server'
logger = logging.getLogger(APPLICATION_NAME)
print("********************************")
setup_logging()
resume_data = get_resume_data()	
app = Flask(__name__,static_folder='static')


def get_resume(resume_id, folder, mark, command):
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
    return resume_id_new
	
	

@app.route('/')
def start():
    logger.info("start")
    return redirect(url_for('markup_html', folder = "Default",  resume_id = "0", checked_spam = "checked", checked_soso = "checked",checked_cool = "checked",checked_not_marked = "checked" ))

@app.route('/callback/<string:folder>/<string:resume_id>', methods = ['POST', 'GET'])
def markup_callback(folder, resume_id):
    print(request.form)    
    mark = []
    checked_spam = ""
    checked_soso = ""
    checked_cool = ""
    checked_not_marked = ""

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

    if request.method == 'POST':
        print(request.form)
        if (request.form['markup_button'] == 'Prev'):
            logger.info("Prev")
            resume_id_prev = get_resume(resume_id, folder, mark, PREV)
            return redirect(url_for('markup_html', folder = folder,  resume_id = resume_id_prev, checked_spam = checked_spam, checked_soso = checked_soso, checked_cool = checked_cool, checked_not_marked = checked_not_marked ))

        if (request.form['markup_button'] == 'Next'):
            logger.info("Next")
            resume_id_next = get_resume(resume_id, folder, mark, NEXT)
            return redirect(url_for('markup_html', folder = folder,  resume_id = resume_id_next,  checked_spam = checked_spam, checked_soso = checked_soso, checked_cool = checked_cool, checked_not_marked = checked_not_marked ))


        elif (request.form['markup_button'] == 'Search'):
            return redirect(url_for('search'))
  
        elif (request.form['markup_button'] == 'Cool') | (request.form['markup_button'] == 'Soso') | (request.form['markup_button'] == 'Spam'):
            print("next cool spam")
            ind = resume_data['resume_id'].to_list().index(resume_id)
            print(ind)
            if (ind):
                print("1")
                resume_data.loc[ind, 'mark'] =  request.form['markup_button']
                resume_data.loc[ind, 'comment'] =  request.form['comment']
                print("2")
            logger.info("Mark")
            resume_id_next = get_resume(resume_id, folder, mark, NEXT)
            return redirect(url_for('markup_html', folder = folder,  resume_id = resume_id_next,  checked_spam = checked_spam, checked_soso = checked_soso, checked_cool = checked_cool, checked_not_marked = checked_not_marked ))

        elif (request.form['markup_button'] == 'Refresh'):
            logger.info("Refresh")

            resume_id_first = get_resume(resume_id, folder, mark, FIRST)
            return redirect(url_for('markup_html', folder = folder,  resume_id = resume_id_first,  checked_spam = checked_spam, checked_soso = checked_soso, checked_cool = checked_cool, checked_not_marked = checked_not_marked ))
        elif (request.form['markup_button'] == 'Save'):
            logger.info("Save")
            resume_data.to_csv("FILE_RESUME_MARKED")
            return redirect(url_for('markup_html', folder = folder,  resume_id = resume_id,  checked_spam = checked_spam, checked_soso = checked_soso, checked_cool = checked_cool, checked_not_marked = checked_not_marked ))



@app.route('/markup/<string:folder>/<string:resume_id>/<string:checked_spam>/<string:checked_soso>/<string:checked_cool>/<string:checked_not_marked>/')
def markup_html(folder, resume_id, checked_spam, checked_soso, checked_cool, checked_not_marked):
    logger.info("start markup_html")
    print(folder, resume_id)
   
    marks= "Not_marked"
    comment = " "
    
    if (resume_id != NO_RESUME):
        if (resume_id == '0'):
            resume_id = get_resume(resume_id, folder, ["Spam", "So-so", "Cool","Not_marked"], FIRST)
            print(resume_id)
            return redirect(url_for('markup_html', folder = folder,  resume_id = resume_id,  checked_spam = checked_spam, checked_soso = checked_soso, checked_cool = checked_cool, checked_not_marked = checked_not_marked ))
        if resume_id != NO_RESUME:
            logger.info("start get_result_file")

            ind = resume_data['resume_id'].to_list().index(resume_id) 	
            print(ind)
            if (ind):
                marks = resume_data.loc[ind, 'mark']
                comment = resume_data.loc[ind, 'comment'] 
                folder = resume_data.loc[ind, 'folder']
            print(resume_id, marks, comment, folder)

    print("111")
    markup_insertion = (
        f''' <form action = "{url_for('markup_callback', folder=folder, resume_id=resume_id, checked_spam = checked_spam, checked_soso = checked_soso, checked_cool = checked_cool, checked_not_marked = checked_not_marked )}" method = "POST">
                  <p>
                    <input type="submit" name="markup_button" value="Cool" style="height:100px;width:200px;background-color:green;color:white">
                    <input type="submit" name="markup_button" value="So-so" style="height:100px;width:200px;background-color:yellow;">
                    <input type="submit" name="markup_button" value="Spam" style="height:100px;width:200px;background-color:red;">
                    <input type="submit" name="markup_button" value="Prev" style="height:50px;width:100px;">
                    <input type="submit" name="markup_button" value="Next" style="height:50px;width:100px;">
                    <textarea name="comment" rows="5" cols="50" style="aligh:bottom">{comment}</textarea>
                    <input type="checkbox" name="spam" value="checked" {checked_spam} style="height:50px;width:50px">Spam</input>
		    <input type="checkbox" name="soso" value="checked" {checked_soso} >Soso</input>
		    <input type="checkbox" name="cool" value="checked" {checked_cool}>Cool</input>
		    <input type="checkbox" name="not_marked" value="checked" {checked_not_marked}>No marked</input>
		    <select name="folder">
			  <option>Default</option>
			  <option>First</option>
	   	    </select>
 
                    <input type="submit" name="markup_button" value="Refresh" style="height:50px;width:100px;">
                    <input type="submit" name="markup_button" value="Search" style="height:50px;width:100px;">
               	            		


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
    url = request.url
    url = url.replace(f"{HOST}:{PORT}","hh.ru")
    url = url + "&page=1"
    print(url)
    ids = download1.search_resume_ids(url)

    dirname = 'resume_html'
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    dirname2 = dirname + '_reduced'
    if not os.path.exists(dirname2):
        os.makedirs(dirname2)



    print('len(ids)={}'.format(len(ids)))
    for k, id in enumerate(ids):
         resume_soup = download1.resume(id)

         filepath = os.path.join(dirname, str(id) + '.html')
         with open(filepath, 'w') as fin:
             fin.write(str(resume_soup))
         to_extract = resume_soup.findAll('script')
         for i, item in enumerate(to_extract):
             if i not in [0,6,7,8,9,10]:
                  item.extract()
         filepath = os.path.join(dirname2, str(id) + '.html')
         with open(filepath, 'w') as fin:
	      #print(f"write resume with id = {id}")	      	
              print("write")
              fin.write(str(resume_soup))
         
       
    return redirect(url_for('start'))

     

