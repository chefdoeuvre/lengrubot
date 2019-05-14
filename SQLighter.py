# -*- coding:  utf-8 -*-
import sqlite3

class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def AddUserFirstTime(self,id,username):
        with self.connection:
            command = 'INSERT INTO "USERS" (`id`,`username`) VALUES ('+str(id)+',"'+str(username)+'");'
            result = self.cursor.execute(command).fetchall()
            return len(result)

    def UpdateUserInfo(self,id,key,value):
        with self.connection:
            command = 'UPDATE "USERS" SET "'+str(key)+'" = "'+str(value)+'" WHERE "id" = "'+str(id)+'"'
            result = self.cursor.execute(command).fetchall()
            return len(result)

    def UserExists(self,id,username):
        with self.connection:
           command = 'SELECT id FROM USERS WHERE id = "' +str(id)+'"'
           idresult = self.cursor.execute(command).fetchall()
        if len(idresult) == 0:
           self.AddUserFirstTime(id,username)
        else:
           command = 'UPDATE "USERS" SET "username" = "'+str(username)+'" WHERE "id" = "'+str(id)+'"'
           result = self.cursor.execute(command).fetchall()
        return len(idresult)

    def UserExistsInfo(self,username):
        with self.connection:
           command = 'SELECT username FROM USERS WHERE username = "' +str(username)+'"'
           usernameresult = self.cursor.execute(command).fetchall()
        return len(usernameresult)
    
    def WhoAmI(self,id):
        with self.connection:
            return self.cursor.execute('SELECT * FROM "USERS" WHERE id = ?', (id,)).fetchall()[0]

    def ListAll(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM "USERS"').fetchall()
    
    def Whois(self,username):
        with self.connection:
            return self.cursor.execute('SELECT * FROM "USERS" WHERE username = ?', (username,)).fetchall()[0]
            
    def close(self):
        #""" ��������� ������� ���������� � �� """
        self.connection.close()