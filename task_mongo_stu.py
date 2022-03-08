# -*- coding: utf-8 -*-
"""Task_Mongo_Stu.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1p08abjQx-Y6dTYR7H2bKF6WNz-xyM9SP
"""

import json
import pymongo
from pymongo import *
import numpy as np

# Creating Mongo Client

link = pymongo.MongoClient("mongodb://kkr016:<password!~kkr@1213>@kkr016-shard-00-00.vrrci.mongodb.net:27017,kkr016-shard-00-01.vrrci.mongodb.net:27017,kkr016-shard-00-02.vrrci.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-k1j4zb-shard-0&authSource=admin&retryWrites=true&w=majority")

print("List of Data Base:\n")
u=link.list_database_names()
for i in u:
  print(i)

#Creating Data Base And Collection

database_1 = link["student_database"]
col_1 = database_1["collections"]
rec_1 = col_1["collections"]

#Load JSon File

dic=[]
with open(r"/content/students.json") as s:
    for j in s:
        z = json.loads(j)
        dic.append(z)

#insert Collection

print("Record and Collection Updated")

rec_1.insert_many(dic)

import pandas as pd
df_1 = pd.DataFrame(dic)
df_1

name=[]
score1=[]
score2=[]
score3=[]

for i in range(len(dic)):
  name.append(dic[i]['name'])
  score1.append(dic[i]['scores'][0]['score'])
  score2.append(dic[i]['scores'][1]['score'])
  score3.append(dic[i]['scores'][2]['score'])

#For User Simplicity Scores Column is Covereted into Seprate Collection

res = zip(name,score1,score2,score3)
df_2=pd.DataFrame(res, columns=['name','exam_score', 'quiz_score', 'homework_score'])
df_2

#Function for Exporting Data Frame Into MongoDB

def exportMongo(data):
  data.reset_index(drop=True, inplace=True)
  data_dict = data.to_dict("records")
  return data_dict

#Converting Scores Column into Seprate Column for User Simplicity

col_2 = database_1["student_scores"]
rec_2 = col_2["scores"]
rec_2.insert_many(exportMongo(df_2))

for i in rec_2.find({},{'_id':0,'index':0}):
  print(i)

# Query_1

# Find the student name who scored maximum scores in all (exam, quiz and homework)?

print("\nMaximum Mark in Exam Type is :\n")
t = rec_2.find_one( sort = [ ( "exam_score" , -1 ) ] )
print(t["name"])

print("\nMaximum Mark in Quiz Type is :\n")
t = rec_2.find_one( sort = [ ( 'quiz_score' , -1 ) ] )
print(t["name"])

print("\nMaximum Mark in Homework Type is :\n")
t = rec_2.find_one( sort = [ ( 'homework_score' , -1 ) ] )
print(t["name"])

# Query_2

# Find students who scored below average in the exam and pass mark is 40%?

avgEx=df_2["exam_score"].mean()
pasMark=40

# Here 100 is the 100% of Marks

p=[]
for i in rec_2.find({"$and":[{"exam_score":{"$lt":avgEx}},{"exam_score":{"$gt":pasMark}}]},{'_id':0,"name":1}):
  p.append(i)

print("\nStudents Who Scored Below Average in the Exam and Pass Mark is Shown using Data Frame")
df_A=pd.DataFrame(p)
df_A

# Query_3

#  Find students who scored below pass mark and assigned them as fail, and above pass mark as pass in all the categories.

df_3=df_2
t1=[]
t2=[]
t3=[]

t1 = np.where((df_2['exam_score'] > pasMark), "Pass", "Fail")
df_3.insert(loc = 2,
          column = 'exam_grade',
          value = t1)

t2 = np.where((df_2['quiz_score'] > pasMark), "Pass", "Fail")
df_3.insert(loc = 4,
          column = 'quiz_grade',
          value = t2)

t3 = np.where((df_2['homework_score'] > pasMark), "Pass", "Fail")
df_3.insert(loc = 6,
          column = 'homework_grade',
          value = t3)

df_3

#df_3["P/F"] = np.where((df_2['exam_score'] > pasMark) & (df_2['quiz_score'] > pasMark) & (df_2['homework_score'] > pasMark), "Pass", "Fail")

#Pass/Fail Doest reflect in MOngo DB

# Query_4

# Find the total and average of the exam, quiz and homework and store them in a separate collection.

df_2['total'] = (df_2['exam_score']+df_2['quiz_score']+df_2['homework_score'])
df_2['mean'] = ((df_2['exam_score']+df_2['quiz_score']+df_2['homework_score'])/3)

df_4=df_2

