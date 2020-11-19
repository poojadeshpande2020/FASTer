#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


ner1 = load_model('./spacy_model_symptoms_final')
ner2 = load_model('./spacy_model_drugs_final')


# In[3]:


with open('./spellchecker1','rb') as f_d:
    symspell1 = pickle.load(f_d)


# In[4]:


with open('./spellchecker2','rb') as f:
    symspell2 = pickle.load(f)


# # Chatbot functions

# In[5]:


#may be add more words like (patient,has,the, experiencing) Then ask for symptom suggestions. did you mean so and so.
sw = set(stopwords.words('english'))
remove_words = ['no','not']
add_words = ['patient','showing','experiencing']
new_sw = set([word for word in sw if word not in remove_words])
new_sw = new_sw.union(add_words)

def preprocess(user_input):
    """Returns a lower case sentence WITHOUT punctuation, digits and stop words"""
    #Remove punctuation
    #user_input = user_input.translate(str.maketrans('','',string.punctuation))
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
    

# In[7]:
def spellcheck2(user_input,spell_obj):
    global new_sw
    words = word_tokenize(user_input)
    data = []
    for word in words:
        row = []
        suggestions = spell_obj.lookup(word,verbosity = 2,max_edit_distance = 3,include_unknown = False,transfer_casing = False)
        if len(suggestions) == 0:
            continue
        
        for s in suggestions[:2]:
            correct = str(s).split(',')[0]
            if (correct in new_sw) or (correct == word):
                break
            if len(row) == 0:
                row.append(word)
            row.append(correct)
        if len(row) >0 and len(row)<3:
            row.append('')
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
    o = []
    final = "Please choose a number which describes the appropriate correction for the misspelled word : '{}'\n".format(row['misspelled'])
    for i,s in enumerate(row.index[1:]):
        if not pd.isnull(row[s]):
            o.append(i+1)
            final = final + str(i+1) + "." + row[s] + "\n"
    return final,o

def replace_word(row,userinput,orig_sent):
    misspelled = row['misspelled']
    correct_word = row[userinput]
    new_sent = orig_sent.replace(misspelled,correct_word,1)
    return new_sent

#Global variable
orig_sent = ""
d = pd.DataFrame()
options = []

# # Building the chatbot workflow
def get_opening_message():
    '''The variable starting message.'''
    return "Hi, my name is FASTer!\nI will be helping you with stroke patient intake.\nPlease enter the six digit patient ID" 

def patient_id(model_endpoint,userinput):
    patient_id = userinput.strip()
    if not patient_id.isdigit() or len(patient_id)!=6:
        return "Please enter a six digit patient ID",0,{}
    else:
        return "Please describe the symptoms that the patient is exhibiting",1,patient_id
    
def question_1(model_endpoint,userinput):
    global orig_sent
    orig_sent = userinput.strip()
    global d
    global options
    d = spellcheck2(preprocess(userinput),symspell1)
    if len(d) == 0:
        symptoms = extraction(userinput,ner1)
        return "Please enter a valid severity level -- (E1,E2,E3,E4)",2,symptoms
    else:
        response,options = numbered_print(d.iloc[0])
        return response,1.1,{}
 
def spelling_state_1(model_endpoint,userinput):
    global orig_sent
    global d
    global options
    if not userinput.isdigit() or (int(userinput) not in options):
        return "Please enter a valid selection",1.1,{}
    else:
        orig_sent = replace_word(d.iloc[0],userinput,orig_sent)
        d.drop(d.index[0],inplace = True)
    if len(d)>=1:
        response,options = numbered_print(d.iloc[0])
        return response,1.1,{}

    else:
        symptoms = extraction(orig_sent,ner1)
        return "Please enter a valid severity level -- (E1,E2,E3,E4)",2,symptoms
	

def question_2(model_endpoint,userinput):
    if userinput.strip().lower() not in ['e1','e2','e3','e4']:
        return "Please enter a valid severity level",2,{}
    else:
        severity_level = userinput.strip()
        return "Is the patient oriented --> (Yes, No, Somewhat, Unknown)",3,severity_level

def question_3(model_endpoint,userinput):
    if userinput.strip().lower() not in ['yes','no','somewhat','unknown']:
        return "Please enter a valid response",3,{}
    else:
        oriented = userinput.strip()
        return "Is the patient able to understand you --> (Yes, No, Somewhat, Unknown)",4,oriented

def question_4(model_endpoint,userinput):
    if userinput.strip().lower() not in ['yes','no','somewhat','unknown']:
        return "Please enter a valid response",4,{}
    else:
        patient_understand = userinput.strip()
        return "Are you able to understand the patient --> (Yes, No, Somewhat, Unknown)",5,patient_understand

