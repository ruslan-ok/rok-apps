"""Module for interacting with the SQLite database"""
import requests, json, datetime, sqlite3, mysql.connector
from rusel.secret import use_mysql, db_file, host, user, password, database, auth_plugin

debug = False

class DB():
    def open(self):
        if use_mysql:
            self.con = mysql.connector.connect(host=host, user=user, password=password, database=database, auth_plugin=auth_plugin)
        else:
            self.con = sqlite3.connect(db_file)
        if use_mysql:
            self.param_ph = '%s'
            self.db_name = database + '.'
        else:
            self.param_ph = '?'
            self.db_name = ''

    def close(self):
        self.con.commit()
        self.con.close()

    def execute(self, request, params=None):
        if use_mysql:
            cur = self.con.cursor(buffered=True)
        else:
            cur = self.con.cursor()
        prep_request = request.replace('%d.', self.db_name).replace('?', self.param_ph)
        if debug:
            print('--------------------------')
            print(prep_request, params)
            print('--------------------------')
        cur.execute(prep_request, params)
        if 'SELECT' in request:
            return cur.fetchall()
        return None

