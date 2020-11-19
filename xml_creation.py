#!/usr/bin/env python
# coding: utf-8

# In[3]:


import xml.etree.cElementTree as ET


# In[5]:




#define variables
def create_xml(storage):
    patientID = storage[0]
    patientFirstName = "Adam"
    patientLastName = "Smith"
    patientAddress = "123 Python Way"
    patientCity = "Chicago"
    patientState = "IL"
    patientZip = "12345"
    patientGender = "Male"
    patientDOB = "2002-01-01"
    insuranceID = "123456"
    insuranceCarrier = "Blue Cross Blue Shield"
    intakeID = "123456"
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
    createdDate= "44131"
    createdBy = "MJONES"
    updatedDate = "44131"
    updatedBy = "MJONES"
    physicianID = "99"
    phyisicanFirstName = "PFirstName"
    physicianLastName = "PLastName"

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


# In[ ]:




