from flask import Flask, render_template, request, session, jsonify, g, url_for, redirect, Blueprint
import importlib
import pymysql
import data.db_con as db
import difflib

app = Flask(__name__)
dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)

users = [('one','pass1'),('two','pass2')]

# @app.route('/test/')
# @app.route('/test/<checkid>')
# def test(checkid):
#     checkid = checkid
#     return render_template('test.html', checkid=checkid)

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

@app.route('/objedit/<pick_id>')
def objedit(pick_id):
    session['pick_id'] = pick_id
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
    pickeddoc = dic_cur.fetchone()
    session['pickedid'] = pick_id

    return render_template(
            'objedit.html', 
            user=session.get('user'),
            doc=pickeddoc,
            matchdoc=session.get('matchdoc'),
            )


@app.route('/search', methods=['POST'])    
def search():
    data = request.get_json()
    pick_id = session.get('pickedid')
    
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
            WHERE objects.id <> %s
            GROUP BY objects.id""", pick_id)
    unpickeddata = dic_cur.fetchall()
    
    matchdoc = []
    for doc in unpickeddata:
        session['matchdoc'].clear()
        matchdoc.clear()
        if data['searchname'] in doc['obj_name']:
            matchdoc.append(doc)
            session['matchdoc'] = matchdoc
            return 'Match'
        else:
            return 'Err'
   
    

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
    app.debug = True
    app.run(
        debug=True, 
        host="0.0.0.0"
        )
