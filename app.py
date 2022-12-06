from flask import Flask
from flask_restful import Api, Resource
import mysql.connector, os

#initialize database connection
mydb = mysql.connector.connect(
    host = os.environ["host"],
    user = os.environ["username"],
    password = os.environ["password"]
)

app = Flask(__name__)
api = Api(app)

class Feedback(Resource):
    def get(self): #read
        pass

    def put(self): #create
        pass

    def post(self): #update
        pass

    def delete(self): #delete
        pass
