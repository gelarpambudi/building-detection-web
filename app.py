from flask import Flask
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/uploads/'
app.config['RESULTS_FOLDER'] = './static/results/'
app.config['ALLOWED_EXTENSIONS'] = set(['tiff', 'tif', 'TIF', 'TIFF'])
app.config['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY')
app.config['GOOGLE_API_BASE_URL'] = 'https://maps.googleapis.com'
app.config['GOOGLE_GEOCODE_API_PATH'] = '/maps/api/geocode/json'
app.secret_key = "this_is_your_key"
