# compose_flask/app.py
from flask import Flask


from errors import register_errors
# from utils import generator_id
# from utils import get_current_date
# from utils import create_user
from models import db


# from flask_apispec import doc
# from models import Book

from config import *
import os

URI = 'postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}'.format(
    user=USER_DB,
    pw=PW,
    host=HOST,
    port=PORT,
    db=DB
)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
db.init_app(app)
register_errors(app)


from endpoints import api, JWTManager
app.register_blueprint(api)


jwt = JWTManager()
jwt.init_app(app)

from utils import get_user

@jwt.user_loader_callback_loader
def get_current_user(identity):
    return get_user(identification=identity)