from marshmallow import Schema, fields, validate, ValidationError, missing

class Feedback(Schema):
    item_id = fields.Integer(required = True)
    pset_id = fields.Integer(required = True) #double check formatting of this
    course_id = fields.Integer(required = True) #double check formatting of this
    feedback = fields.String(required = True) #check if there is a limit
    is_correct = fields.Boolean(required = True)