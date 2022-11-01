from flask import Flask, render_template, request, redirect
import pickle 
import numpy as np
import smtplib
from flask_mysqldb import MySQL
import yaml
import sendgrid
from sendgrid.helpers.mail import *
# API KEY = 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

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
# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         model.save()
#         # Failure to return a redirect or render_template
#     else:
#         return render_template('index.html')

@app.route('/doctor')
def doctor():
    return render_template('doctor.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/community')
def community():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM blogs") #returns int of rows in the table
    if resultValue > 0:
        blogDetails = cur.fetchall() #all the names and emails would be stored
        return render_template('community.html', blogDetails = blogDetails )
    return render_template('community.html')

@app.route('/community/form', methods = ['GET', 'POST'])
def communityform():
    if request.method == 'POST':
        blogDetails = request.form
        title = blogDetails['title']
        content = blogDetails['content']
        cur = mysql.connection.cursor() #To execute query commands
        cur.execute("INSERT INTO blogs(title, content) VALUES(%s, %s)", (title, content))
        mysql.connection.commit() #to save changes in db
        cur.close()
        return redirect ('/community')
    return render_template('communityForm.html')


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
    predictText = "Greetings from Diadisc\n On the basis of the information provided by you , our predictor has calculated the risk of you getting diabetes. Rating on scale of 10 you have a rating of {}".format(output)
    if output>str(7) and data9 == str(1):
        content = "As you have suffered from covid earlier, you also have high chances of having Black Fungus as well. We suggest you to get an appointment with a doctor. Our appointment scheduler can help you get an appointment in your city."
    elif output > str(7) and data9 == str(0) :
        content = "We suggest you to get an appointment with a doctor. Our appointment scheduler can help you get an appointment in your city."
    else :
        content = "We suggest you to maintain your health. If in case you want to consult a doctor our appointment scheduler can help you get an appointment in your city."

    # SUBJECT = 'Reg diabetes prediction by Diadisc'
    # TEXT = predictText + "\n" + content + "For further reference visit our webpage " " team"
    # message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
    #server = smtplib.SMTP("smtp.gmail.com", 587)
    #server.starttls() # puts the connection to the SMTP server into TLS mode.
    #server.login("sairamnomula14@gmail.com", "password")
    #server.sendmail("sairamnomula14@gmail.com", email, message)

    sg = sendgrid.SendGridAPIClient('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')
    from_email = Email("diadisc@gmail.com")
    to_email = To("sairam.nomul00@gmail.com")
    SUBJECT = 'Reg diabetes prediction by Diadisc'
    # content = Content(predictText + "\n" + content)
    content = Content("Hello")
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
    
    if output>str(7) and data9 == str(1):
        result_web = "Thank you " + name + " for using our Diabetes predictor."
        result_web2 = "We predict that the chances of you having diabetes"
        result_web3 = "is {} on the scale of 10.".format(output)
        result_web4 = "As you have suffered from covid earlier, you also have"
        result_web5 = "high chances of having Black Fungus as well."
        result_web6 = "We suggest you to consult a doctor."
    elif output>str(7) and data9 == str(0):
        result_web = "Thank you " + name + " for using our Diabetes predictor."
        result_web2 = "We predict that the chances of you having diabetes"
        result_web3 = "is {} on the scale of 10.".format(output)
        result_web4 = "We suggest you to consult a doctor."
        result_web5 = ""
        result_web6 = ""
    else :
        result_web = "Thank you " + name + " for using our Diabetes predictor."
        result_web2 = "We predict that the chances of you having diabetes"
        result_web3 = "is {} on the scale of 10.".format(output)
        result_web4 = ""
        result_web5 = ""
        result_web6 = ""

    return render_template('result.html', output = result_web,output2 = result_web2, output3 = result_web3, output4 = result_web4, output5 = result_web5, output6 = result_web6)

if __name__ == "__main__":
    app.run(debug = True, port=8000)
