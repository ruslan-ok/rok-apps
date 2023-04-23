import os, mysql.connector

def get_mysql_ver():
    host = os.environ.get('DJANGO_HOST_MAIL')
    user = os.environ.get('DJANGO_PROD_DB_USER')
    password = os.environ.get('DJANGO_PROD_DB_PWRD')
    database = os.environ.get('DJANGO_PROD_DB_NAME')
    try:
        con = mysql.connector.connect(host=host, user=user, password=password, database=database, auth_plugin='mysql_native_password')
        cur = con.cursor(buffered=True)
        cur.execute('SELECT VERSION()')
        ver = cur.fetchall()
        con.commit()
        con.close()
        return ver[0][0]
    except:
        return ''

