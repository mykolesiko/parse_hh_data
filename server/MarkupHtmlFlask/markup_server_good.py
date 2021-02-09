import os
import csv

from flask import Flask, redirect, url_for, request
app = Flask(__name__)

def get_data_dir():
    return 'resume_html_reduced'

def get_result_file():
    result_file = os.path.join(get_data_dir(), 'markup_result.csv')
    if not os.path.exists(result_file):
        with open(result_file, 'w+') as fout:
            fout.write('id,markup,filename\n')
    return result_file

@app.route('/')
def start():
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
        if request.form['markup_button'] != 'Next':
            result_file = get_result_file()
            result = {
                'id' : doc_id, 
                'markup' : request.form['markup_button'], 
                'filename' : filename,
            }
            keys = result.keys()
            with open(result_file, 'a', newline='')  as fout:
                dict_writer = csv.DictWriter(fout, keys)
                dict_writer.writerows([result])            

        return redirect(url_for('markup_html', doc_id = doc_id + 1))


@app.route('/markup/<int:doc_id>')
def markup_html(doc_id):
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
    with open(result_file, mode='r') as fin:
        csv_reader = csv.DictReader(fin)
        for row in csv_reader:
            #print(f'row={row}')
            if row and row['filename'] == filename:
                marks.append(row['markup'])
    #print(f'marks: {marks}')
    #print('---debug----', url_for('markup_callback', doc_id=doc_id))

    markup_insertion = (
        f''' <form action = "{url_for('markup_callback', doc_id=doc_id, filename=filename)}" method = "POST">
                <p>
                    <input type="submit" name="markup_button" value="Cool" style="height:100px;width:200px;background-color:green;color:white">
                    <input type="submit" name="markup_button" value="So-so" style="height:100px;width:200px;background-color:yellow;">
                    <input type="submit" name="markup_button" value="Spam" style="height:100px;width:200px;background-color:red;">
                    <input type="submit" name="markup_button" value="Next">
                </p>
                <p> Marks: {marks} </p>
            </form>
        '''
    )

    with open(os.path.join(data_dir, filename), 'r') as fin:    
        resume_html = fin.read()

    body_idx = resume_html.find('<body') 
    body_idx = resume_html.find('>', body_idx) + 1

    markup_html = resume_html[:body_idx] + markup_insertion + resume_html[body_idx:]
    return markup_html
