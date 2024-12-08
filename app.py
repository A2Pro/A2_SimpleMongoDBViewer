#!/usr/bin/python3

from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from bson import ObjectId, json_util
import json
from datetime import datetime

app = Flask(__name__)


def get_db():
    client = MongoClient("mongodb://a2pro:Eight63teal@192.168.0.50:27017/admin")
    return client


def convert_to_json(obj):
    return json.loads(json_util.dumps(obj))

@app.route('/')
def index():
    client = get_db()
    databases = client.list_database_names()
    return render_template('index.html', databases=databases)

@app.route('/collections/<database>')
def get_collections(database):
    client = get_db()
    db = client[database]
    collections = db.list_collection_names()
    return jsonify(collections)

@app.route('/data/<database>/<collection>')
def get_data(database, collection):
    client = get_db()
    db = client[database]
    coll = db[collection]
    
    
    query_str = request.args.get('query', '{}')
    try:
        query = json.loads(query_str)
    except json.JSONDecodeError:
        query = {}
    
    
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    skip = (page - 1) * per_page
    
    
    total = coll.count_documents(query)
    
    
    documents = list(coll.find(query).skip(skip).limit(per_page))
    
    return jsonify({
        'total': total,
        'data': convert_to_json(documents),
        'page': page,
        'pages': (total // per_page) + 1
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1500, debug=True)