col_4 = database_1["total_mean"]
rec_4 = col_4["total_mean"]
rec_4.insert_many(exportMongo(df_4))

print("Total and Average of The Exam, Quiz and Homework \nStore Them in A Aeparate Collection\n")
for i in rec_4.find({},{'_id':0,"name":1,"total":1,"mean":1}):
  print(i)

# Query_5

#  Create a new collection which consists of students who scored below average and above 40% in all the categories.

emean=df_2["exam_score"].mean()
qmean=df_2["quiz_score"].mean()
hmean=df_2["homework_score"].mean()
x=[]
y=[]
z=[]
pasMark=40
for i in rec_4.find( { "$and": [ { "exam_score": { "$gt" : pasMark } },{ "exam_score": { "$lt" : emean } } ] }, {'_id':0,"quiz_score":0,"homework_score":0}):
  x.append(i)

for i in rec_4.find( { "$and": [ { "quiz_score": { "$gt" : pasMark } },{ "quiz_score": { "$lt" : qmean } } ] }, {'_id':0,"exam_score":0,"homework_score":0}):
  y.append(i)

for i in rec_4.find( { "$and": [ { "homework_score": { "$gt" : pasMark } },{ "homework_score": { "$lt" : hmean } } ] }, {'_id':0,"exam_score":0,"quiz_score":0}):
  z.append(i)

df_5=pd.DataFrame(x)

df_6=pd.DataFrame(y)

df_7=pd.DataFrame(z)

# Create a New Collection Having Single Type of Score

col_5 = database_1["exam_score"]
rec_5 = col_5["exam_score"]
rec_5.insert_many(exportMongo(df_5))

col_6 = database_1["quiz_score"]
rec_6 = col_6["quiz_score"]
rec_6.insert_many(exportMongo(df_6))

col_7 = database_1["homework_score"]
rec_7 = col_7["homework_score"]
rec_7.insert_many(exportMongo(df_7))

print("Students Who Scored Below Average {} and Above 40% in Exam Type\n".format(emean))
for i in rec_5.find( { }, {'_id':0,"name":1,"exam_score":1} ):
  print(i)

print("Students Who Scored Below Average {} and Above 40% in Quiz Type\n".format(qmean))
for i in rec_6.find( { }, {'_id':0,"name":1,"quiz_score":1} ):
  print(i)

print("Students Who Scored Below Average {} and Above 40% in Homework Type\n".format(hmean))
for i in rec_7.find( { }, {'_id':0,"name":1,"homework_score":1} ):
  print(i)

# Over Combination Above Query
zz=[]
for i in rec_4.find( { "$and": [ { "$and": [ { "$and": [ { "homework_score": { "$gt" : pasMark } },{ "homework_score": { "$lt" : hmean } } ] }, 
                               { "$and": [ { "quiz_score": { "$gt" : pasMark } },{ "quiz_score": { "$lt" : qmean } } ] } ] }, 
                                { "$and": [ { "exam_score": { "$gt" : pasMark } },{ "exam_score": { "$lt" : emean } } ] } ] }, {'_id':0 }):
  zz.append(i)

df_8=pd.DataFrame(z)

col_8 = database_1["Overall_constraints"]
rec_8 = col_8["homework_score"]
rec_8.insert_many(exportMongo(df_8))

# Query_6

# Create a new collection which consists of students who scored below the fail mark in all the categories.

failMark=39.9999
col_9 = database_1["non_passed_stu"]
rec_9 = col_9["non_passed_stu"]
t=[]

for i in rec_2.find( { "$or": [ { "$or": [ { "homework_score": { "$lt" : failMark } }, { "quiz_score": { "$lt" : failMark } } ] },
                                { "quiz_score": { "$lt" : failMark } } ] }, {'_id':0 }):
  t.append(i)

df_9=pd.DataFrame(t)
rec_9.insert_many(exportMongo(df_9))

print("Students Who Scored Below The Fail Mark in All The Categories\n")
for i in rec_9.find( { }, {'_id':0} ):
  print(i)

#Query 7

#Create a new collection which consists of students who scored above pass mark in all the categories.

col_10 = database_1["passed_stu"]
rec_10 = col_10["passed_stu"]
t=[]

for i in rec_2.find( { "$and": [ { "$and": [ { "homework_score": { "$gt" : pasMark } }, { "quiz_score": { "$gt" : pasMark } } ] },
                                { "quiz_score": { "$gt" : pasMark } } ] }, {'_id':0 }):
  t.append(i)

df_10=pd.DataFrame(t)
rec_10.insert_many(exportMongo(df_10))

print("Students Who Scored Above The Pass Mark in All The Categories\n")
for i in rec_10.find( { }, {'_id':0} ):
  print(i)