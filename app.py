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

def generate_sample_data():
    return [
        {"name": "A2Pro_64", "age": 37, "email": "a2@example.com", "created_at": datetime.now()},
        {"name": "X3_MotoF", "age": 25, "email": "X3@example.com", "created_at": datetime.now(), "motorbike" : True}
    ]

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

@app.route('/create/database', methods=['POST'])
def create_database():
    data = request.get_json()
    database_name = data.get('name')
    
    if not database_name:
        return jsonify({"error": "Database name is required"}), 400
    
    client = get_db()
    # Creating a dummy collection since MongoDB doesn't allow empty databases
    db = client[database_name]
    db.create_collection('_temp')
    
    return jsonify({"message": f"Database '{database_name}' created successfully"})

@app.route('/create/collection', methods=['POST'])
def create_collection():
    data = request.get_json()
    database_name = data.get('database')
    collection_name = data.get('name')
    
    if not database_name or not collection_name:
        return jsonify({"error": "Database and collection names are required"}), 400
    
    client = get_db()
    db = client[database_name]
    db.create_collection(collection_name)
    
    return jsonify({"message": f"Collection '{collection_name}' created successfully"})

@app.route('/delete/database/<database>', methods=['DELETE'])
def delete_database(database):
    client = get_db()
    client.drop_database(database)
    return jsonify({"message": f"Database '{database}' deleted successfully"})

@app.route('/delete/collection/<database>/<collection>', methods=['DELETE'])
def delete_collection(database, collection):
    client = get_db()
    db = client[database]
    db.drop_collection(collection)
    return jsonify({"message": f"Collection '{collection}' deleted successfully"})

@app.route('/load-sample-data/<database>/<collection>', methods=['POST'])
def load_sample_data(database, collection):
    client = get_db()
    db = client[database]
    coll = db[collection]
    
    sample_data = generate_sample_data()
    coll.insert_many(sample_data)
    
    return jsonify({"message": f"Sample data loaded into '{collection}' successfully"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1500, debug=True)