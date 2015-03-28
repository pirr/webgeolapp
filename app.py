from flask import Flask, render_template, request, url_for, flash
from wtforms import Form, TextField, PasswordField, validators
import ipdb

app = Flask(__name__)

users = 'one'
name = None
passwd = None

@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('index.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    name = request.form['name']
    passwd = request.form['pass']
    print(name, passwd)
    # if name == users:
    #     return render_template('login.html')
    # else:
    #     flash("Введите правильный логин и пароль")
    # return render_template('login.html')


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