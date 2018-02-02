from flask import Blueprint

api = Blueprint('api', __name__)

from app.api import blogs, authentication, comments, labels, favourites, responses
