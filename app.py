from flask import Flask, render_template, request, session, jsonify, json
import importlib
import pymysql
import data.db_con as db
import data.calculation_module as calc
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

@app.route('/docs', methods=['POST', 'GET'])
def docs():
    return render_template(
            'docs.html',
            user=session.get('user')
            )

@app.route('/objs')
def objs_preview():
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    
    dic_cur.execute("""SELECT 
        objs_docs.obj_id, COUNT(*) AS docs_count,
        GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
        GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi', objects.obj_name
        FROM objs_docs 
        LEFT JOIN doc_pi ON objs_docs.doc_id = doc_pi.doc_id 
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        LEFT JOIN objects ON objects.obj_id = objs_docs.obj_id
        WHERE objs_docs.obj_id<>0 
        GROUP BY objs_docs.obj_id
        """)
    
    objs = dic_cur.fetchall()

    return render_template(
            'objs.html',
            objs = objs,
            user=session.get('user')
            )

@app.route('/object/<doc_id>', methods=['POST'])
def doc_in_obj(doc_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)

    dic_cur.execute("""SELECT
        objs_docs.obj_id FROM objs_docs
        WHERE objs_docs.doc_id = %s
        """, doc_id)
    picked_group_sql = dic_cur.fetchone()

    if picked_group_sql:
        obj_id = picked_group_sql['obj_id']
        dic_cur.execute("""SELECT 
            documents.id, objs_docs.obj_id, documents.doc_name, dic_source_type.name AS 'source_type', objects.obj_name, doc_coordinates.lat, doc_coordinates.lon,
            GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
            GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi' 
            FROM documents
            LEFT JOIN objs_docs ON documents.id = objs_docs.doc_id
            LEFT JOIN doc_pi ON documents.id = doc_pi.doc_id 
            LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
            LEFT JOIN source ON documents.id = source.doc_id
            LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
            LEFT JOIN objects ON objects.obj_id = objs_docs.obj_id
            LEFT JOIN doc_coordinates ON documents.id = doc_coordinates.doc_id
            WHERE objs_docs.obj_id = %s
            GROUP BY documents.id
            """, obj_id)
        
        docs = dic_cur.fetchall()
        # docs = sorted(docs, key=lambda doc: int(doc['obj_id']))
        html = render_template(
                'search.html',
                docs=docs, 
                )
    else:
        html = 'Нет группы'

    return jsonify(html=html)

