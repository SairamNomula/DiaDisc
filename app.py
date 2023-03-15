from flask import Flask, render_template, request, redirect
import pickle 
import numpy as np
import smtplib
from flask_mysqldb import MySQL
import yaml
import sendgrid
from sendgrid.helpers.mail import *
import os
from dotenv import load_dotenv

load_dotenv()
PWD = os.getenv('PWD')
SENDGRID_API_KEY=os.getenv('SENDGRID_API_KEY')

#Initialize the flask App
app = Flask(__name__)

#configure db
db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app) 

model = pickle.load(open('model.pkl', 'rb'))

#default page of our web-app
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/doctor')
def doctor():
    return render_template('doctor.html')

@app.route('/form')
def form():
    return render_template('form.html')

#To use the predict button in our web-app
@app.route('/predict',methods=['POST'])
def predict():
    #For rendering results on HTML GUI
    name = request.form['name']
    email = request.form['email']
    # int_features = [float(x) for x in request.form.values()]
    #print(int_features)
    data8 = int(request.form['age'])
    data7 = float(request.form['fnc'])
    data9 = int(request.form['covid'])
    data1 = int(request.form['pregnancies'])
    data2 = int(request.form['glucose'])
    data3 = int(request.form['bp'])
    data4 = int(request.form['thick'])
    data5 = int(request.form['insulin'])
    data6 = float(request.form['bmi'])
    print(data9)
    print(type(data9))
    
    final_features = np.array([[data1, data2, data3, data4, data5, data6, data7, data8]])
    print(final_features)
    # final_features = [np.array(int_features)]
    prediction = model.predict_proba(final_features)
    print(prediction)
    output = '{0:.{1}f}'.format(10*prediction[0][1],2)
    predictText = "Hello from DiaDisc\n Our predictor assessed your probability of developing diabetes based on the information you supplied. You have a rating of {} on a scale of 10.".format(output)
    if output>str(7) and data9 == str(1):
        content = "You are more likely to get Black Fungus if you have previously suffered with covid. We recommend that you make an appointment with a doctor. Our appointment planner can assist you in obtaining an appointment in your city."
    elif output > str(7) and data9 == str(0) :
        content = "We recommend that you make an appointment with a doctor. Our appointment planner can assist you in obtaining an appointment in your city."
    else :
        content = "We advise you to take care of your health. If you need to see a doctor, our appointment calendar can help you find one in your area."

    SUBJECT = 'Regarding diabetes prediction by DiaDisc'
    TEXT = predictText + "\n" + content
    message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls() # puts the connection to the SMTP server into TLS mode.
    server.login("Diadictor@gmail.com", "zjyiqqmrkoznqarr")
    server.sendmail("Diadictor@gmail.com", email, message)
    # server.login("diadisc2223@gmail.com", PWD)
    # server.sendmail("diadisc2223@gmail.com", email, message)

    # sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
    # from_email = Email("diadisc2223@gmail.com")
    # to_email = To("sairam.nomul00@gmail.com")
    # SUBJECT = 'Reg diabetes prediction by Diadisc'
    # # content = Content(predictText + "\n" + content)
    # Content = content("Hello")
    # mail = Mail(from_email, to_email, subject, Content)
    # response = sg.client.mail.send.post(request_body=mail.get())
    # print(response.status_code)
    # print(response.body)
    # print(response.headers)
    
    if output>str(7) and data9 == str(1):
        result_web = "Thank you " + name + " for using DiaDisc."
        result_web2 = "We predict that the chances of you having diabetes"
        result_web3 = "is {} on the scale of 10.".format(output)
        result_web4 = ""
        result_web5 = "We recommend that you make an appointment with a doctor."
        result_web6 = "Our appointment planner can assist you in obtaining an appointment in your city."
    elif output>str(7) and data9 == str(0):
        result_web = "Thank you " + name + " for using DiaDisc."
        result_web2 = "We predict that the chances of you having diabetes"
        result_web3 = "is {} on the scale of 10.".format(output)
        result_web4 = "We recommend you to consult a doctor."
        result_web5 = ""
        result_web6 = ""
    else :
        result_web = "Thank you " + name + " for using DiaDisc."
        result_web2 = "We predict that the chances of you having diabetes"
        result_web3 = "is {} on the scale of 10.".format(output)
        result_web4 = ""
        result_web5 = ""
        result_web6 = ""

    return render_template('result.html', output = result_web,output2 = result_web2, output3 = result_web3, output4 = result_web4, output5 = result_web5, output6 = result_web6)

if __name__ == "__main__":
    app.run(debug = True, port=8000)
