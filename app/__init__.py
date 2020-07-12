from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from flask_mail import Mail

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, 'static/img')

app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)
mail = Mail(app)

from app.routes import *
from app.reset_route import *
from app.anonymous_routes import *
from app.errors import *