def question_5(model_endpoint,userinput):
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
    return "restarting app...\n\n" + get_opening_message(), 0, {}


# #Create a form
# form = []
# #Q.1
# print("Bot: Hello, Please describe the symptoms that the patient is exhibiting.")
# userinput = input()

# #Spellchecking step
# list_suggestions = spellcheck(preprocess(userinput),symspell1)

# #Asking the user to select the appropriate correction for the misspelled word
# for word,recommendations in list_suggestions.items():
#     for instance in recommendations:
#         if instance in new_sw:
#             break
#         response = input("Bot: Did you mean {} instead of {} ".format(instance,word))
#         if response.lower() == 'yes':
#         #Replaces the word in the original sentence
#             userinput = userinput.replace(word,instance,1)
#             break
#         else:
#             continue            
# #Use NER to extract the symptoms and store it in a list
# list_symptoms = extraction(userinput,ner1)
# form.append(list_symptoms)
        
# #Q.2
# print("Bot: Please describe the severity of the patient, E1, E2, E3, E4")
# flag = True
# while (flag):
    
#     userinput = input()
#     if userinput.strip().lower() not in ['e1','e2','e3','e4']:
#         print("Bot: Please enter a valid severity level")
#     else:
#         flag = False
#         severity_level = userinput.strip()
# form.append(severity_level)
    
# #Q.3
# print("Bot: Is the patient oriented, (Yes, No. Somewhat, Unknown)")
# flag = True
# while (flag):
#     userinput = input()
#     if userinput.strip().lower() not in ['yes','no','somewhat','unknown']:
#         print("Bot: Please enter a valid response")
#     else:
#         flag =False
#         oriented = userinput.strip()
# form.append(oriented)
    
# #Q.4
# print("Bot: Is the patient able to understand you? (Yes, No, Somewhat, Unknown)")
# flag = True
# while (flag):
    
#     userinput = input()
#     if userinput.strip().lower() not in ['yes','no','somewhat','unknown']:
#         print("Bot: Please enter a valid response")
#     else:
#         flag = False
#         patient_understand = userinput.strip()
# form.append(patient_understand)

# #Q.5
# print("Bot: Are you able to understand the patient? (Yes, No, Somewhat, Unknown)")
# flag = True
# while(flag):
#     userinput = input()
#     if userinput.strip().lower() not in ['yes','no','somewhat','unknown']:
#         print("Bot: Please enter a valid response")
#     else:
#         flag = False
#         user_understand_patient = userinput.strip()
# form.append(user_understand_patient)
        
# #Q.6
# print("Bot: When were the symptoms first noticed - how long has the patient been experiencing symptoms?")
# userinput = input()
# how_long_symptoms = userinput.strip()
# form.append(how_long_symptoms)

# #Q.7
# print("Bot: Please describe the course - how have the symptoms evolved?")
# userinput = input()
# symptoms_evolution = userinput.strip()
# form.append(symptoms_evolution)

# #Q.8
# print("Bot: Please describe the precipitating factors - What was the patient doing when the symptoms arose?")
# userinput = input()
# precipitating_factors = userinput.strip()
# form.append(precipitating_factors)

# #Q.9
# print("Bot: Please describe the associated features")
# userinput = input()
# #Spellchecking step
# list_suggestions = spellcheck(preprocess(userinput),symspell1)
# #Asking the user to select the appropriate correction for the misspelled word
# for word,recommendations in list_suggestions.items():
#     for instance in recommendations:
            
#         if instance in new_sw:
#             break
#         response = input("Bot: Did you mean {} instead of {} ".format(instance,word))
#         if response.lower() == 'yes':
#         #Replaces the word in the original sentence
#             userinput = userinput.replace(word,instance,1)
#             break
#         else:
#             continue            
# #Use NER to extract the symptoms and store it in a list
# list_associated_features = extraction(userinput,ner1)
# form.append(list_associated_features)


# #Q.10
# print("Bot: Please describe any previous episodes")
# userinput  = input()
# previous_episodes = userinput.strip()
# form.append(previous_episodes)

# #Q.11
# print("Bot: Please list patient's past medical history - include medical conditions and stroke/risk factors")
# userinput = input()
# #Spellchecking step
# list_suggestions = spellcheck(preprocess(userinput),symspell1)
# #Asking the user to select the appropriate correction for the misspelled word
# for word,recommendations in list_suggestions.items():
#     for instance in recommendations:
            
#         if instance in new_sw:
#             break
#         response = input("Bot: Did you mean {} instead of {} ".format(instance,word))
#         if response.lower() == 'yes':
#         #Replaces the word in the original sentence
#             userinput = userinput.replace(word,instance,1)
#             break
#         else:
#             continue            
# #Use NER to extract the symptoms and store it in a list
# medical_history = extraction(userinput,ner1)
# form.append(medical_history)


