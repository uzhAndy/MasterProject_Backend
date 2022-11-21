from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO
from flask import Flask

app = Flask(__name__)

db = SQLAlchemy()

jwt = JWTManager()

cors = CORS()

socket_io = SocketIO()


