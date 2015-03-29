from flask import Flask, render_template, request, flash, session
import ipdb

app = Flask(__name__)

users = [('one','pass1'),('two','pass2')]

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        passwd = request.form['passwd']
        if (name, passwd) in users:
            session['username'] = name
            return render_template('login.html', name=name)
        else:
            flash("Введите верный логин и пароль")
            return render_template('index.html')

@app.route('/documents/')
def documents():
    if 'username' in session:
        return render_template('documents.html')
    else:
        flash("Введите логин и пароль")
        return render_template('index.html')

@app.route('/objects/')
def objs():
    if 'username' in session:
        return render_template('objects.html')
    else:
        flash("Введите логин и пароль")
        return render_template('index.html')

@app.route('/logout')
def clear():
    session.clear()
    return render_template('index.html')

if __name__ == '__main__':
    app.secret_key = "bacon"
    app.debug = True
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(
            debug=True, 
            host="0.0.0.0"
            )