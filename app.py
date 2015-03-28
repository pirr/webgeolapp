from flask import Flask, render_template, request, url_for, flash, redirect, session
from wtforms import Form, TextField, PasswordField, validators
import ipdb

app = Flask(__name__)
app.secret_key = "bacon"

user = ('one','pass')
name = None
passwd = None

@app.route('/')
def main():
    return render_template('index.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if (request.form['name'], request.form['passwd']) == user:
            session['name'] = name
            print(session['name'])
            return render_template('login.html')

        else:
            flash("Введите правильный логин и пароль")
            return render_template('index.html')


@app.route('/documents/')
def documents():
    return render_template('documents.html')

@app.route('/objects/')
def objs():
    return render_template('objects.html')

if __name__ == '__main__':
    app.debug = True
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)