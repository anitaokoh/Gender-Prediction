from flask import Flask, render_template, request
from oauth2client.service_account import ServiceAccountCredentials
from catboost import CatBoostClassifier
from sklearn.model_selection import GridSearchCV
from datetime import datetime
import gspread
import pandas as pd
import pickle

#function to get current time
def date_now():
    now = datetime.now()
    mydate = datetime.strftime(now , '%Y-%m-%d %H:%M:%S')
    return mydate

#reading the data
gender = pd.read_csv('data/gender.csv')
colour = list(gender['Favorite Color'].unique())
music = list(gender['Favorite Music Genre'].unique())
alcohol = list(gender['Favorite Beverage'].unique())
soft_drink = list(gender['Favorite Soft Drink'].unique())

#loading the saved model
with  open('gender_model.pkl', 'rb') as model:
    catboost_model = pickle.load(model)

# Connecting to google sheet api
scope = ['https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name('gender.json', scope)

client = gspread.authorize(creds)

details = client.open('Gender data').worksheet('gender_data')
pred = client.open('Gender data').worksheet('check_prediction')


# creating the flask app
app = Flask(__name__)


@app.route("/")
def home():
    return render_template('home.html', COLOUR = colour, MUSIC = music, ALCOHOL = alcohol, SOFT_DRINK = soft_drink)


@app.route("/result")
def result():
    answer = ['Yes', 'No']
    reveal = ['Female', 'Non-Binary', 'Male']
    data = dict(request.args)
    collect1 = [date_now()]
    collect1 += list(data.values())
    details.insert_row(collect1, 2)
    key = ['colour', 'music', 'alcohol', 'soft_drink']
    preference = list(map(data.get, key))
    print(preference)
    prediction = catboost_model.predict(preference)
    if prediction == 1.0:
        gender_reveal = 'Female'
    else:
        gender_reveal = 'Male'
    return render_template('result.html', ANSWER=answer, REVEAL=reveal, GENDER_REVEAL = gender_reveal)

@app.route("/end")
def end():
    final_data = dict(request.args)
    collect2 = [date_now()]
    collect2 += list(final_data.values())
    pred.insert_row(collect2, 2)
    return render_template('end.html')



if __name__ == '__main__':
    app.run(debug=True)
