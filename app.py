from flask import Flask, render_template, request, url_for
import ipdb

app = Flask(__name__)

@app.route('/')
def main():
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