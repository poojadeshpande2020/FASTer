#!/usr/bin/env python
# coding: utf-8
#Import all required libraries
import pandas as pd
import numpy as np
import spacy
import nltk
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import string
import os
import random
import pickle
from building_spacy_model import load_model,detected_keywords
from spacy import displacy

#Load the spacy models
ner1 = load_model('./spacy_model_symptoms_final')
ner2 = load_model('./spacy_model_drugs_final')

#Load spellcheck models
with open('./spellchecker1','rb') as f_d:
    symspell1 = pickle.load(f_d)
with open('./spellchecker2','rb') as f:
    symspell2 = pickle.load(f)

#Process stopwords
sw = set(stopwords.words('english'))
remove_words = ['no','not']
add_words = ['patient','showing','experiencing']
new_sw = set([word for word in sw if word not in remove_words])
new_sw = new_sw.union(add_words)

def preprocess(user_input):
    """Returns a lower case sentence WITHOUT punctuation, digits and stop words"""

    #Tokenize
    tokens = word_tokenize(user_input)
    #Remove punctuation
    tokens = [token for token in tokens if token not in string.punctuation]
    #Lower case
    tokens = [token.lower() for token in tokens]
    #Remove digits
    tokens = [token for token in tokens if not token.isdigit()]
    #Remove stopwords
    tokens = [token for token in tokens if token not in new_sw]
    #Returns a sentence
    return ' '.join(tokens)
    
def spellcheck2(user_input,spell_obj):
    """Returns a dataframe consisting of 2 suggestions for the misspelled word"""
    global new_sw
    #Tokenize the sentence
    words = word_tokenize(user_input)
    data = []
    for word in words:
        row = []
        suggestions = spell_obj.lookup(word,verbosity = 2,max_edit_distance = 3,include_unknown = False,transfer_casing = False)
        #If there are no suggestions then move onto the next word
        if len(suggestions) == 0:
            continue
        #Take top two suggestions
        for s in suggestions[:2]:
            correct = str(s).split(',')[0]
            if (correct in new_sw) or (correct == word):
                break
            #Insert the misspelled word in the list
            if len(row) == 0:
                row.append(word)
            #Append the correction
            row.append(correct)
        #If there's only one suggestion then insert ' ' in the second column
        if len(row) >0 and len(row)<3:
            row.append('')
        #Insert 'none of the above' in the last column
        if len(row)==3:    
            row.append('none of the above')
            data.append(row)
            
    df = pd.DataFrame(data,columns = ['misspelled','1','2','3'])
    df.replace({'':np.nan},inplace=True)
    return df



#Take the output from spellcheck then pass the entire sentence through this.
#Uses NER model to extract the symptoms
def extraction(user_input,ner_obj):
    """Uses NER to return a list of detected symptoms"""
    doc = ner_obj(user_input)
    entities = [(str(token),token.label_) for token in doc.ents]
    detected_entities = detected_keywords(entities)
  
    return detected_entities

def numbered_print(row):
    """Returns text that offers spelling suggestions for the misspelled word"""
    o = []
    final = "Please choose a number which describes the appropriate correction for the misspelled word : '{}'\n".format(row['misspelled'])
    for i,s in enumerate(row.index[1:]):
        if not pd.isnull(row[s]):
            o.append(i+1)
            final = final + str(i+1) + "." + row[s] + "\n"
    return final,o

def replace_word(row,userinput,orig_sent):
    """replace the misspelled word with the chosen correction"""
    misspelled = row['misspelled']
    correct_word = row[userinput]
    new_sent = orig_sent.replace(misspelled,correct_word,1)
    return new_sent

#Global variables
orig_sent = ""
d = pd.DataFrame()
options = []
#Load the patient list
with open('patientList.txt','rb') as patientList:
        patient_list = pickle.load(patientList)

# # Building the chatbot workflow
def get_opening_message():
    '''The variable starting message.'''
    return "Hi, my name is FASTer!\nI will be helping you with stroke patient intake.\nPlease enter the six digit patient ID" 

