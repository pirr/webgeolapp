from flask import Flask, render_template, request, flash, session
from wtforms import Form, TextField, PasswordField, validators
import ipdb

app = Flask(__name__)

user = ('one','pass')

@app.route('/')
def main():
    return render_template('index.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        passwd = request.form['passwd']
        if (name, passwd) == user:
            session['username'] = name
            return render_template('login.html', name=name)
        else:
            flash("Введите правильный логин и пароль")
            return render_template('index.html')

@app.route('/documents/')
def documents():
    if 'username' in session:
        return render_template('documents.html')
    else:
        flash("Введите правильный логин и пароль")
        return render_template('index.html')


@app.route('/objects/')
def _objs():
    return render_template('objects.html')

@app.route('/logout')
def clear():
    session.clear()
    return render_template('index.html')

if __name__ == '__main__':
    app.secret_key = "bacon"
    app.debug = True
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)