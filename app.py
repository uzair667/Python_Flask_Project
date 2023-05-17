from flask import Flask, render_template, jsonify, request
import requests as req
import json 
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from models import *
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
from webargs import fields
from webargs.flaskparser import use_args
from datetime import datetime



import pandas as pd

app  = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin123@localhost/new_db'
app.config['UPLOAD_FOLDER'] = 'uploads'

migrate = Migrate(app, db)
db.init_app(app)


ma = Marshmallow(app)
ma.init_app(app)

@app.route('/')
def get_data() -> json:
    api_data = req.get('https://fakestoreapi.com/products')
    json_data = json.loads(api_data.content)

    schema = DataSchema(many=True)
    res = schema.load(json_data)

    data = Data()

    rowcount = db.session.query(func.count(data.title)).scalar()
    if rowcount == 0:

        db.session.add_all(res)
        db.session.commit()
    else:
        print('data already exist')

    excel = pd.DataFrame(json_data)
    excel.to_excel('uzair.xlsx',index=False)


    with open('uzair.txt', 'w') as e:
       rs = e.write(json.dumps(json_data))

    header = ('id','title','price','description','category','image','rating(rate)','rating(count)')
    return render_template('data.html', result = res, head_titles = header)

@app.route('/link_data/<id>', methods = ['GET'])
def link_data(id) -> 'html':
    user_id = id

    result = Data.query.where(Data.id == user_id).first()
    header = ('id','title','price','description','category','image','rating(rate)','rating(count)')
    return render_template('link_data.html', titles = header, rs = result)
    

@app.route('/files_page', methods = ['GET','POST'])
def files_page()->'html':
    return render_template('files_page.html')


@app.route('/files', methods = ['POST'])
def files()->'html':
    name = request.files['file']
    description = request.form['description']
    file_name = secure_filename(name.filename)
    file_ext = os.path.splitext(file_name)[1]


    i = 1
    new_filename = file_name
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], new_filename)):
        basename = os.path.splitext(file_name)[0]
        new_filename = f"{basename}({i}){file_ext}"
        i += 1
    name.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))


    file = File()
    file.file_name = new_filename
    file.file_description = description
    file.file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

    db.session.add(file)
    db.session.commit()

    result = File.query.all()

    titles = ('id','file_name','file_description','file_path')
    return render_template('file.html', rs = result, titles=titles)

@app.route('/download/<id>', methods = ['GET'])
def download_file(id)->'html':
    file_id = id
    file = File.query.filter_by(id=file_id).first()
    return send_from_directory(app.config['UPLOAD_FOLDER'], file.file_name, as_attachment=True)

@app.route('/edit', methods = ['POST'])
@use_args({'title': fields.String(required=True), 'id': fields.String(required=True)}, location = 'form')
def edit(args) ->'html':
    id = args.get('id')
    title = args.get('title')
    name = 'uzair'

    data = Data.query.where(Data.id == id).first()
    if data:
        data.title = title
        db.session.commit()
    else:
        print('data not found')

    tracking = Tracking()
    tracking.name = name
    tracking.changes = title
    tracking.time_stamp = datetime.now()
    tracking.data_id = id

    db.session.add(tracking)
    db.session.commit()

    result = Data.query.all()    
    header = ('id','title','price','description','category','image','rating(rate)','rating(count)')
    return render_template('edit.html',result = result, head_titles = header)
    
if __name__ == '__main__':
    app.run(debug = True)