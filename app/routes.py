from flask import Blueprint
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

bp = Blueprint('main', __name__)