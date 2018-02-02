from flask import Blueprint

api = Blueprint('api', __name__)

from app.api import blogs, authentication, users, comments, labels, favourites, responses
