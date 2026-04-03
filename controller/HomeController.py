from flask import render_template

def home():
    return render_template('views/home.html')
