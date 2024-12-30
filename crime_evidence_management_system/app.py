from flask import Flask, request,render_template,redirect,url_for,jsonify

import pandas as pd
import random
from pymongo import MongoClient
from flask_mail import Mail, Message

app = Flask(__name__)

host = "ocdb.app"
port = 5050
database = "db_42wrhgtke" # your database
username = "user_42wrhgtke" # your username
password = "p42wrhgtke" # your password
 
connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"
my_client = MongoClient(connection_string)
my_db = my_client[database]
aut_login = my_db["aut_login"]
unaut_login=my_db["unaut_login"]
collection = my_db['cases']

"""# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'swaroopqis@gmail.com'
app.config['MAIL_PASSWORD'] = 'qihb sgty ysew ikes'
app.config['MAIL_DEFAULT_SENDER'] = 'swaroopedupulapati1@gmail.com'

mail = Mail(app)"""



@app.route('/',methods=['GET',"POST"])
def home():
    return render_template("index.html")

@app.route('/aut_login',methods=['GET',"POST"])
def aut_login_form():
    if request.method == 'POST':
        name=request.form["user_id"]
        password=request.form["password"]
        user_details=aut_login.find_one({'name': name ,"password": password})
        if user_details:
            return render_template("aut_login_sucess.html")       
        else:
            return render_template("aut_login.html", data = f"{name} has no account ")      
    else:
        return render_template('aut_login.html')


@app.route('/uaut_login',methods=['GET',"POST"])
def unaut_login_form():
    if request.method == 'POST':
        name=request.form["user_id"]
        password=request.form["password"]
        user_details=unaut_login.find_one({'name': name ,"password": password})
        if user_details:
            return render_template("un_aut_login_sucess.html")       
        else:
            return render_template("unaut_login.html", data = f"{name} has no account ")      
    else:
        return render_template('unaut_login.html')
    

@app.route('/autregister',methods=['GET',"POST"])
def aut_register():
    if request.method == 'POST':
        name=request.form["user_id"]
        password=request.form["password"]
        aut_login.insert_one({"name":name,"password":password})
        return render_template("aut_register.html", name = name)
    else:
        return render_template('aut_register.html')
@app.route('/unautregister',methods=['GET',"POST"])
def unaut_register():
    if request.method == 'POST':
        name=request.form["user_id"]
        password=request.form["password"]
        unaut_login.insert_one({"name":name,"password":password})
        return render_template("un_aut_register.html", name = name)
    else:
        return render_template('un_aut_register.html')

@app.route('/add_case',methods=['GET',"POST"])
def add_case():
    if request.method == 'POST':
        case_number = request.form.get('case_number')
        labels = request.form.getlist('label')
        data = request.form.getlist('data')

        # Combine labels and data into a dictionary
        details = {label: data[i] for i, label in enumerate(labels) if label and data[i]}
        
        if case_number and details:
            # Insert into MongoDB
            case_data = {
                'case_number': case_number,
                'details': details
            }
            collection.insert_one(case_data)
            return "<h1> case added succesfully</h1>"

    return render_template('add_case.html')




@app.route('/enter_case', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        case_number = request.form.get('case_number')

        # Fetch case details from MongoDB
        case = collection.find_one({'case_number': case_number})

        if case:
            return render_template('update.html', case=case)
        else:
            return "Case not found!", 404

    return render_template('case_no.html')


    
@app.route('/update_case', methods=['POST'])
def update_case():
    case_number = request.form.get('case_number')
    updated_details = request.form.get('details')

    # Find the previous data
    case = collection.find_one({'case_number': case_number})
    previous_details = case['details'] if case else {}

    # Update case in MongoDB
    if case_number and updated_details:
        updated_details = eval(updated_details)  # Convert string back to dict
        collection.update_one({'case_number': case_number}, {'$set': {'details': updated_details}})

        # Send email with previous and modified data
        send_email(case_number, previous_details, updated_details)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'failure'})

def send_email(case_number, previous_details, updated_details):
    message = Message(
        subject=f"Case Updated: {case_number}",
        recipients=['swaroopedupulapati1@gmail.com'],
    )

    # Email body with previous and updated data
    message.body = f"""
    Case Number: {case_number}

    Previous Details:
    {previous_details}

    Updated Details:
    {updated_details}
    """
    mail.send(message)


app.run(debug=True)