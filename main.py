import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from flask import Flask, request, jsonify
from cloudinary.uploader import upload
from flask_cors import CORS



app = Flask(__name__)
CORS(app)

# Route for uploading event banner
