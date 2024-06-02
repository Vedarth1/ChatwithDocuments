from flask import Blueprint
from src.controllers.chat import chats

api=Blueprint('api',__name__)

api.register_blueprint(chats)