import os
from flask import Flask,Blueprint
from src.config.config import Config
from dotenv import load_dotenv
from src.routes import api
from flask_cors import CORS
app = Flask(__name__)
CORS(app,supports_credentials=True)

load_dotenv()
config = Config().dev_config
app.env = config.ENV
app.secret_key=os.environ.get("SECRET_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
print(os.environ.get("SECRET_KEY"))

app.register_blueprint(api, url_prefix="/api")