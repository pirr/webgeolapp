from flask import Flask, render_template, request, session, jsonify, g, url_for, redirect, Blueprint
import importlib
import pymysql
import data.db_con as db

app = Flask(__name__)
dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)

users = [('one','pass1'),('two','pass2')]

test_page = Blueprint('test_page', __name__,
                        template_folder='templates')
@app.route('/test/')
@app.route('/test/<checkid>')
def test(checkid):
    checkid = checkid
    return render_template('test.html', checkid=checkid)
    # return render_template('test.html',
    #     user=session.get('user'),
    #     checkid=checkid)
    # checkid=session.get('checkid')
    # return render_template('test.html', checkid=checkid)

@app.route('/')
def main():
    return render_template(
            'index.html', 
            user=session.get('user'),
            checkid=session.get('checkid')
            )

@app.route('/documents')
def documents():
    dic_cur.execute("""SELECT 
        objects.id, objects.obj_name, dic_doc_type.name AS 'doc_type',
        GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi 
            SEPARATOR ', ') AS 'pi',
        GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi 
            SEPARATOR ', ') AS 'group_pi'
        FROM objects
        LEFT JOIN obj_pi on objects.id = obj_pi.obj_id 
        LEFT JOIN dic_pi on dic_pi.id = obj_pi.pi_id
        LEFT JOIN obj_doc on objects.id = obj_doc.obj_id
        LEFT JOIN dic_doc_type on dic_doc_type.id = obj_doc.doc_type_id
        GROUP BY objects.id
        LIMIT 500""")
    
    data = dic_cur.fetchall()
    return render_template(
            'documents.html', 
            user=session.get('user'),
            count=len(data),
            data=data,
            )

@app.route('/objects')
def objs():
    return render_template(
            'objects.html', 
            user=session.get('user')
            )
@app.route('/checkdoc/', methods=['POST'])
@app.route('/checkdoc/<check>')
def checkdoc():
    data = request.get_json()
    session['checkid'] = data['check']
    check = session['checkid']
    return session['checkid']

@app.route('/workspacedoc/<pick_id>')
def workspacedoc(pick_id):
    pick_id = pick_id
    dic_cur.execute("""SELECT 
        objects.id, objects.obj_name, dic_doc_type.name AS 'doc_type',
        GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
        GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi 
            SEPARATOR ', ') AS 'group_pi'
        FROM objects
        LEFT JOIN obj_pi on objects.id = obj_pi.obj_id 
        LEFT JOIN dic_pi on dic_pi.id = obj_pi.pi_id
        LEFT JOIN obj_doc on objects.id = obj_doc.obj_id
        LEFT JOIN dic_doc_type on dic_doc_type.id = obj_doc.doc_type_id
        WHERE objects.id = %s
        GROUP BY objects.id""", pick_id)
    checkdoc = dic_cur.fetchone()
    return render_template(
            'workspacedoc.html', 
            user=session.get('user'),
            doc=checkdoc,
            )


        
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if (data['user'], data['password']) in users:
        session['user'] = data['user']
        return 'ok'
    else:
        return 'Err'

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return 'clear'

if __name__ == '__main__':
    app.secret_key = "bacon"
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(
        debug=True, 
        host="0.0.0.0"
        )
