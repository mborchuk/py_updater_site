import mysql.connector


class DataBases:

    def __init__(self, host, user, password, database, port):
        self.login = user
        self.password = password
        self.host = host
        self.database = database
        self.mydb = ''
        self.port = port

    def connect(self):

        mydb = mysql.connector.connect(
            host=self.host,
            user=self.login,
            passwd=self.password,
            database=self.database,
            port=self.port
        )
        if mydb:
            self.mydb = mydb
        else:
            self.mydb = False

    def query(self, query, val='', type='I'):
        myresult = ''
        mycursor = self.mydb.cursor()
        mycursor.execute(query, val)
        #self.mydb.commit()
        if type == 'S':
            myresult = mycursor.fetchall()
        #self.mydb.commit()
        #return mycursor.lastrowid
        return myresult
