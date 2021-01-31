import os
import csv

from flask import Flask, redirect, url_for, request
app = Flask(__name__)


DATA_DIR = 'html_data'

@app.route('/')
def start():
    return redirect(url_for('markup_html',doc_id = 0))

@app.route('/callback/<int:doc_id>',methods = ['POST', 'GET'])
def markup_callback(doc_id):
    if request.method == 'POST':
        print('-------------markup_button={}, doc_id={}, filename={}'.format(
                            request.form['markup_button'],
                            doc_id,
                            request.form['markup_filename'],
                            )
        )
        result_file = os.path.join(DATA_DIR, 'markup_result.csv')
        result = {'id':doc_id, 'markup':request.form['markup_button'], 'filename':request.form['markup_filename']}
        keys = result.keys()
        is_header_need = not os.path.exists(result_file)
        with open(result_file, 'a+', newline='')  as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            if is_header_need:
                dict_writer.writeheader()
            dict_writer.writerows([result])            

        return redirect(url_for('markup_html', doc_id = doc_id + 1))


@app.route('/markup/<int:doc_id>')
def markup_html(doc_id):

    html_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.html')])

    filename =  html_files[doc_id]

    markup_insertion = (
        f''' <form action = "http://localhost:5000/callback/{doc_id}" method = "POST">
                <p>
                    <input type="submit" name="markup_button" value="Great">
                    <input type="submit" name="markup_button" value="Spam">
                </p>
                <p>File <input type = "text" name="markup_filename" value = "{filename}" /></p>
            </form>
        '''
    )

    with open(os.path.join(DATA_DIR, filename), 'r') as fin:    
        resume_html = fin.read()

    body_idx = resume_html.find('<body') 
    body_idx = resume_html.find('>', body_idx) + 1

    markup_html = resume_html[:body_idx] + markup_insertion + resume_html[body_idx:]
    return markup_html

if __name__ == '__main__':
   app.run(debug = True)

