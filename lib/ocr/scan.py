import pytesseract
import sqlite3
import pickle
from PIL import Image

conn = sqlite3.connect('./db/reciepts.db')
c = conn.cursor()

uid = 'RCT-4e06cc1d-14bb-42da-adb2-11204c063da4'

c.execute('SELECT line_word_letter FROM receipts WHERE uid = \'RCT-4e06cc1d-14bb-42da-adb2-11204c063da4\'')
rows = c.fetchall()[0]
line_word_letter = pickle.loads(rows[0])

Image.fromarray(line_word_letter[4][0]).show()