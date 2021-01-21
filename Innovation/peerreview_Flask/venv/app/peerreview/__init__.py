from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 

app = Flask(__name__)

#user authentication
login_manager = LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'

#db
app.config['SECRET_KEY'] = "e20f56f3b5ca0eb6f2d0c36f9c1d083d"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:root@localhost:3306/innovation"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from peerreview import routes