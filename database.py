import sqlite3
import uuid
import base64

class db():
    def __init__(self,  dbname):
        try:
            global conn
            conn = sqlite3.connect(dbname)
            global cursor
            cursor = conn.cursor()
        except Exception as exc:
            raise Exception(exc)
    #--<

    """
        If your database was f***ed up by something,  you can create new one

        create() - will create a new tables in your database
    """

    #------------------------------------------------------------------------------------------------<DO NOT CHANGE
    def create_users(self):
        cursor.execute("""CREATE TABLE users
                  (login text, password text, status text, gaseed text)
               """)
    def create_authorized_cookies(self):
        cursor.execute("""CREATE TABLE authorized
                  (coockieid text, login text)
               """)
    #------------------------------------------------------------------------------------------------<DO NOT CHANGE

    #--<Admin, regular

    def set_user_status(self, data):
        sql = """
        UPDATE users
        SET status = '{}'
        WHERE login = '{}'
        """.format('User',data[0])
        cursor.execute(sql)
        conn.commit()
        return True

    def create_auth(self, data):
        sql = """
        INSERT INTO authorized
        VALUES ('{}', '{}')
        """.format(data['cid'],data['login'])
        #print(sql)
        cursor.execute(sql)
        conn.commit()

    def create_user(self, data):
        gaseed = str(uuid.uuid4())
        gaseed = base64.b32encode(gaseed.encode()).decode()
        sql = """
        INSERT INTO users
        VALUES ('{}', '{}', '{}', '{}')
        """.format(data['login'], data['pass'],'Waiting', gaseed)

        cursor.execute(sql)
        conn.commit()
        return(gaseed)

    def get_user_name(self,data):
        sql = """SELECT *
                 FROM authorized
                 WHERE coockieid=?
              """

        c = cursor.execute(sql,[(data['cid'])])
        a = cursor.fetchall()
        conn.commit()
        return(a[0][1])

    def check_coockie(self,data):
        sql = """SELECT *
                 FROM authorized
                 WHERE coockieid=?
              """

        c = cursor.execute(sql,[(data['cid'])])
        a = cursor.fetchall()
        conn.commit()
        print(a)

        try:
            if len(a) == 0:
                return False
            else:
                return True
        except Exception:
            return False

    def check_user(self,data):
        sql = """SELECT *
                 FROM users
                 WHERE login=?
              """

        c = cursor.execute(sql,[(data['login'])])
        a = cursor.fetchall()
        conn.commit()

        try:
            if len(a) == 1:
                return True
            else:
                return False
        except Exception:
            return False

    def get_user_password(self,login):
        sql = """SELECT password
                 FROM users
                 WHERE login=?
              """

        c = cursor.execute(sql,[(login)])
        a = cursor.fetchall()
        conn.commit()
        return a[0][0]

    def get_user_status(self,login):
        sql = """SELECT status
                 FROM users
                 WHERE login=?
              """

        c = cursor.execute(sql,[(login)])
        a = cursor.fetchall()
        conn.commit()
        return a[0][0]

    def get_user_gaseed(self, login):
        sql = """SELECT gaseed
                 FROM users
                 WHERE login=?
              """

        c = cursor.execute(sql,[(login)])
        a = cursor.fetchall()
        conn.commit()
        return a
    def make_custom_query(self, query):
        c = cursor.execute(query)
        a = cursor.fetchall()
        conn.commit()
        return a
