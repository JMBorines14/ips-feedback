from flask import Flask, request
from flask_restful import Api, Resource
from schema import Feedback
from marshmallow import ValidationError
import mysql.connector, os, math, json

#initialize database connection
mydb = mysql.connector.connect(
    host = os.environ["host"],
    user = os.environ["username"],
    password = os.environ["password"]
)

app = Flask(__name__)
api = Api(app)

def update_database(feedback_id, data, type):
    global mydb

    cus = mydb.cursor()

    if type == 1:
        statement = ""
    elif type == 0:
        statement = ""
    elif type == -1:
        statement = ""
    else:
        statement = ""

    cus.execute(statement)
    mydb.commit()

def read_database(item_id):
    global mydb
    cus = mydb.cursor()

    statement = ""
    cus.execute(statement)
    
    result = cus.fetchall()

def process_fields(feedback_id, type: int):
    if not request.data:
        body = {}
    else:
        try:
            body = json.loads(request.data)
        except json.JSONDecodeError as e:
            return {"resp": 0, "error": e.msg}, 400
        
        try:
            validated = Feedback().load(body)
        except ValidationError as e:
            return {"resp": 0, "error": e.msg}, 400
        else:
            update_database(feedback_id, validated, type)
            return {"resp": 1, "msg": "Success!"}, 201

class Check(Resource):
    def get(self, item_id):
        pass

class Feedback(Resource):
    def put(self, feedback_id): #create
        process_fields(feedback_id, 0)

    def post(self, feedback_id): #update
        process_fields(feedback_id, 1)

    def delete(self, feedback_id): #delete
        process_fields(feedback_id, -1)

class Testing:
    def get(self):
        """Added API for testing if the server is running"""
        return {"message": "The server is up and running!"}

api.add_resource(Testing, '/test')
api.add_resource(Check, '/check/<string:item_id>')
api.add_resource(Feedback, '/feedback_put/<string:feedback_id>', 
                    'feedback_post/<string:feedback_id>', 'feedback_delete/<string:feedback_id>')