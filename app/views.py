from flask import Flask, render_template, request, session, jsonify, json, url_for, redirect, make_response

import importlib
import pymysql
import csv
import io

###self modules###
import app.calculation_module as calc
import app.db_con as db
import app.filters as filters


from app import app

dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
cur = db.dbCon().cursor(pymysql.cursors.Cursor)

@app.route('/')
@app.route('/index')
def main():
    return render_template(
            'index.html', 
            user=session.get('user'),
            checkid=session.get('checkid')
            )

@app.route('/docs', methods=['POST', 'GET'])
def docs():
    dic_pi = filters.pis()
    sources_type = filters.sources_type()
    
    return render_template(
            'docs.html',
            dic_pi=dic_pi,
            sources_type = sources_type,
            user=session.get('user'),
            title='Документы',
            )

@app.route('/objs')
def objs():
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    
    dic_cur.execute("""SELECT 
        objs_docs.obj_id, 
        COUNT(DISTINCT objs_docs.doc_id) AS docs_count,
        GROUP_CONCAT(DISTINCT dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
        GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi', 
        objs.name,
        log_objs.user_id AS user_id,
        users.name AS user_name
        FROM objs_docs 
        LEFT JOIN doc_pi ON objs_docs.doc_id = doc_pi.doc_id 
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        LEFT JOIN objs ON objs.obj_id = objs_docs.obj_id
        LEFT JOIN log_objs ON log_objs.obj_id = objs_docs.obj_id
        LEFT JOIN users ON users.id = log_objs.user_id
        WHERE objs_docs.obj_id IS NOT NULL 
        GROUP BY objs_docs.obj_id
        """)
    objs = dic_cur.fetchall()

    return render_template(
            'objs.html',
            objs = objs,
            user=session.get('user'),
            user_id=session.get('user_id'),
            title='Объекты'
            )

