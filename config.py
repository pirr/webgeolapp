from app import app
import os


SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
CSRF_ENABLED = True
app.secret_key = "bacon"
export DATABASE_URL = "mysql+pymysql://root:fpVGdd87S0UjeoEOrAA7@127.0.0.1:3306/geol_objects"


