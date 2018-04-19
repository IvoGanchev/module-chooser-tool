from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


mail = Mail()
app = Flask(__name__)

bcrypt = Bcrypt(app)
app.config.from_object('config')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'testerinomaximino@gmail.com'
app.config['MAIL_PASSWORD'] = 'thisisatest'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail.init_app(app)

db = SQLAlchemy(app)

from app import views, models