@app.route('/doc/<doc_id>', methods=['GET','POST'])
def doc(doc_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    
    dic_cur.execute("""SELECT 
        docs.id, 
        objs_docs.obj_id, 
        docs.name, 
        dic_source_type.name AS 'source_type'
        FROM docs
        LEFT JOIN objs_docs ON docs.id = objs_docs.doc_id
        LEFT JOIN source ON docs.id = source.doc_id
        LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
        LEFT JOIN doc_coordinates ON docs.id = doc_coordinates.doc_id
        WHERE docs.id = %s
        GROUP BY docs.id
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

    dic_cur.execute("""SELECT
        objs_docs.obj_id FROM objs_docs
        WHERE objs_docs.doc_id = %s
        """, doc_id)
    picked_group_sql = dic_cur.fetchone()

    return render_template(
            'doc.html',
            doc=doc,
            pis=pis,
            coord=coord,
            user=session.get('user'),
            title='док-{}'.format(doc['id'])
            )

@app.route('/doc_editor/<doc_id>', methods=['GET','POST'])
def doc_editor(doc_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)

    dic_cur.execute("""SELECT 
        docs.id, 
        objs_docs.obj_id, 
        docs.name, 
        dic_source_type.name AS 'source_type'
        FROM docs
        LEFT JOIN objs_docs ON docs.id = objs_docs.doc_id
        LEFT JOIN source ON docs.id = source.doc_id
        LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
        LEFT JOIN doc_coordinates ON docs.id = doc_coordinates.doc_id
        WHERE docs.id = %s
        GROUP BY docs.id
        """, doc_id)
    doc = dic_cur.fetchone()
    
    dic_cur.execute("""SELECT * 
        FROM dic_source_type 
        LEFT JOIN source 
        ON dic_source_type.id = source.source_type_id
        WHERE source.doc_id = %s
        """, doc_id)
    source_type = dic_cur.fetchone()
    
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
        dic_pi.type_pi AS 'type_pi',
        doc_pi.unit_id,
        dic_pi_units.unit,
        doc_pi.P3,
        doc_pi.P2,
        doc_pi.P1,
        doc_pi.ABC1,
        doc_pi.C1,
        doc_pi.C2
        FROM doc_pi
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        LEFT JOIN dic_pi_units ON dic_pi_units.id = doc_pi.unit_id
        WHERE doc_pi.doc_id = %s
        """, doc_id)
    pis = dic_cur.fetchall()
    
    dic_pi_units = filters.dic_pi_units()

    sources_type = filters.sources_type()
    for source in sources_type:
        if source['name'] == source_type['name']:
            sources_type.remove(source)
    
    dic_pi = filters.pis()
    for pi in pis:
        for pi_ in dic_pi:
            if pi['pi_id'] == pi_['pi_id']:
                dic_pi.remove(pi_)

    return render_template(
            'doc_editor.html',
            doc=doc,
            source_type=source_type,
            sources_type=sources_type,
            pis=pis,
            dic_pi=dic_pi,
            dic_pi_units=dic_pi_units,
            coord=coord,
            user=session.get('user'),
            title='ред.док-{}'.format(doc['id'])
            )

@app.route('/doc_edit_post/<doc_id>', methods=['GET','POST'])
def doc_edit_post(doc_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    data = request.get_json()

    if data:
        dic_cur.execute("""DELETE 
            doc_pi
            FROM doc_pi
            WHERE doc_pi.doc_id = %s
            """, doc_id)

        for pi_id in data['pis_id']:
            dic_cur.execute("""INSERT INTO 
                doc_pi 
                (doc_pi.doc_id, doc_pi.pi_id)
                VALUES (%s, %s)""",
                (int(doc_id), int(pi_id)))

        dic_cur.execute("""UPDATE
            docs
            SET docs.name = %s
            WHERE docs.id = %s""",
            (data['name'],doc_id))

        dic_cur.execute("""UPDATE
            doc_coordinates
            SET doc_coordinates.lat = %s,
                doc_coordinates.lon = %s
            WHERE doc_coordinates.doc_id = %s""",
            (data['lat'], data['lon'], doc_id))

        dic_cur.execute("""UPDATE
            source
            SET source.source_type_id = %s
            WHERE source.doc_id = %s""",
            (data['source_type_id'], doc_id))

        return 'ok'

    else:
        return 'Err'

@app.route('/docs_in_obj/<doc_id>', methods=['GET','POST'])
def docs_in_obj(doc_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)

    dic_cur.execute("""SELECT
        objs_docs.obj_id FROM objs_docs
        WHERE objs_docs.doc_id = %s
        """, doc_id)
    picked_group_sql = dic_cur.fetchone()

    # docs = None
    if picked_group_sql:
        obj_id = picked_group_sql['obj_id']
        dic_cur.execute("""SELECT 
            docs.id, 
            objs_docs.obj_id, 
            docs.name, 
            dic_source_type.name AS 'source_type', 
            objs.name, doc_coordinates.lat, 
            doc_coordinates.lon,
            GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
            GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi' 
            FROM docs
            LEFT JOIN objs_docs ON docs.id = objs_docs.doc_id
            LEFT JOIN doc_pi ON docs.id = doc_pi.doc_id 
            LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
            LEFT JOIN source ON docs.id = source.doc_id
            LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
            LEFT JOIN objs ON objs.obj_id = objs_docs.obj_id
            LEFT JOIN doc_coordinates ON docs.id = doc_coordinates.doc_id
            WHERE objs_docs.obj_id = %s
            GROUP BY docs.id
            """, obj_id)
        
    docs = dic_cur.fetchall()

    html = render_template('docs_in_obj.html',
                            docs=docs)

    return jsonify(html=html)


@app.route('/obj/<obj_id>')
def obj(obj_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    
    dic_cur.execute("""SELECT 
        docs.id, 
        objs_docs.obj_id,
        docs.name,
        dic_source_type.name AS 'source_type', 
        doc_coordinates.lat, 
        doc_coordinates.lon,
        GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
        GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi'
        FROM objs_docs
        LEFT JOIN docs ON docs.id = objs_docs.doc_id
        LEFT JOIN doc_pi ON docs.id = doc_pi.doc_id 
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        LEFT JOIN source ON docs.id = source.doc_id
        LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
        LEFT JOIN objs ON objs.obj_id = objs_docs.obj_id
        LEFT JOIN doc_coordinates ON docs.id = doc_coordinates.doc_id
        WHERE objs_docs.obj_id = %s
        GROUP BY objs_docs.id
        """, obj_id)
    docs = dic_cur.fetchall()

    dic_cur.execute("""SELECT
        objs.name, 
        objs.obj_id,
        log_objs.user_id, 
        GROUP_CONCAT(DISTINCT dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi'
        FROM objs_docs
        LEFT JOIN objs ON objs_docs.obj_id = objs.obj_id
        LEFT JOIN log_objs ON log_objs.obj_id = objs.obj_id
        LEFT JOIN doc_pi ON objs_docs.doc_id = doc_pi.doc_id
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        WHERE objs.obj_id = %s
        """, obj_id)
    obj = dic_cur.fetchone()

    return render_template(
            'obj.html',
            docs=docs,
            obj=obj,
            user=session.get('user'),
            user_id=session.get('user_id'),
            title=('объект-{}'.format(obj_id))
            )

@app.route('/obj_editor/<obj_id>')
def obj_editor(obj_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)

    dic_cur.execute("""SELECT
        objs.name, 
        objs.obj_id, 
        GROUP_CONCAT(DISTINCT dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi'
        FROM objs_docs
        LEFT JOIN objs ON objs_docs.obj_id = objs.obj_id
        LEFT JOIN doc_pi ON objs_docs.doc_id = doc_pi.doc_id
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        LEFT JOIN docs ON docs.id = objs_docs.doc_id
        WHERE objs.obj_id = %s
        """, obj_id)
    obj = dic_cur.fetchone()

    return render_template(
            'obj_editor.html',
            obj=obj,
            user=session.get('user'),
            title=('ред.объект-{}'.format(obj_id))
            )

@app.route('/obj_search/<obj_id>', methods=['POST'])
def obj_search(obj_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    data = request.get_json()

    dic_cur.execute("""SELECT 
            docs.id, 
            objs_docs.obj_id, 
            docs.name, 
            dic_source_type.name AS 'source_type',
            GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
            GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi', 
            doc_coordinates.lat, 
            doc_coordinates.lon
            FROM docs
            LEFT JOIN objs_docs ON docs.id = objs_docs.doc_id
            LEFT JOIN doc_pi ON docs.id = doc_pi.doc_id 
            LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
            LEFT JOIN source ON docs.id = source.doc_id
            LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
            LEFT JOIN doc_coordinates ON docs.id = doc_coordinates.doc_id
            WHERE (docs.name LIKE %s AND objs_docs.obj_id IS NULL) 
                OR (docs.name LIKE %s AND objs_docs.obj_id <> %s)
            GROUP BY docs.id
            LIMIT 250
            """, ('%'+data['searchname']+'%', 
                '%'+data['searchname']+'%', obj_id))

    docs = dic_cur.fetchall()
    html = render_template(
        'obj_search.html',
        docs=docs,
        obj_id=obj_id
        )

    return jsonify(html=html)

@app.route('/obj_create/<doc_id>', methods=['GET','POST'])
def obj_create(doc_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)

    dic_cur.execute("""SELECT 
            MAX(objs.obj_id) AS obj_id
            FROM objs
            """)
    obj_id = dic_cur.fetchone()
    
    if obj_id['obj_id']:
        obj_id = int(obj_id['obj_id']) + 1 
    else:
        obj_id = 1

    dic_cur.execute("""SELECT 
            docs.name 
            FROM docs
            WHERE docs.id = %s
            """, doc_id )
    obj_name = dic_cur.fetchone()

    dic_cur.execute("""INSERT INTO
            objs_docs (obj_id, doc_id)
            VALUES (%s,%s)
            """, (obj_id, doc_id))

    dic_cur.execute("""INSERT INTO
            objs (obj_id, name)
            VALUES (%s,%s);
            """, (obj_id, obj_name['name']))
    
    dic_cur.execute("""INSERT INTO
            log_objs (user_id, obj_id)
            VALUES (%s,%s)
            """, (session['user_id'], obj_id))

    return redirect(url_for('obj_editor',obj_id=obj_id))

@app.route('/obj_docs/<obj_id>', methods=['POST'])
def obj_docs(obj_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    data = request.get_json()

    if 'doc_id_push' in data:
        dic_cur.execute("""DELETE 
                objs_docs
                FROM objs_docs
                WHERE objs_docs.doc_id = %s
                """, data['doc_id_push'])

    if 'doc_id_pull' in data:
        dic_cur.execute("""SELECT 
                objs_docs.obj_id
                FROM objs_docs
                WHERE objs_docs.doc_id = %s
                """, data['doc_id_pull'])
        obj_id_pull = dic_cur.fetchone()

        if obj_id_pull:
            return 'Документ уже в группе'
        else:
            dic_cur.execute("""INSERT IGNORE INTO
                    objs_docs (obj_id, doc_id)
                    VALUES (%s,%s)
                    """, (obj_id, data['doc_id_pull']))

    docs_res = None
    if 'docs_res' in data:
        docs_res = ','.join(map(str,data['docs_res']))

        dic_cur.execute("""SELECT
            docs.id, 
            docs.name,
            GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
            doc_coordinates.lat, 
            doc_coordinates.lon
            FROM docs
            JOIN doc_pi ON docs.id = doc_pi.doc_id 
            JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
            JOIN doc_coordinates ON docs.id = doc_coordinates.doc_id
            WHERE FIND_IN_SET(docs.id, %s)
            GROUP BY docs.id
            """, docs_res)
        docs_res = dic_cur.fetchall()

    dic_cur.execute("""SELECT 
            docs.id, 
            objs_docs.obj_id, 
            docs.name, 
            dic_source_type.name AS 'source_type', 
            doc_coordinates.lat, 
            doc_coordinates.lon,
            GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
            GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi'
            FROM objs_docs
            LEFT JOIN docs ON docs.id = objs_docs.doc_id
            LEFT JOIN doc_pi ON docs.id = doc_pi.doc_id 
            LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
            LEFT JOIN source ON docs.id = source.doc_id
            LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
            LEFT JOIN objs ON objs.obj_id = objs_docs.obj_id
            LEFT JOIN doc_coordinates ON docs.id = doc_coordinates.doc_id
            WHERE objs_docs.obj_id = %s
            GROUP BY objs_docs.id
            """, obj_id)
    
    obj = dic_cur.fetchall()

    if not obj:
        dic_cur.execute("""DELETE 
            objs
            FROM objs
            WHERE objs.obj_id = %s
            """, obj_id)

        return 'Empty'

    else:
        html = render_template(
            'obj_docs.html',
            obj=obj,
            obj_id=obj_id,
            docs_res_=docs_res)
        return jsonify(html=html)

@app.route('/obj_edit_post/<obj_id>', methods=['GET','POST'])
def obj_edit_post(obj_id):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    data = request.get_json()

    if data:
        
        dic_cur.execute("""UPDATE
            objs
            SET objs.name = %s
            WHERE objs.obj_id = %s""",
            (data['obj_name'],obj_id))

        return 'ok'

    else:
        return 'Err'

@app.route('/docs_table', methods=['POST'])    
def docs_table():
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    data = request.get_json()
    if 'searchname' in data:
        searchname = data['searchname']
    else:
        searchname = ''
    
    if 'pis_id' in data:
        pis_id = ','.join(map(str,data['pis_id']))

    if 'sources_id' in data:
        sources_id = ','.join(map(str,data['sources_id']))

    dic_cur.execute("""SELECT
            docs.id, 
            objs_docs.obj_id, 
            docs.name, 
            dic_source_type.name AS 'source_type', 
            dic_pi.id AS 'pi_id',
            doc_coordinates.lat, 
            doc_coordinates.lon,
            GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
            GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi'
            FROM docs
            LEFT JOIN objs_docs ON docs.id = objs_docs.doc_id
            LEFT JOIN doc_pi ON docs.id = doc_pi.doc_id 
            LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
            LEFT JOIN source ON docs.id = source.doc_id
            LEFT JOIN doc_coordinates ON docs.id = doc_coordinates.doc_id
            LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
            WHERE FIND_IN_SET (doc_pi.pi_id, %s) AND docs.name LIKE %s AND FIND_IN_SET (dic_source_type.id, %s)
            GROUP BY docs.id
            LIMIT 150
            """,(pis_id, '%'+searchname+'%', sources_id))
    docs = dic_cur.fetchall()
    count = len(docs)
    
    html = render_template(
        'docs_table.html',
        docs=docs,
        count=count,
        user=session.get('user')
        )

    return jsonify(html=html)

@app.route('/download', methods=['GET'])
def download_registry():

    dic_cur.execute("""SELECT
            docs.id AS '№ п/п', 
            objs_docs.obj_id AS '№ объекта', 
            docs.name AS 'Название', 
            dic_source_type.name AS 'Источник', 
            GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'Полезные ископаемые',
            GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'Группа ПИ',
            doc_coordinates.lat AS 'Широта',
            doc_coordinates.lon AS 'Долгота'
            FROM docs
            LEFT JOIN objs_docs ON docs.id = objs_docs.doc_id
            LEFT JOIN doc_pi ON docs.id = doc_pi.doc_id 
            LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
            LEFT JOIN source ON docs.id = source.doc_id
            LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
            LEFT JOIN doc_coordinates ON doc_coordinates.doc_id = docs.id
            GROUP BY docs.id
            """)

    docs = dic_cur.fetchall()
    sio = io.StringIO()
    fieldnames =['№ п/п','№ объекта','Название','Источник',
        'Полезные ископаемые','Группа ПИ','Широта','Долгота']
    dict_writer = csv.DictWriter(sio, fieldnames=fieldnames, delimiter=';', lineterminator='\n', extrasaction='ignore')
    dict_writer.writeheader()
    dict_writer.writerows(docs)
    response = make_response((sio.getvalue()).encode("windows-1251"))
    response.headers["Content-Disposition"] = "attachment; filename=registry.csv"
    
    return response
 
@app.route('/log/<user>', methods=['GET','POST'])
def log(user):
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    
    dic_cur.execute("""SELECT 
        objs_docs.obj_id, COUNT(DISTINCT objs_docs.doc_id) AS docs_count,
        GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
        GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi', objs.name
        FROM objs_docs 
        LEFT JOIN log_objs ON log_objs.obj_id = objs_docs.obj_id
        LEFT JOIN doc_pi ON objs_docs.doc_id = doc_pi.doc_id
        LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
        LEFT JOIN objs ON objs.obj_id = objs_docs.obj_id
        WHERE objs_docs.obj_id IS NOT NULL AND log_objs.user_id = %s
        GROUP BY objs_docs.obj_id
        """, session['user_id'])
    
    objs = dic_cur.fetchall()

    return render_template(
            "log.html",
            user=user,
            objs = objs,
            title='Пользователь'
            )
    
@app.route('/login', methods=['POST'])
def login():
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)
    data = request.get_json()

    dic_cur.execute("""SELECT *
                    FROM users
                    WHERE users.name = %s 
                        AND users.pass = %s
                        """, (data['user'], data['password']))
    user = dic_cur.fetchone()

    if user:
        session['user'] = user['name']
        session['user_id'] = user['id']
        return 'ok'
    else:
        return 'Err'

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return 'clear'

# @app.route('/test', methods=['GET','POST'])
# def test():
#     tab_data = [{'a':2,'b':3,'c':5}, {'a':6,'b':7,'c':8}]
#     return render_template('test.html', tab_data=tab_data)

# @app.route('/test_data', methods=['GET','POST'])
# def data_test():
#     tab_data = [{'a':2,'b':3,'c':5}, {'a':6,'b':7,'c':8}]
#     return jsonify(tab_data=tab_data)

app.run(
        debug=True, 
        host="0.0.0.0"
        )
