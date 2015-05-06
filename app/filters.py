import pymysql
import app.db_con as db

dic_cur = db.dbCon().cursor(pymysql.cursors.DictCursor)

def pis():
    dic_cur.execute("""SELECT 
        dic_pi.id AS 'pi_id', 
        dic_pi.pi, 
        dic_pi.type_pi 
        FROM dic_pi
        """)
    return dic_cur.fetchall()

def sources_type():
    dic_cur.execute("""SELECT * FROM dic_source_type""")
    return dic_cur.fetchall()



