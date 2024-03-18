from mongoengine import Document, StringField, ListField, IntField, DateTimeField, ObjectIdField, DictField

class Participant(Document):
    email = StringField(required=True)
    #user_id = ObjectIdField()

class Response(Document):
    user_id = ObjectIdField()
    form_id = ObjectIdField()
    #Enforces that each response is different 
    #response_id = ObjectIdField()
    role = StringField()
    years_of_experience = IntField()
    age = IntField()
    gender = StringField()
    vision_impairment = ListField(StringField())
    correctness_score = IntField()
    # add question to map to its corresponding eye tracking data
    eye_tracking_data = ListField(DictField())
    responses = ListField(DictField())

class UserForm(Document):
    user_id = ObjectIdField()
    # have each form map to a correctness score
    associated_forms = ListField(ObjectIdField())
    # correctness_score = IntField()

class Creator(Document):
    email = StringField(required=True)
    password = StringField(required=True)
    #user_id = ObjectIdField()
    forms_created = ListField(ObjectIdField())

class Form(Document):
    #form_id = ObjectIdField()
    responses = ListField(DictField())
    # add correct answers later
