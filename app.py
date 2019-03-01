import json
import mimetypes
from datetime import datetime

from bson import ObjectId, json_util
from bson.errors import InvalidId
from flask import Flask, Response, abort, jsonify, make_response, request
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://db:27017/restdb'

mongo = PyMongo(app)

def to_json(data):
    """Convert Mongo object(s) to JSON"""
    return json.dumps(data, default=json_util.default)

DEFAULT_HEADER = {'Content-Type': 'application/json'}

@app.errorhandler(404)
def not_found(error):
    return make_response(to_json({'error': 'Not found'}), 404)


@app.errorhandler(400)
def aborted(error):
    return make_response(to_json({'error': 'Aborted'}), 400)


@app.route('/lists/', methods=['GET', 'POST'])
def lists_list():
    lists = mongo.db.lists
    if request.method == 'GET':
        """Return a list of all todo lists
        GET /lists/?limit=10&offset=20
        """
        lim = int(request.args.get('limit', 10))
        off = int(request.args.get('offset', 0))
        results = lists.find().skip(off).limit(lim)
        json_results = list(results)
        return to_json(json_results), 200, DEFAULT_HEADER

    elif request.method == 'POST':
        """Create a todo list
        POST /lists/
        {"title": "Some title"}
        """
        if not request.json or not 'title' in request.json:
            abort(400)
        new_list = {
            "title": request.json.get('title')
        }
        list_id = lists.insert_one(new_list).inserted_id
        response = lists.find_one_or_404({"_id": list_id})
        return to_json(response), 201, DEFAULT_HEADER


@app.route('/lists/<id>', methods=['GET', 'PUT', 'DELETE'])
def lists_detail(id):
    lists = mongo.db.lists
    if request.method == 'GET':
        """Return specific todo list
        GET /lists/123456
        """
        result = lists.find_one({"_id": ObjectId(id)})
        return to_json(result), 200, DEFAULT_HEADER

    elif request.method == 'PUT':
        """Edit specific todo list
        PUT /lists/123456
        {"title": "Some title"}
        """
        if not request.json or not 'title' in request.json:
            abort(400)
        title = request.json.get('title')
        result = lists.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set":{"title": title}},
            upsert=False,
            new=True
        )
        return to_json(result), 200, DEFAULT_HEADER

    elif request.method == 'DELETE':
        """Edit specific todo list
        DELETE /lists/123456
        """
        response = lists.delete_one({"_id": ObjectId(id)})
        if response.deleted_count == 1:
            result = {'message' : 'record deleted'}
        else: 
            result = {'message' : 'no record found'}
        return to_json(result), 200, DEFAULT_HEADER
        
################################################################

@app.route('/items/', methods=['POST'])
def items_list():
    lists = mongo.db.lists
    """Create a todo item
    POST /items/
    {"parent_id": "<parent list id>",
    "text": "<str>",
    "due_date": <timestamp>",
    "finished_status": "<bool>"}
    """
    if not request.json or not 'text' in request.json \
                    or not 'parent_id' in request.json:
        abort(400)
    parent_id = request.json.get('parent_id')
    text = request.json.get('text')
    due_date = request.json.get('due_date')
    if due_date:
        due_date = datetime.fromtimestamp(due_date)
    finished_status = request.json.get('finished_status', False)

    new_list_entry = {
        "_id": ObjectId(),
        "text": text,
        "due_date": due_date,
        "finished_status": finished_status
    }
    result = lists.find_one_and_update(
        {"_id": ObjectId(parent_id)},
        {"$push":
            {"items": new_list_entry}
        },
        upsert=False,
        new=True
    )
    return to_json(result), 201, DEFAULT_HEADER


@app.route('/items/<id>', methods=['PUT', 'DELETE'])
def items_detail(id):
    lists = mongo.db.lists
    if request.method == 'PUT':
        """Edit specific todo item
        PUT /items/123456
        {"text": "<todo text>",
        "due_date": "unix timestamp",
        "finished_status": "<status>"}
        """
        if not request.json:
            abort(400)
        text = request.json.get('text', False)
        due_date = request.json.get('due_date', False)
        if due_date:
            due_date = datetime.fromtimestamp(due_date)
        finished_status = request.json.get('finished_status', False)
        update_data = {}
        update_items = {
            "text": text,
            "due_date": due_date,
            "finished_status": finished_status
                    }
        for k,v in update_items.items():
            if v:
                update_data["items.$." + k] = v
        response = lists.find_one_and_update(
            {"items._id": ObjectId(id)},
                {"$set": update_data},
            upsert=False,
            new=True
        )
        return to_json(response), 200, DEFAULT_HEADER

    elif request.method == 'DELETE':
        """Delete specific todo item
        DELETE /item/123456
        """
        try:
            response = lists.update_one(
                {},
                {
                "$pull":{
                    'items':{
                        '_id': ObjectId(id)}
                    }
                },
                upsert=False
            )
        except InvalidId as e:
            return to_json({'error': str(e)}), 200, DEFAULT_HEADER
        if response.modified_count == 1:
            result = {'message' : 'record deleted'}
        else: 
            result = {'message' : 'no record found'}
        return to_json(result), 200, DEFAULT_HEADER


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