def patient_id(model_endpoint,userinput):
    """Processes patient id, validates against the patient list, returns the next Q if all goes okay"""
    global patient_list
    patient_id = userinput.strip()
    if not patient_id.isdigit() or int(patient_id) not in patient_list:
        return "Please enter a valid six digit patient ID",0,{}
    else:
        return "Please describe the symptoms that the patient is exhibiting",1,patient_id
    
def question_1(model_endpoint,userinput):
    """Processes symptoms, passes through spell check, and NER model if there are no 
    misspelled words. """
    global orig_sent
    global d
    global options
    orig_sent = userinput.strip()
    d = spellcheck2(preprocess(userinput),symspell1)
    if len(d) == 0:
        symptoms = extraction(userinput,ner1)
        return "Please enter a valid severity level -- (E1,E2,E3,E4)",2,symptoms
    else:
        response,options = numbered_print(d.iloc[0])
        return response,1.1,{}
 
def spelling_state_1(model_endpoint,userinput):
    """Processes spelling mistakes and returns the next Q"""
    global orig_sent
    global d
    global options
    #Validate user response
    if not userinput.isdigit() or (int(userinput) not in options):
        return "Please enter a valid selection",1.1,{}
    #Replace the word, drop the row from the database
    else:
        orig_sent = replace_word(d.iloc[0],userinput,orig_sent)
        d.drop(d.index[0],inplace = True)
    #If there are more words, repeat the process
    if len(d)>=1:
        response,options = numbered_print(d.iloc[0])
        return response,1.1,{}

    else:
        symptoms = extraction(orig_sent,ner1)
        return "Please enter a valid severity level -- (E1,E2,E3,E4)",2,symptoms
	

def question_2(model_endpoint,userinput):
    """Processes severity level, returns next Q"""
    if userinput.strip().lower() not in ['e1','e2','e3','e4']:
        return "Please enter a valid severity level",2,{}
    else:
        severity_level = userinput.strip()
        return "Is the patient oriented --> (Yes, No, Somewhat, Unknown)",3,severity_level

def question_3(model_endpoint,userinput):
    """Processes patient orientation, returns next Q"""
    if userinput.strip().lower() not in ['yes','no','somewhat','unknown']:
        return "Please enter a valid response",3,{}
    else:
        oriented = userinput.strip()
        return "Is the patient able to understand you --> (Yes, No, Somewhat, Unknown)",4,oriented

def question_4(model_endpoint,userinput):
    """Processes patient understanding"""
    if userinput.strip().lower() not in ['yes','no','somewhat','unknown']:
        return "Please enter a valid response",4,{}
    else:
        patient_understand = userinput.strip()
        return "Are you able to understand the patient --> (Yes, No, Somewhat, Unknown)",5,patient_understand

def question_5(model_endpoint,userinput):
    """Processes user understanding patient and return the next Q"""
    if userinput.strip().lower() not in ['yes','no','somewhat','unknown']:
        return "Please enter a valid response",5,{}
    else:
        user_understand_patient = userinput.strip()
        return "When were the symptoms noticed? \nHow long has the patient been experiencing symptoms",6,user_understand_patient

def question_6(model_endpoint,userinput):
    how_long_symptoms = userinput.strip()
    return "Please describe the course. \nHow have the symptoms evolved?",7,how_long_symptoms


def question_7(model_endpoint,userinput):
    symptoms_evolution = userinput.strip()
    return "Please describe the precipitating factors. \nWhat was the patient doing when the symptoms arose?",8,symptoms_evolution

def question_8(model_endpoint,userinput):
    precipitating_factors = userinput.strip()
    return "Please describe the associated features",9,precipitating_factors

