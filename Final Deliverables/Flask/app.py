from __future__ import division, print_function
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image 
from tensorflow.keras.models import load_model
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import mysql.connector

global graph
#graph=tf.get_default_graph()
# Define a flask app
app = Flask(__name__)
model = load_model('natur1.h5')


print('Model loaded. Check http://127.0.0.1:5000/')



conn=mysql.connector.connect(host="localhost", user="root", password="", database="login")
cursor=conn.cursor()


@app.route('/')  # route to display the home page
def home():
    return render_template('index.html')  # rendering the home page


@app.route('/index', methods=['GET','POST'])
def index():
    # Main page
    return render_template('digital.html')

@app.route('/login')
def login():  # put application's code here
    return render_template('login.html')


@app.route('/register')
def register():  # put application's code here
    return render_template('register.html')


@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE'{}' AND `password` LIKE '{}'""".format(email, password))
    users = cursor.fetchall()

    if len(users) > 0:
        return render_template('digital.html')
    else:
        return render_template('login.html', prediction_text="1")


@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute(
        """INSERT INTO `users`(`id`, `name`, `email`, `password`) VALUES (NULL,'{}','{}','{}')""".format(name, email,
                                                                                                         password))
    conn.commit()
    return render_template('login.html', prediction_text="0")


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['image']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)
        img = image.load_img(file_path, target_size=(64,64))
        
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        
        #with graph.as_default():
        preds = np.argmax(model.predict(x))
        found = ["Bird- Antbird - Large passerine bird family , subtropical and tropical Central and South America, from Mexico to Argentina",
                 "Bird- Peacock - The blue peacock lives in India and Sri Lanka, ",
                 "Bird- Wild Turkey -  Forest floors, but can also be found in grasslands and swamps ",
                 "Animal- Gatto - Continental Europe, southwestern Asia, the savannah regions of Africa and as a pet.",
                 "Animal- Mucca - India, in east Africa, in northern Europe, and in South America",
                 "Animal- Pecora -  The Arctic circle as far south as Patagonia",
                 "Flower- Rose - Most species are native to Asia, with smaller numbers native to Europe, North America, and northwestern Africa",
                 "Flower- Sunflower - Indo-gangetic plains of Punjab, Haryana and UP in spring and Bihar, Odisha, West Bengal ",
                 "Flower- Tulip - Himachal Pradesh and hilly areas of Jammu and Kashmir "]
        print(preds)
        text = found[preds]
        return text

if __name__ == '__main__':
    app.run(threaded = False)

