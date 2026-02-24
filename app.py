import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
from models import create_project

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database()

@app.route('/')
def index():
    items = db.items.find()
    return render_template('index.html', items=items)


@app.route('/item/<id>')
def details(id):
    item = db.items.find_one({"_id": ObjectId(id)})
    return render_template('details.html', item=item)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        db.items.insert_one({"name": name})
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    item = db.items.find_one({"_id": ObjectId(id)})
    if request.method == 'POST':
        name = request.form.get('name')
        db.items.update_one({"_id": ObjectId(id)}, {"$set": {"name": name}})
        return redirect(url_for('index'))
    return render_template('edit.html', item=item)

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    db.items.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q')
    if query:
        results = db.items.find({"name": {"$regex": query, "$options": "i"}})
    else:
        results = []
    return render_template('search.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)