
from datetime import datetime
from flask import Flask, render_template, request, jsonify, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from main_copy import get_opening_message,question_1,spelling_state_1,question_2,question_3,question_4, question_5,end
from main_copy import question_6,question_7,question_8,question_9,question_10,question_11, patient_id
from main_copy import question_12,question_13,question_14,question_15,spelling_state_2,spelling_state_3,spelling_state_4
import json
import main_copy
import pickle
#from xml_creation import create_xml
import xml.etree.cElementTree as ET
from sqlalchemy.types import PickleType
from random import randint
from sqlalchemy import func, and_

#Create the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///faster.db'
db = SQLAlchemy(app)

class Intakequestions(db.Model):
    intakeID = db.Column(db.Integer, primary_key=True, nullable = False)
    patientSymptoms = db.Column(db.String(250), nullable=True)
    patientOriented = db.Column(db.String(250), nullable=True)
    patientUnderstandsYou = db.Column(db.String(250), nullable=True)
    youUnderstandPatient = db.Column(db.String(250), nullable=True)
    symptoms = db.Column(db.String(250), nullable=True)
    symptomSeverity = db.Column(db.String(250), nullable=True)
    course = db.Column(db.String(250), nullable=True)
    precipitatingFactors = db.Column(db.String(250), nullable=True)
    associatedFeatures = db.Column(db.String(250), nullable=True)
    previousEpisodes = db.Column(db.String(250), nullable=True)
    pastMedicalHistory = db.Column(db.String(250), nullable=True)
    allergies = db.Column(db.String(250), nullable=True)
    drugHistory = db.Column(db.String(250), nullable=True)
    familyHistoryOfStroke = db.Column(db.String(250), nullable=True)
    socialHistory = db.Column(db.String(250), nullable=True)
    createdDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    createdBy = db.Column(db.String(250), nullable=True)
    updatedDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    UpdatedBy = db.Column(db.String(250), nullable=True)
    Consult_intakequestions = db.relationship('Consult', backref='intakequestions', lazy=True)
    
    def __repr__(self):
        return f"Intakequestions('{self.intakeID}','{self.patientSymptoms}', '{self.patientOriented}','{self.patientUnderstandsYou}','{self.youUnderstandPatient}','{self.symptoms}','{self.symptomSeverity}','{self.course}','{self.precipitatingFactors}','{self.associatedFeatures}','{self.previousEpisodes}','{self.pastMedicalHistory}','{self.allergies}','{self.drugHistory}','{self.familyHistoryOfStroke}','{self.socialHistory}','{self.createdDate}','{self.createdBy}','{self.updatedDate}','{self.UpdatedBy}')"

class Consult(db.Model):
    consultID = db.Column(db.Integer, primary_key=True, nullable = False)
    intakeID = db.Column(db.Integer, db.ForeignKey('intakequestions.intakeID'), nullable = False)
    patientID = db.Column(db.Integer, db.ForeignKey('patients.patientID'), nullable = False)
    physicianID = db.Column(db.Integer,db.ForeignKey('physician.physicianID'), nullable = False)
    consultStartTime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    consultEndTime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    physicianAssignedTime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    consultStatus = db.Column(db.String(250), nullable=True)
    consultCreatedDatetime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    createdBy = db.Column(db.String(250), nullable=True)
    consultUpdatedDatetime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updatedBy = db.Column(db.String(250), nullable=True)
    
    
    def __repr__(self):
        return f"Consult('{self.consultID}', '{self.intakeID}','{self.patientID}','{self.physicianID}','{self.consultStartTime}','{self.consultEndTime}','{self.physicianAssignedTime}','{self.consultStatus}','{self.consultCreatedDatetime}','{self.createdBy}','{self.consultUpdatedDatetime}','{self.updatedBy}')"
    

