from flask import Flask, render_template, request, session
import ipdb

app = Flask(__name__)

users = [('one','pass1'),('two','pass2')]

@app.route('/')
def main():
    return render_template('index.html', user=session.get('user'))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if (data['user'], data['password']) in users:
        session['user'] = data['user']
        return 'ok'
    else:
        return 'Err'

@app.route('/documents')
def documents():
    if 'username' in session:
        return render_template('documents.html')
    else:
        flash("Введите логин и пароль")
        return render_template('index.html')

@app.route('/objects')
def objs():
    if 'username' in session:
        return render_template('objects.html')
    else:
        flash("Введите логин и пароль")
        return render_template('index.html')
    
@app.route('/logout', methods=['POST'])
def clear():
    session.clear()
    return 'Ok'

if __name__ == '__main__':
    app.secret_key = "bacon"
    app.debug = True
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(
            debug=True, 
            host="0.0.0.0"
            )