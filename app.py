from flask import Flask, render_template, request, session, jsonify
import importlib
import pymysql
import data.db_con as db
import difflib

app = Flask(__name__)
dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)

users = [('one','pass1'),('two','pass2')]

@app.route('/')
def main():
    return render_template(
            'index.html', 
            user=session.get('user'),
            checkid=session.get('checkid')
            )

@app.route('/documents')
def documents():
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    dic_cur.execute("""SELECT 
        documents.id, objects.obj_id, documents.doc_name, dic_source_type.name AS 'source_type',
        GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
        GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi' 
        FROM documents
        LEFT JOIN objects ON documents.id = objects.doc_id
        LEFT JOIN doc_pi ON documents.id = doc_pi.doc_id 
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        LEFT JOIN source ON documents.id = source.doc_id
        LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
        GROUP BY documents.id
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
    return render_template(
            'objedit.html',
            pick_id=pick_id
            )

@app.route('/doc_in_obj/<pick_id>', methods=['POST', 'GET'])
def doc_in_obj(pick_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    
    dic_cur.execute("""SELECT
        objects.obj_id FROM objects
        WHERE objects.doc_id = %s""", pick_id)
    picked_group_sql = dic_cur.fetchone()
    
    if not picked_group_sql:
        dic_cur.execute("""SELECT 
            MAX(objects.obj_id) AS obj_id from objects
            """)
        obj_last_id = dic_cur.fetchone()
        obj_id = int(obj_last_id['obj_id']) + 1
        dic_cur.execute("""INSERT IGNORE INTO 
                    objects (obj_id, doc_id)
                    VALUES (%s, %s)""",
                    (obj_id, pick_id))
        picked_group = obj_id
    else:
        picked_group = picked_group_sql['obj_id']
        

    dic_cur.execute("""SELECT 
        documents.id, objects.obj_id, documents.doc_name, dic_source_type.name AS 'source_type',
        GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
        GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi' 
        FROM documents
        LEFT JOIN objects ON documents.id = objects.doc_id
        LEFT JOIN doc_pi ON documents.id = doc_pi.doc_id 
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        LEFT JOIN source ON documents.id = source.doc_id
        LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
        WHERE objects.obj_id = %s
        GROUP BY documents.id
        """, picked_group)
    doc_in_obj = dic_cur.fetchall()

    html = render_template(
            'doc_in_obj.html',
            doc_in_obj=doc_in_obj,
            )

    return jsonify(html=html)


@app.route('/search', methods=['POST', 'GET'])    
def search():
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    data = request.get_json()
    
    dic_cur.execute("""SELECT 
                documents.id, objects.obj_id, documents.doc_name, dic_source_type.name AS 'source_type',
            GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
            GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi' 
            FROM documents
            LEFT JOIN objects ON documents.id = objects.doc_id
            LEFT JOIN doc_pi ON documents.id = doc_pi.doc_id 
            LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
            LEFT JOIN source ON documents.id = source.doc_id
            LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
            WHERE documents.doc_name LIKE %s
            GROUP BY documents.id""", '%'+data['searchname']+'%')
    matchdoc = dic_cur.fetchall()
    
    html = render_template(
            'search.html',
            matchdoc=matchdoc,
            )
    
    return jsonify(html=html)

    
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