class Patients(db.Model):
    patientID = db.Column(db.Integer, primary_key=True, nullable = False)
    patientFirstName = db.Column(db.String(250), nullable=True)
    patientLastName = db.Column(db.String(250), nullable=True)
    patientAddress1 = db.Column(db.String(250), nullable=True)
    patientAddress2 = db.Column(db.String(250), nullable=True)
    patientCity = db.Column(db.String(250), nullable=True)
    patientState = db.Column(db.String(250), nullable=True)
    patientZip = db.Column(db.String(250), nullable=True)
    patientGender = db.Column(db.String(250), nullable=True)
    patientDOB = db.Column(db.String(250), nullable=True)
    insuranceID = db.Column(db.String(250), nullable=True)
    insuranceCarrier = db.Column(db.String(250), nullable=True)
    createdDatetime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    createdBy = db.Column(db.String(250), nullable=True)
    updatedDatetime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updatedBy = db.Column(db.String(250), nullable=True)
    Consult_patients = db.relationship('Consult', backref='patients', lazy=True)
    
    
    def __repr__(self):
        return f"Patients('{self.patientID}', '{self.patientFirstName}','{self.patientLastName}','{self.patientAddress1}','{self.patientAddress2}','{self.patientCity}','{self.patientState}','{self.patientZip}','{self.patientGender}','{self.patientDOB}','{self.insuranceID}','{self.insuranceCarrier}','{self.createdDatetime}','{self.createdBy}','{self.updatedDatetime}','{self.updatedBy}')"

class Physician(db.Model):
    physicianID = db.Column(db.Integer, primary_key=True, nullable = False)
    physicianFirstName = db.Column(db.String(250), nullable=True)
    physicianLastName = db.Column(db.String(250), nullable=True)
    physicianSpecialty = db.Column(db.String(250), nullable=True)
    physicianCredential = db.Column(db.String(250), nullable=True)
    physicianShiftStartTime = db.Column(db.DateTime, nullable=True)
    physicianShiftEndTime = db.Column(db.DateTime, nullable=True)
    createdDatetime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    createdBy = db.Column(db.String(250), nullable=True)
    updatedDatetime = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updatedBy = db.Column(db.String(250), nullable=True)
    Consult_physician = db.relationship('Consult', backref='physician', lazy=True)
        
    
    def __repr__(self):
        return f"Physician('{self.physicianID}', '{self.physicianFirstName}','{self.physicianLastName}','{self.physicianSpecialty}','{self.physicianCredential}','{self.physicianShiftStartTime}','{self.physicianShiftEndTime}','{self.createdDatetime}','{self.createdBy}','{self.updatedDatetime}','{self.updatedBy}')"

def listToString(s):  
    """Converts a list to string"""
    str1 = ', '.join(s)
    return str1 

def random_with_N_digits(n):
    """Generate a random number with n digits"""
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def queryIntakeID (storage):

    subq = db.session.query(Consult.patientID, func.max(Consult.consultCreatedDatetime).label('maxdate')).group_by(Consult.patientID).subquery('t2')
    query = db.session.query(Consult).join (subq, and_(Consult.patientID == subq.c.patientID, Consult.consultCreatedDatetime == subq.c.maxdate))
    intakeID = query.filter_by(patientID = storage[0]).first().intakeID
    return str(intakeID)
    
def querycreatedDate(storage):
    createDate = Intakequestions.query.filter_by(intakeID = queryIntakeID(storage)).first().createdDate
    return str(createDate)

def queryupdatedDate(storage):
    updatedDate = Intakequestions.query.filter_by(intakeID = queryIntakeID(storage)).first().updatedDate
    return str(updatedDate)

