from flask import Flask, request, jsonify
from lib.image_processing.preprocess import *
import urllib.request
import uuid 
import sqlite3
import pickle

conn = sqlite3.connect('db/reciepts.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS receipts (
    id integer PRIMARY KEY,
    img text NOT NULL,
    lined_img text NOT NULL,
    line_word_letter text NOT NULL,
    uid text NOT NULL UNIQUE
    );'''
)

class ProcessedImage:
    def __init__(self, img_path='', img=[], lined_img=[], line_word_letter=[], uid = ''):
        self.img_path = img_path
        self.img = img
        self.lined_img = lined_img
        self.line_word_letter = line_word_letter
        self.uid = uid

    def upload_image(self, img_path):
        self.img = load_image(img_path)
        img = black_white(self.img)
        img = fix_skew(img)
        img = noise_reduction(img)
        self.lined_img = thin_skeleton(img) # Need to update code to actually do this
        self.line_word_letter = segmentation(self.lined_img)
        self.uid = 'RCT-' + str(uuid.uuid4())
        return self.img, self.lined_img, self.line_word_letter

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/upload_image", methods=["POST"])
def process_image():
    # Read the image via file.stream
    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        # img = cv2.imread(file)
        # print(img)
        # print(file)
        myImage = ProcessedImage()
        myImage.upload_image(file)
        conn = sqlite3.connect('db/reciepts.db')
        conn.execute('''
        INSERT INTO receipts (img, lined_img, line_word_letter, uid)
        VALUES (?, ?, ?, ?);
        ''', (pickle.dumps(myImage.img), pickle.dumps(myImage.lined_img), pickle.dumps(myImage.line_word_letter), myImage.uid))
        conn.commit()
        resp = jsonify({'msg': 'receipt_process - success', 'id': myImage.uid})
        resp.status_code = 201
        return resp

@app.route("/api/check_database", methods=["GET"])
def create_database():
    if (conn):
    # Carry out normal procedure
        msg = "Connection successful"
    else:
    # Terminate
        msg = "Connection unsuccessful"
    resp = jsonify({'msg': msg})
    resp.status_code = 201
    return resp


if __name__ == "__main__":
    app.run(debug=True)