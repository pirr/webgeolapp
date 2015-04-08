from flask import Flask, render_template, request, session, jsonify, g
import ipdb
import importlib
import pymysql
import data.workdata as dw
import data.db_con as db
importlib.reload(dw)

app = Flask(__name__)

users = [('one','pass1'),('two','pass2')]

dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)

@app.route('/')
def main():
    return render_template(
                        'index.html', 
                        user=session.get('user')
                        )

@app.route('/documents')
def documents():
    dic_cur.execute("""
        SELECT 
        objects.id, objects.obj_name, dic_doc_type.name AS 'doc_type',
        GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
        GROUP_CONCAT(DISTINCT dic_pi.type_pi order by dic_pi.type_pi 
            SEPARATOR ', ') AS 'group_pi'
        from objects
        left join obj_pi on objects.id = obj_pi.obj_id 
        left join dic_pi on dic_pi.id = obj_pi.pi_id
        left join obj_doc on objects.id = obj_doc.obj_id
        left join dic_doc_type on dic_doc_type.id = obj_doc.doc_type_id
        group by objects.id
                            """)
    data = dic_cur.fetchall()
    return render_template(
                        'documents.html', 
                        user=session.get('user'),
                        count=len(data),
                        data=data
                        )

@app.route('/objects')
def objs():
    return render_template(
                        'objects.html', 
                        user=session.get('user')
                        )

# @app.route('/test')
# def test():
#     return render_template(
#                         'test.html',
#                         checkid=session.get('checkid')
#                         )


@app.route('/workspacedoc')
def workspacedoc():
    dic_cur.execute("""
        SELECT 
        objects.id, objects.obj_name, dic_doc_type.name AS 'doc_type',
        GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
        GROUP_CONCAT(DISTINCT dic_pi.type_pi order by dic_pi.type_pi 
            SEPARATOR ', ') AS 'group_pi'
        from objects
        left join obj_pi on objects.id = obj_pi.obj_id 
        left join dic_pi on dic_pi.id = obj_pi.pi_id
        left join obj_doc on objects.id = obj_doc.obj_id
        left join dic_doc_type on dic_doc_type.id = obj_doc.doc_type_id
        WHERE objects.id = %s
        group by objects.id
                            """, session.get('checkid'))
    checkdoc = dic_cur.fetchone()
    return render_template(
                        'workspacedoc.html', 
                        user=session.get('user'),
                        checkid=session.get('checkid'),
                        doc=checkdoc
                        )

@app.route('/checkdoc', methods=['POST'])
def checkdoc():
    data = request.get_json()
    session['checkid'] = data['check']
    return session['checkid']
        
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
    return ''

if __name__ == '__main__':
    app.secret_key = "bacon"
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(
            debug=True, 
            host="0.0.0.0"
            )