def create_xml(storage):
    """Populate the XML file with the items from the database and the items from the 
    chatbot interaction"""
    patientID = storage[0]
    patientFirstName = Patients.query.filter_by(patientID = storage[0]).first().patientFirstName
    patientLastName = Patients.query.filter_by(patientID = storage[0]).first().patientLastName
    patientAddress = Patients.query.filter_by(patientID = storage[0]).first().patientAddress1
    patientCity = Patients.query.filter_by(patientID = storage[0]).first().patientCity
    patientState = Patients.query.filter_by(patientID = storage[0]).first().patientState
    patientZip = Patients.query.filter_by(patientID = storage[0]).first().patientZip
    patientGender = Patients.query.filter_by(patientID = storage[0]).first().patientGender
    patientDOB = Patients.query.filter_by(patientID = storage[0]).first().patientDOB
    insuranceID = Patients.query.filter_by(patientID = storage[0]).first().insuranceID
    insuranceCarrier = Patients.query.filter_by(patientID = storage[0]).first().insuranceCarrier
    intakeID = queryIntakeID (storage)
    patientSymptoms = ', '.join(storage[1])
    symptomSeverity = storage[2]
    patientOriented = storage[3]
    patientUnderstandsYou = storage[4]
    youUnderstandPatient = storage[5]
    symptoms = storage[6]
    course = storage[7]
    precipitatingFactors = storage[8]
    associatedFeatures = ', '.join(storage[9])
    previousEpisodes = storage[10]
    pastMedicalHistory = ', '.join(storage[11])
    allergies = storage[12]
    drugHistory = ', '.join(storage[13])
    familyHistoryOfStroke = storage[14]
    socialHistory = storage[15]
    createdDate= querycreatedDate(storage)
    createdBy = "SYSADMIN"
    updatedDate = queryupdatedDate(storage)
    updatedBy = "SYSADMIN"
    physicianID = '1234'
    phyisicanFirstName = Physician.query.filter_by(physicianID = '1234').first().physicianFirstName
    physicianLastName = Physician.query.filter_by(physicianID = '1234').first().physicianFirstName

    root = ET.Element("patientevaluation")
    doc = ET.SubElement(root, "record")

    ET.SubElement(doc, "patientID").text = patientID
    ET.SubElement(doc, "patientFirstName").text = patientFirstName
    ET.SubElement(doc, "patientLastName").text = patientLastName
    ET.SubElement(doc, "patientAddress").text = patientAddress
    ET.SubElement(doc, "patientCity").text = patientCity
    ET.SubElement(doc, "patientState").text = patientState
    ET.SubElement(doc, "patientZip").text = patientZip
    ET.SubElement(doc, "patientGender").text = patientGender
    ET.SubElement(doc, "patientDOB").text = patientDOB
    ET.SubElement(doc, "insuranceID").text = insuranceID
    ET.SubElement(doc, "insuranceCarrier").text = insuranceCarrier
    ET.SubElement(doc, "intakeID").text = intakeID
    ET.SubElement(doc, "patientSymptoms").text = patientSymptoms
    ET.SubElement(doc, "symptomSeverity").text = symptomSeverity
    ET.SubElement(doc, "patientOriented").text = patientOriented
    ET.SubElement(doc, "patientUnderstandsYou").text = patientUnderstandsYou
    ET.SubElement(doc, "youUnderstandPatient").text = youUnderstandPatient
    ET.SubElement(doc, "symptoms").text = symptoms
    ET.SubElement(doc, "course").text = course
    ET.SubElement(doc, "precipitatingFactors").text = precipitatingFactors
    ET.SubElement(doc, "associatedFeatures").text = associatedFeatures
    ET.SubElement(doc, "pastMedicalHistory").text = pastMedicalHistory
    ET.SubElement(doc, "allergies").text = allergies
    ET.SubElement(doc, "drugHistory").text = drugHistory
    ET.SubElement(doc, "familyHistoryOfStroke").text = familyHistoryOfStroke
    ET.SubElement(doc, "socialHistory").text = socialHistory
    ET.SubElement(doc, "createdDate").text = createdDate
    ET.SubElement(doc, "createdBy").text = createdBy
    ET.SubElement(doc, "updatedDate").text = updatedDate
    ET.SubElement(doc, "updatedBy").text = updatedBy
    ET.SubElement(doc, "physicianID").text = physicianID
    ET.SubElement(doc, "phyisicanFirstName").text = phyisicanFirstName
    ET.SubElement(doc, "physicianLastName").text = physicianLastName

    tree = ET.ElementTree(root)
    tree.write("filename.xml")
    return None

 
