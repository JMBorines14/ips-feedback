from flask import Flask, request
from flask_restful import Api, Resource
from schema import PSFeedback, AnswerForChecking
from marshmallow import ValidationError
import mysql.connector, os, math, json
import openai

app = Flask(__name__)
api = Api(app)

def compare_and_check(item_id, student_answer, options, data):
    """This function compares the student's answer with the different answers/feedbacks for a particular item"""
    is_correct = 0
    feedback = "The answer is incorrect, but we do not know why. You may consult your instructor regarding your answer."
    for i in options:
        if math.isclose(student_answer, i[0], abs_tol = data["tolerance"]):
            is_correct = i[2]
            feedback = i[1]
            break
    
    #add entry to database
    mydb = mysql.connector.connect(
    host = os.environ["host"],
    port = os.environ["port"],
    user = os.environ["username"],
    password = os.environ["password"],
    database = os.environ["database"]
    )

    cus = mydb.cursor()
    to_return = {}, 0

    try:
        statement = "INSERT INTO attempt (item_id, pset_id, course_id, student_id, attempt_id, student_feedback, is_correct, float_answer, submit_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (item_id, data["pset_id"], data["course_id"], data["student_id"], data["attempt_id"], feedback, is_correct, student_answer, data["submit_date"])
        cus.execute(statement, values)
        mydb.commit()
        to_return = {'resp': 1, 'is_correct': is_correct, 'feedback': feedback}, 200
    except mysql.connector.Error as e:
        to_return = {'resp': 0, 'message': e.msg}, 400
    except:
        to_return = {'resp': 0,'message': 'Something is wrong'}, 400
    finally:
        if mydb.is_connected():
            cus.close()
            mydb.close()
        
        return to_return

def update_database(feedback_id, data, type):
    """Updates the feedback entity of the database"""
    #initialize database connection
    mydb = mysql.connector.connect(
    host = os.environ["host"],
    port = os.environ["port"],
    user = os.environ["username"],
    password = os.environ["password"],
    database = os.environ["database"]
    )

    cus = mydb.cursor()
    resp = 0
    msg = ""
    status_code = 400

    if type == 1:
        statement = "UPDATE feedback SET item_id = %s, pset_id = %s, course_id = %s, feedback = %s, is_correct = %s, float_answer = %s WHERE feedback_id = %s"
        values = (data["item_id"], data["pset_id"], data["course_id"], data["feedback"], data["is_correct"], data["float_answer"], feedback_id)
    elif type == 0:
        statement = "INSERT INTO feedback (item_id, pset_id, course_id, feedback_id, feedback, is_correct, float_answer) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (data["item_id"], data["pset_id"], data["course_id"], feedback_id, data["feedback"], data["is_correct"], data["float_answer"])
    elif type == -1:
        statement = "DELETE FROM feedback WHERE feedback_id = %s"
        values = (feedback_id,)
    else:
        statement = ""
        values = ()

    try:
        cus.execute(statement, values)
        mydb.commit()
        resp = 1
        msg = "Success!"
        status_code = 200
    except mysql.connector.Error as e:
        msg = e.msg
        status_code = 400
    except:
        msg = "Something else went wrong"
        status_code = 400
    finally:
        if mydb.is_connected():
            cus.close()
            mydb.close()

        return {'resp': resp, 'message': msg}, status_code

def read_database(item_id, data):
    mydb = mysql.connector.connect(
    host = os.environ["host"],
    port = os.environ["port"],
    user = os.environ["username"],
    password = os.environ["password"],
    database = os.environ["database"]
    )

    cus = mydb.cursor()

    try:
        statement = "SELECT float_answer, feedback, is_correct FROM feedback WHERE item_id = %s"
        value = (item_id)
        cus.execute(statement, value)
        result = cus.fetchall()
        return compare_and_check(item_id, data["float_answer"], result, data)
    except mysql.connector.Error as e:
        return {'resp': 0, 'message': e.msg}, 400
    except:
        return {'resp': 0, 'message': 'Something is wrong with the server'}, 500
    
def process_fields(feedback_id, type: int):
    if not request.data:
        body = {}
    else:
        try:
            body = json.loads(request.data)
        except json.JSONDecodeError as e:
            return {"resp": 0, "error": e.msg}, 400
        
    try:
        validated = PSFeedback().load(body)
    except ValidationError as e:
        return {"resp": 0, "error": "Validation failed!"}, 400
    else:
        return update_database(feedback_id, validated, type)

def summarize_prompt(text):
    return """Summarize the following essay to a 5th grader reading level: {}""".format(
        text.capitalize()
    )

def codecheck_prompt(code):
    return """Describe the function of the following code and determing any errors or inefficies: {}""".format(
        code.capitalize()
    )

class Check(Resource):
    def get(self, item_id):
        if not request.data:
            body  = {}
        else:
            try:
                body = json.loads(request.data)
            except json.JSONDecodeError as e:
                return {'resp': 0, 'error': e.msg}, 400
        
        try:
            validated = AnswerForChecking().load(body)
        except ValidationError as e:
            return {'resp': 0, 'error': "Validation error"}, 400
        else:
            return read_database(item_id, validated)

class Feedback(Resource):
    def put(self, feedback_id): #create
        return process_fields(feedback_id, 0)

    def post(self, feedback_id): #update
        return process_fields(feedback_id, 1)

    def delete(self, feedback_id): #delete
        return update_database(feedback_id, {}, -1)

class SummarizeEssay(Resource):
    def post(self):
        body = json.loads(request.data)
        response = openai.Completion.create(
            model="text-davinci-002",
            max_tokens=100,
            prompt=summarize_prompt(body["essay"]),
            temperature=0.6,
        )
        return response

class CheckCode(Resource):
    def post(self):
        body = json.loads(request.data)
        response = openai.Completion.create(
            model="text-davinci-002",
            max_tokens=500,
            prompt=codecheck_prompt(body["code"]),
            temperature=0.6,
        )
        return response

class Testing(Resource):
    def get(self):
        """Added API for testing if the server is running"""
        return {"message": "The server is up and running!"}

api.add_resource(Testing, '/test')
api.add_resource(Check, '/check/<string:item_id>')
api.add_resource(Feedback, '/feedback_put/<string:feedback_id>', 
                    '/feedback_post/<string:feedback_id>', '/feedback_delete/<string:feedback_id>')
api.add_resource(SummarizeEssay, '/summarize')
api.add_resource(CheckCode, '/codecheck')