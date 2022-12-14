from marshmallow import Schema, fields

class PSFeedback(Schema):
    item_id = fields.Integer(required = True)
    pset_id = fields.Integer(required = True)
    course_id = fields.Integer(required = True)
    feedback = fields.String(required = True) #check if there is a limit
    is_correct = fields.String(required = True)
    float_answer = fields.Float(required = True)

class AnswerForChecking(Schema):
    pset_id = fields.Integer(required = True)
    course_id = fields.Integer(required = True)
    student_id = fields.Integer(required = True)
    attempt_id = fields.Integer(required = True)
    float_answer = fields.Float(required = True)
    submit_date = fields.Integer(required = True) #double check formatting