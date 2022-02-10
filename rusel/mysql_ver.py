import mysql.connector
from service.secret import host, user, password, database, auth_plugin

def get_mysql_ver():
    con = mysql.connector.connect(host=host, user=user, password=password, database=database, auth_plugin=auth_plugin)
    db_name = database + '.'
    cur = con.cursor(buffered=True)
    cur.execute('SELECT VERSION()')
    ver = cur.fetchall()
    con.commit()
    con.close()
    return ver[0][0]

