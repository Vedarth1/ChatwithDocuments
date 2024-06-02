import os
from flask import Flask,Blueprint
from src.config.config import Config
from dotenv import load_dotenv
from src.routes import api
app = Flask(__name__)

load_dotenv()
config = Config().dev_config
app.env = config.ENV
app.secret_key=os.environ.get("SECRET_KEY")
print(os.environ.get("SECRET_KEY"))

app.register_blueprint(api, url_prefix="/api")