# state that the conversation with the chatbot is in
states = {
    0.0:patient_id,
    1.0: question_1,
    1.1:spelling_state_1,
    2.0: question_2,
    3.0: question_3,
    4.0: question_4,
    5.0: question_5,
    6.0: question_6,
    7.0: question_7,
    8.0: question_8,
    9.0: question_9,
    9.1:spelling_state_2,
    10.0: question_10,
    11.0: question_11,
    11.1:spelling_state_3,
    12.0: question_12,
    13.0: question_13,
    13.1:spelling_state_4,
    14.0: question_14,
    15.0: question_15,
    16.0: end
}

model_endpoint = "http://0.0.0.0:5000/model/predict"
#Create a global variable to store the responses
store = []

def retrieveAllPatientIDs():
    """Dumps all the patient IDs into a list, stores it as a pickle object.
    This will be used in main_copy.py to validate the patientID information"""
    query = db.session.query(Patients.patientID.distinct().label("patientID"))
    patientIDs = [row.patientID for row in query.all()]
    with open('patientList.txt','wb') as patientList:
        pickle.dump(patientIDs,patientList)
    return None

#Call the function
retrieveAllPatientIDs()

@app.route('/')
@app.route('/login')
def login():
    """User login page"""
    return render_template('login.html')

@app.route("/index.html", methods=["POST", "GET", "HEAD"])
def chat():
    """Chatbot interaction"""
    global store
    if request.method == "POST":
        '''Process an ongoing conversation.'''
        data = json.loads(request.data)
        input_text = data["input"]
        state = float(data["state"])
        #If the state is zero, clear the contents of store variable. (Restart the conversation)
        if state == 0.0:
            store = []

        # gets name of the next function based on state that conversation with chatbot is in
        get_next_text = states.get(state)
        #Goes to 'states' dictionary, retrieves the function, processes the response and returns the next question to ask
        response, new_state, info = get_next_text(model_endpoint, input_text)
        store.append(info)
        #If chatbot has reached the last state, clean up the store variable, insert processed responses into the database
        if new_state == 16.0:
            if {} in store: 
                store = [value for value in store if value!= {}]
            #Insert responses in database   
            resp = Intakequestions(intakeID = random_with_N_digits(6)
                       , patientSymptoms = listToString(store[1])
                       , patientOriented = store[2]
                       , patientUnderstandsYou =store[3]
                       , youUnderstandPatient =store[4]
                       , symptoms =store[5]
                       , symptomSeverity =store[6]
                       , course =store[7]
                       , precipitatingFactors =store[8]
                       , associatedFeatures =listToString(store[9])
                       , previousEpisodes =store[10]
                       , pastMedicalHistory =listToString(store[11])
                       , allergies =store[12]
                       , drugHistory =listToString(store[13])
                       , familyHistoryOfStroke =store[14]
                       , socialHistory =store[15]
                      )
            db.session.add(resp)
            db.session.commit()
            #Assign physician
            consult = Consult (consultID = random_with_N_digits(6)
                       , intakeID = resp.intakeID
                       , patientID = store[0] #Patient ID is stored here
                       , physicianID = 1234
                       
                       )
            db.session.add(consult)
            db.session.commit()
            #Dump store contents into a pickle object (more for testing purposes)
            with open('file.txt','wb') as f:
                pickle.dump(store,f)

            #Create the XML file with the stored responses
            create_xml(store)
        return jsonify({"response": response, "state": new_state, "matches": info})

    else:
        '''Start a conversation.'''
        return render_template("index.html", display_text=get_opening_message(), state=0.0)


if __name__ == "__main__":
    
    # Start the app
    app.run(port=8000, host="0.0.0.0", debug=False)
    
