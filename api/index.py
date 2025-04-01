from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Flask on Vercel!"

# Vercel requires this for serverless functions
def handler(event, context):
    return app(event, context)
