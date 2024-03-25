from mongoengine import Document, EmbeddedDocument, ReferenceField, StringField, ListField, IntField, DateTimeField, ObjectIdField, DictField

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
    #add questions
    questions = ListField(DictField())

    # we could replace questions with this
    #questions = ListField(EmbeddedDocumentField(Question))



class Form(Document):
    #form_id = ObjectIdField()
    responses = ListField(DictField())
    # add correct answers later
    #add questions
    questions = ListField(DictField())
    question_text = StringField(required=True)
    question_type = StringField(required=True)
    correct_answer = StringField()

# possible question schema
class Question(EmbeddedDocument):
    # question_id = ObjectIdField()
    question_text = StringField(required=True)
    question_type = StringField(required=True)
    options = ListField(StringField())  # If applicable, for multiple choice questions
    correct_answer = StringField()
    # could also possibly add a classification for where the skin lesion is located

class Form(Document):
    form_name = StringField(required=True)
    date_created = DateTimeField(required=True)
    questions = ListField(ReferenceField(Question))