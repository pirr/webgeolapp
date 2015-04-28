from flask import Flask, render_template

import pymysql
import app.db_con as db

app = Flask(__name__)

@app.route('/')    
def docs_table():
    dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)

    a = [1,2,3]
    # a = ','.join(map(str,a))
        
    dic_cur.execute("""SELECT 
            docs.id, objs_docs.obj_id, docs.name, dic_source_type.name AS 'source_type', dic_pi.id AS 'pi_id',
            GROUP_CONCAT(dic_pi.pi ORDER BY dic_pi.pi SEPARATOR ', ') AS 'pi',
            GROUP_CONCAT(DISTINCT dic_pi.type_pi ORDER BY dic_pi.type_pi SEPARATOR ', ') AS 'group_pi' 
            FROM docs
            LEFT JOIN objs_docs ON docs.id = objs_docs.doc_id
            LEFT JOIN doc_pi ON docs.id = doc_pi.doc_id 
            LEFT JOIN dic_pi ON dic_pi.id = doc_pi.pi_id
            LEFT JOIN source ON docs.id = source.doc_id
            LEFT JOIN dic_source_type ON dic_source_type.id = source.source_type_id
            WHERE FIND_IN_SET (doc_pi.pi_id, %s)
            GROUP BY docs.id
            LIMIT 250
            """,  ','.join(map(str,a)))
    
    docs = dic_cur.fetchall()

    return render_template('test.html',
                            docs=docs)



if __name__ == "__main__":
    app.run(
        debug=True, 
        host="0.0.0.0"
        )