# #Q.12
# print("Bot: Please list any allergies the patient may have")
# userinput = input()
# #Spellchecking step
# list_suggestions = spellcheck(preprocess(userinput),symspell1)
# #Asking the user to select the appropriate correction for the misspelled word
# for word,recommendations in list_suggestions.items():
#     for instance in recommendations:
            
#         if instance in new_sw:
#             break
#         response = input("Bot: Did you mean {} instead of {} ".format(instance,word))
#         if response.lower() == 'yes':
#         #Replaces the word in the original sentence
#             userinput = userinput.replace(word,instance,1)
#             break
#         else:
#             continue            
# #Use NER to extract the symptoms and store it in a list
# allergies = extraction(userinput,ner1)
# form.append(allergies)


# #Q.13
# print("Bot: Describe the patient's drug history, prescription and over the counter")
# userinput = input()
# #Spellchecking step
# list_suggestions = spellcheck(preprocess(userinput),symspell2)
# #Asking the user to select the appropriate correction for the misspelled word
# for word,recommendations in list_suggestions.items():
#     for instance in recommendations:
            
#         if instance in new_sw:
#             break
#         response = input("Bot: Did you mean {} instead of {} ".format(instance,word))
#         if response.lower() == 'yes':
#         #Replaces the word in the original sentence
#             userinput = userinput.replace(word,instance,1)
#             break
#         else:
#             continue            
# #Use NER to extract the symptoms and store it in a list
# drug_history = extraction(userinput,ner2)
# form.append(drug_history)



# #Q.14
# print("Bot: Does the patient have a family history of stroke - (Yes, No, Unknown)")
# flag = True
# while (flag):
#     userinput = input()
#     if userinput.strip().lower() not in ['yes','no','unknown']:
#         print("Bot: Please enter a valid response")
    
#     else:
#         flag = False
#         family_history = userinput.strip()
# form.append(family_history)
        
# #Q.15
# print("Bot: Describe the patient's social history")
# userinput = input()
# social_history = userinput.strip()  
# form.append(social_history)


# In[11]:


# pd.DataFrame({'Info':form},index = ['symptoms','severity_level','patient_oriented','patient_understand','user_understand_patient',
#                                    'how_long_symptoms','symptoms_evolved','precipitating_factors','associated_features',
#                                    'previous_episodes','medical_history','allergies','drug_history','family_history','social_history'])


# # Completed
# 
# 1. Included terms in the training data for NER-- garbled speech, delayed locomotion, shortness of breath, anxiety, reduced consciousness, locomotive dependency.
# 2. Detected all symptoms mentioned in https://my.clevelandclinic.org/health/articles/13490-stroke-glossary,
# Unable to detect 'high/low systolic blood pressure' and 'transient ischemic attack', but can detect 'TIA'.
# 3. Changed the first question to "What symptoms is the patient exhibiting" to avoid accounting for scenarios that may include symptom name preceded by 'no' or 'not'.
# 4. Include 'afebrile' in the spellcheck dictionary.
# 5. Commas are now at the right place. The symptoms are extracted based on occurrences of B_Disease and I_Disease.
# 6. Added code to not ask spelling suggestions for stopword list.
# 
# 
# 

# # Things to do 
# 
# 
# 
# 1. Include 'transient ischemic attack', 'shortness of breath', COPD.
# 2. Think about what to do for allergies.
# 3. Increase drug name spacy model accuracy.
# 4. Ask the user to verify the symptoms.
# 5. Include user id login information.
# 6. Create functions for each question.
# 7. Patient ID?
# 8. SPellcheck only two questions
# 9. If length of symptoms detected is zero, then ask the user if he/she wants to enter any symptoms. THis can cover for weird user responses like "I want chicken biryani"
# 
# 
# 
# 

# # Test cases for entity recognition

# In[6]:


# ## FAIL. Does not detect drug names since the training data doesn't have any drug names at the moment
# doc = ner2("rufinamide and clonazepam")
# displacy.render(doc,jupyter=True, style = "ent")


# In[5]:


#Pass
# doc = ner1("Bell's Palsy and Diabetes")
# displacy.render(doc,jupyter=True, style = "ent")


# In[3]:


# #Pass
# doc = ner1("epilepsy and COPD")
# displacy.render(doc,jupyter=True, style = "ent")


# In[4]:


# #FAIL - doesnot detect garbled speech 
# doc = ner1("The patient has garbled speech and possible indication of dysarthria")
# displacy.render(doc,jupyter=True, style = "ent")