@app.route('/doc/<doc_id>', methods=['GET','POST'])
def doc(doc_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    
    dic_cur.execute("""SELECT 
        documents.id, 
        objs_docs.obj_id, 
        documents.doc_name, 
        dic_source_type.name AS 'source_type'
        FROM documents
        LEFT JOIN objs_docs ON documents.id = objs_docs.doc_id
        LEFT JOIN source ON documents.id = source.doc_id
        LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
        LEFT JOIN doc_coordinates ON documents.id = doc_coordinates.doc_id
        WHERE documents.id = %s
        GROUP BY documents.id
        """, doc_id)
    doc = dic_cur.fetchone()
    
    dic_cur.execute("""SELECT 
        dic_pi.pi AS 'pi', 
        dic_pi.type_pi AS 'group_pi' 
        FROM doc_pi
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        WHERE doc_pi.doc_id = %s
        """, doc_id)
    pis = dic_cur.fetchall()

    dic_cur.execute("""SELECT 
        doc_coordinates.lat, 
        doc_coordinates.lon 
        FROM doc_coordinates
        WHERE doc_coordinates.doc_id = %s
        """, doc_id)
    coord = dic_cur.fetchone()

    return render_template(
            'doc.html',
            doc=doc,
            pis=pis,
            coord=coord,
            user=session.get('user')
            )

@app.route('/doc_editor/<doc_id>', methods=['GET','POST'])
def doc_editor(doc_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)

    dic_cur.execute("""SELECT 
        documents.id, 
        objs_docs.obj_id, 
        documents.doc_name, 
        dic_source_type.name AS 'source_type'
        FROM documents
        LEFT JOIN objs_docs ON documents.id = objs_docs.doc_id
        LEFT JOIN source ON documents.id = source.doc_id
        LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
        LEFT JOIN doc_coordinates ON documents.id = doc_coordinates.doc_id
        WHERE documents.id = %s
        GROUP BY documents.id
        """, doc_id)
    doc = dic_cur.fetchone()
    
    dic_cur.execute("""SELECT * 
        FROM dic_source_type 
        LEFT JOIN source 
        ON dic_source_type.id = source.source_type_id
        WHERE source.doc_id = %s
        """, doc_id)
    source_type = dic_cur.fetchone()

    dic_cur.execute("""SELECT * 
        FROM dic_source_type
        """)
    dic_source_types = dic_cur.fetchall()
    for source in dic_source_types:
        if source['name'] == source_type['name']:
            dic_source_types.remove(source)
    
    dic_cur.execute("""SELECT 
        doc_coordinates.lat, 
        doc_coordinates.lon 
        FROM doc_coordinates
        WHERE doc_coordinates.doc_id = %s
        """, doc_id)
    coord = dic_cur.fetchone()
    
    dic_cur.execute("""SELECT
        dic_pi.id AS 'pi_id',
        dic_pi.pi AS 'pi', 
        dic_pi.type_pi AS 'type_pi' 
        FROM doc_pi
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        WHERE doc_pi.doc_id = %s
        """, doc_id)
    pis = dic_cur.fetchall()

    dic_cur.execute("""SELECT 
        dic_pi.id AS 'pi_id', 
        dic_pi.pi, 
        dic_pi.type_pi 
        FROM dic_pi""")
    dic_pi = dic_cur.fetchall()
    for pi in pis: dic_pi.remove(pi)

    return render_template(
            'doc_editor.html',
            doc=doc,
            source_type=source_type,
            dic_source_types=dic_source_types,
            pis=pis,
            coord=coord,
            dic_pi=dic_pi,
            user=session.get('user'),
            )

@app.route('/doc_edit_post/<doc_id>', methods=['GET','POST'])
def doc_edit_post(doc_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    data = request.get_json()
    
    if data:
        dic_cur.execute("""DELETE doc_pi
            FROM doc_pi
            WHERE doc_pi.doc_id = %s
            """, doc_id)

        for pi in data['features_pis']:
            dic_cur.execute("""INSERT INTO doc_pi 
                (doc_pi.doc_id, doc_pi.pi_id)
                VALUES (%s, %s)""",
                (int(doc_id), int(pi)))

        return 'ok'
    else:
        return 'Err'


@app.route('/obj/<obj_id>')
def obj(obj_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    
    dic_cur.execute("""SELECT 
        documents.id, objs_docs.obj_id, documents.doc_name, dic_source_type.name AS 'source_type', objects.obj_name, doc_coordinates.lat, doc_coordinates.lon,
        GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
        GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi'
        FROM objs_docs
        LEFT JOIN documents ON documents.id = objs_docs.doc_id
        LEFT JOIN doc_pi ON documents.id = doc_pi.doc_id 
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        LEFT JOIN source ON documents.id = source.doc_id
        LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
        LEFT JOIN objects ON objects.obj_id = objs_docs.obj_id
        LEFT JOIN doc_coordinates ON documents.id = doc_coordinates.doc_id
        WHERE objs_docs.obj_id = %s
        GROUP BY objs_docs.id
        """, obj_id)
    obj = dic_cur.fetchall()

    return render_template(
            'obj.html',
            obj = obj,
            user=session.get('user')
            )

@app.route('/search', methods=['POST'])    
def search():
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    data = request.get_json()
    
    dic_cur.execute("""SELECT 
            documents.id, objs_docs.obj_id, documents.doc_name, dic_source_type.name AS 'source_type',
            GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
            GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi' 
            FROM documents
            LEFT JOIN objs_docs ON documents.id = objs_docs.doc_id
            LEFT JOIN doc_pi ON documents.id = doc_pi.doc_id 
            LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
            LEFT JOIN source ON documents.id = source.doc_id
            LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
            WHERE LOWER(documents.doc_name) LIKE LOWER(%s)
            GROUP BY documents.id
            LIMIT 250
            """, '%'+data['searchname']+'%')
    
    docs = dic_cur.fetchall()
    html = render_template(
            'search.html',
            docs=docs,
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
