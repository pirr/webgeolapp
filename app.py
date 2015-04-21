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


@app.route('/documents_preview')
def documents_preview():
    return render_template(
            'documents_preview.html',
            user=session.get('user')
            )

@app.route('/documents', methods=['POST', 'GET'])
def documents():
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
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
        GROUP BY documents.id
        LIMIT 500
        """)

    docs = dic_cur.fetchall()
    # docs = sorted(docs, key=lambda doc: int(doc['obj_id']))
    
    html = render_template(
            'docs.html',
            docs=docs, 
            )
    
    return jsonify(html=html)


@app.route('/objs_preview')
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
            'objs_preview.html',
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
        docs = sorted(docs, key=lambda doc: int(doc['obj_id']))
        html = render_template(
                'docs.html',
                docs=docs, 
                )
    else:
        html = 'Нет группы'

    return jsonify(html=html)


@app.route('/doc_about/<doc_id>')
def doc_about(doc_id):
    return render_template(
            'doc_about.html',
            doc_id=doc_id,
            user=session.get('user')
            )

@app.route('/doc/<doc_id>', methods=['GET','POST'])
def doc(doc_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    
    dic_cur.execute("""SELECT 
        documents.id, objs_docs.obj_id, documents.doc_name, dic_source_type.name AS 'source_type',
        GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
        GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi', doc_coordinates.lat, doc_coordinates.lon 
        FROM documents
        LEFT JOIN objs_docs ON documents.id = objs_docs.doc_id
        LEFT JOIN doc_pi ON documents.id = doc_pi.doc_id 
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        LEFT JOIN source ON documents.id = source.doc_id
        LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
        LEFT JOIN doc_coordinates ON documents.id = doc_coordinates.doc_id
        WHERE documents.id = %s ##choose doc
        GROUP BY documents.id
        """, doc_id)
    doc = dic_cur.fetchone()
    
    data = request.get_json()
    
    near_docs = []

    if data != None:
        dic_cur.execute("""SELECT 
            documents.id, objs_docs.obj_id, documents.doc_name, dic_source_type.name AS 'source_type', 
              objects.obj_name, doc_coordinates.lat, doc_coordinates.lon,
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
            GROUP BY documents.id
            """)
        docs = dic_cur.fetchall()

        for doc_check in docs:
            if not {doc_check['lat'], doc_check['lon']}.intersection({None, 0, ''}):
                d = calc.distance(
                    float(doc['lat']), 
                    float(doc['lon']), 
                    float(doc_check['lat']), 
                    float(doc_check['lon'])
                    )
                if d < float(data['dist']):
                    doc_check['dist'] = data['dist']
                    near_docs.append(doc_check)

    html = render_template(
            'doc.html',
            doc=doc,
            doc_id=doc_id,
            near_docs=near_docs,
            )

    return jsonify(html=html)

@app.route('/near_docs/<doc_id>')
def near_docs(doc_id):
    data = request.get_json()
    near_docs = []

    if data != None:
        dic_cur.execute("""SELECT 
            documents.id, objs_docs.obj_id, documents.doc_name, dic_source_type.name AS 'source_type', 
              objects.obj_name, doc_coordinates.lat, doc_coordinates.lon,
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
            GROUP BY documents.id
            """)
        docs = dic_cur.fetchall()

        for doc_check in docs:
            if not {doc_check['lat'], doc_check['lon']}.intersection({None, 0, ''}):
                d = calc.distance(
                    float(doc['lat']), 
                    float(doc['lon']), 
                    float(doc_check['lat']), 
                    float(doc_check['lon'])
                    )
                if d < float(data['dist']):
                    doc_check['dist'] = data['dist']
                    near_docs.append(doc_check)

    html = render_template(
            'near_docs.html',
            near_docs=near_docs,
            )

    return jsonify(html=html)



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
            )

@app.route('/search', methods=['POST'])    
def search():
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    data = request.get_json()
    matchdocs = ''
    match = False

    if data['searchname'].strip() is not '':
    
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
                WHERE documents.doc_name LIKE %s
                GROUP BY documents.id
                """, '%'+data['searchname']+'%')
        
        matchdocs = dic_cur.fetchall()
        match = True
    else:
        match = False
    
    html = render_template(
            'search.html',
            matchdocs=matchdocs,
            match=match
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
