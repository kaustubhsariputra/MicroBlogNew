import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import requests
from flask_mail import Mail


uri = 'postgresql://rnxqvgimivpeis:d6ace147b3b71b962bbcc26f1e93672e24eac2772a4be154f97943bd005ffef7@ec2-54-90-211-192.compute-1.amazonaws.com:5432/d4b5unvngol1od'

app = Flask(__name__)
app.config['SECRET_KEY']= os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'log_in'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('email')
app.config['MAIL_PASSWORD'] = os.environ.get('password')
mail = Mail(app)


response = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={os.environ.get('newsapikey')}")
sports =  requests.get(f"https://newsapi.org/v2/top-headlines?country=in&category=sports&apiKey={os.environ.get('newsapikey')}")

from MicroBlog import routes