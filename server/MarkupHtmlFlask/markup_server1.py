import os
import csv


from flask import Flask, redirect, url_for, request
import logging
from logging import config
import yaml
import download1

HOST = "138.68.99.110"
PORT = "5002"

def setup_logging():
   """ description """

   with open(DEFAULT_LOGGING_CONFIG_FILEPATH) as file:
       logging.config.dictConfig(yaml.safe_load(file))


DEFAULT_LOGGING_CONFIG_FILEPATH = 'logging.conf.yml'
APPLICATION_NAME = 'markup_server1'
logger = logging.getLogger(APPLICATION_NAME)
print("********************************")
setup_logging()
app = Flask(__name__,static_folder='static')


def get_data_dir():
    return 'resume_html_reduced'

def get_result_file():
    result_file = os.path.join(get_data_dir(), 'markup_result.csv')
    if not os.path.exists(result_file):
        with open(result_file, 'w+') as fout:
            fout.write('id,markup,comment,filename\n')
    return result_file

@app.route('/')
def start():
#    with open("test", "wb") as file:
#        pass
    logger.info("start")
    return redirect(url_for('markup_html',doc_id = 0))

@app.route('/callback/<int:doc_id>/<string:filename>',methods = ['POST', 'GET'])
def markup_callback(doc_id, filename):
    if request.method == 'POST':
        #print('-------------markup_button={}, doc_id={}, filename={}'.format(
        #                    request.form['markup_button'],
        #                    doc_id,
        #                    filename,#request.form['markup_filename'],
        #                    )
        #)

        if (request.form['markup_button'] == 'Prev'):
           logger.info("Prev")
           if (doc_id == 1):
               return redirect(url_for('markup_html', doc_id = doc_id))
           else:
               return redirect(url_for('markup_html', doc_id = doc_id - 1))


        elif (request.form['markup_button'] == 'Search'):
               return redirect(url_for('search'))
  
        elif (request.form['markup_button'] != 'Next'):
            result_file = get_result_file()
            result = {
                'id' : doc_id, 
                'markup' : request.form['markup_button'], 
                'comment' : request.form['comment'],
                'filename' : filename,
            }
            keys = result.keys()
            with open(result_file, 'a', newline='')  as fout:
                dict_writer = csv.DictWriter(fout, keys)
                dict_writer.writerows([result])            
       
       
        return redirect(url_for('markup_html', doc_id = doc_id + 1))


@app.route('/markup/<int:doc_id>')
def markup_html(doc_id):
    logger.info("start markup_html")

    data_dir = get_data_dir()
    result_file = get_result_file()

    html_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.html')])

    #print('------------------doc_id={} type={} len={}'.format(doc_id, type(doc_id), len(html_files)))
    if doc_id < 0:
        return "doc_id={} is negative!".format(doc_id)
    if doc_id >= len(html_files):
        return "That's all {}!".format(len(html_files))

    filename =  html_files[doc_id]

    result_file = get_result_file()
    marks=[]
    comment = " "

    logger.info("start get_result_file")

    with open(result_file, mode='r') as fin:
        csv_reader = csv.DictReader(fin)
        for row in csv_reader:
            #print(f'row={row}')
            if row and row['filename'] == filename:
                marks.append(row['markup'])
                comment = row['comment']
                if comment is None:
                    comment = " "

    #logger.info(f"read result file filename={filename} comment={comment}")
            
    #print(f'marks: {marks}')
    #print('---debug----', url_for('markup_callback', doc_id=doc_id))

    markup_insertion = (
        f''' <form action = "{url_for('markup_callback', doc_id=doc_id, filename=filename)}" method = "POST">
                <p>
                    <input type="submit" name="markup_button" value="Cool" style="height:100px;width:200px;background-color:green;color:white">
                    <input type="submit" name="markup_button" value="So-so" style="height:100px;width:200px;background-color:yellow;">
                    <input type="submit" name="markup_button" value="Spam" style="height:100px;width:200px;background-color:red;">
                    <input type="submit" name="markup_button" value="Prev" style="height:50px;width:100px;">
                    <input type="submit" name="markup_button" value="Next" style="height:50px;width:100px;">
                    <textarea name="comment" align="bottom" rows="5" cols="50">{comment}</textarea>
                    
                    <input type="submit" name="markup_button" value="Search" style="height:50px;width:100px;">


                </p>
                <p> Marks: {marks} </p>
              
            </form>
        '''
    )

#     <input type="submit" name="markup_button" value="Prev">
#                    <input type="submit" name="markup_button" value="Next">
#                    <input type="text" name="comment" value={comment}>



                

    with open(os.path.join(data_dir, filename), 'r') as fin:    
        resume_html = fin.read()

    body_idx = resume_html.find('<body') 
    body_idx = resume_html.find('>', body_idx) + 1

    markup_html = resume_html[:body_idx] + markup_insertion + resume_html[body_idx:]
    logger.info("end markup_html")

    return markup_html



@app.route('/search/')
def search():
    logger.info("start search")
    #print("search")

    #search_html = "hello"    
    #with open("search_resume.html", mode='r') as fin:
         #print(search_html)
         #search_html = fin.read()
         #print(search_html)
#   logger.info("end search_html")

    #return search_html
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

     