def question_9(model_endpoint,userinput):
    """Processes associated features, pass through spell check"""
    global orig_sent
    orig_sent = userinput.strip()
    global d
    global options
    d = spellcheck2(preprocess(userinput),symspell1)
    if len(d) == 0:
        associated_features = extraction(userinput,ner1)
        return "Please describe any previous episodes",10,associated_features
    else:
        response,options  = numbered_print(d.iloc[0])
        return response,9.1,{}

def spelling_state_2(model_endpoint,userinput):
    """repeat spellcheck for all words, pass through NER model"""
    global orig_sent
    global d
    global options
    if not userinput.isdigit() or (int(userinput) not in options):
        return "Please enter a valid selection.",9.1,{}
    else:
        orig_sent = replace_word(d.iloc[0],userinput,orig_sent)
        d.drop(d.index[0],inplace = True)
    if len(d)>=1:
        response,options  = numbered_print(d.iloc[0])
        return response,9.1,{}

    else:
        associated_features = extraction(orig_sent,ner1)
        return "Please describe any previous episodes",10,associated_features

def question_10(model_endpoint,userinput):
    previous_episodes = userinput.strip()
    return "Please list the patient's medical history. \nInclude medical conditions and stroke/risk factors",11,previous_episodes

def question_11(model_endpoint,userinput):
    """Processes medical history, passes through spellcheck"""
    global orig_sent
    orig_sent = userinput.strip()
    global d
    global options
    d = spellcheck2(preprocess(userinput),symspell1)
    if len(d) == 0:
        medical_history = extraction(userinput,ner1)
        return "Please list any allergies the patient may have",12,medical_history
    else:
        response,options = numbered_print(d.iloc[0])
        return response,11.1,{}

def spelling_state_3(model_endpoint,userinput):
    """Processes spellcheck for each word, passes through NER model"""
    global orig_sent
    global d
    global options
    if not userinput.isdigit() or (int(userinput) not in options):
        return "Please enter a valid selection",11.1,{}
    else:
        orig_sent = replace_word(d.iloc[0],userinput,orig_sent)
        d.drop(d.index[0],inplace = True)
    if len(d)>=1:
        response,options = numbered_print(d.iloc[0])
        return response,11.1,{}

    else:
        medical_history = extraction(orig_sent,ner1)
        return "Please list any allergies the patient may have",12,medical_history

def question_12(model_endpoint,userinput):
    allergies = userinput.strip()
    return "Please describe the patient's drug history. \nPrescription and over the counter",13,allergies

def question_13(model_endpoint,userinput):
    """Process drug history, pass through spell check"""
    global orig_sent
    orig_sent = userinput.strip()
    global d
    global options
    d = spellcheck2(preprocess(userinput),symspell2)
    if len(d) == 0:
        drug_history = extraction(userinput,ner2)
        return "Does the patient have a family history of stroke --> (Yes, No, Unknown)",14,drug_history
    else:
        response,options = numbered_print(d.iloc[0])
        return response,13.1,{}

def spelling_state_4(model_endpoint,userinput):
    """Pass each word through spell check, offer suggestions, pass through NER"""
    global orig_sent
    global d
    global options
    if not userinput.isdigit() or (int(userinput) not in options):
        return "Please enter a valid selection.",13.1,{}
    else:
        orig_sent = replace_word(d.iloc[0],userinput,orig_sent)
        d.drop(d.index[0],inplace = True)
    if len(d)>=1:
        response,options = numbered_print(d.iloc[0])
        return response,13.1,{}
    else:
        drug_history = extraction(orig_sent,ner2)
        return "Does the patient have a family history of stroke",14,drug_history


def question_14(model_endpoint,userinput):
    if userinput.strip().lower() not in ['yes','no','unknown']:
    	return "Please enter a valid response",14,{}
    else:
    	family_history = userinput.strip()
    	return "Please describe the patient's social history",15,family_history

def question_15(model_endpoint,userinput):
    social_history = userinput.strip()
    return "Thank you for your input",16,social_history


def end(model_endpoint, userinput):
    """restart app after completing interaction"""
    return "restarting app...\n\n" + get_opening_message(), 0, {}
