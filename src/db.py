"""
To use : Sqlite

File that will :
    1. connect/validate to sqlite database
    2. contains function for query and checks
    3. contains function for update
"""
from email.mime import base
# from os import O_NONBLOCK, stat
from re import S
import re
import sqlite3
import logging
from ast import literal_eval

from black import out

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserDatabase:
    def __init__(self, db_name, table_name):
        try:
            logger.info("Connecting to sqlite database with name: " + db_name)
            # self.connection = sqlite3.connect(
            #     db_name,  check_same_thread=False)
            self.table_name = table_name
            self.db_name = db_name
            logger.info("Connecting established successfully: " + table_name)
        except Exception as e:
            logger.info("Error connecting to database: " + str(e))
        # self.cursor = self.connection.cursor()
        self.check_string = f"""SELECT * FROM {self.table_name}"""
        self.query_string = f"""SELECT * FROM {self.table_name} WHERE username=? and password=?"""
        self.insert_string = f"""INSERT INTO {self.table_name} (username, password, response, role) VALUES(?,?,?,'student')"""
        self.update_string = f"""UPDATE {self.table_name} SET response=? where username=?"""

    def validate(self, username, password):
        self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
        self.cursor = self.connection.cursor() 
        response = self.cursor.execute(
            self.query_string, (username, password)).fetchone()
        logger.info("Validation successful for username: " + str(username))
        logger.info(response)
        status = 0
        if response:
            if response[-1] == '':
                status = 1
            if response[-1] is None:
                status = 2
        self.connection.close()        
        return True if response else False, status

    def update_entry(self, username, feed_type, response=None):
        try:
            self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
            self.cursor = self.connection.cursor() 
            if username is not None and feed_type is not None and response is not None:
                prev_response = self.cursor.execute(
                    f"""SELECT * FROM {self.table_name} WHERE username=?""", (username,)).fetchone()[-1]
                if prev_response == "" or prev_response is None:
                    cur_response = {}
                else:
                    cur_response = literal_eval(prev_response)
                cur_response[feed_type] = response
                result_list = [str(cur_response), username]
                self.cursor.execute(self.update_string, result_list)
                self.connection.commit()
                self.connection.close()
                logger.info(
                    f"Successfully updated table corresponding to user: {username}")
                return True
            else:
                logger.info("Unable to update database: ")
                return False
        except Exception as e:
            logger.info("Unable to update database: "+str(e))
            return False

    def insert_entry(self, username, password):
        try:
            self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
            self.cursor = self.connection.cursor() 
            response = self.cursor.execute(self.check_string +
                                           " WHERE username=?", (username,)).fetchone()
            if response:
                return False

            self.cursor.execute(self.insert_string,
                                (username, password, None))
            self.connection.commit()
            self.connection.close()
            logger.info("Successfully inserted entry: " + str(username))
            return True
        except Exception as e:
            logger.info("Error inserting entry: " + str(e))
            return False

    def check_database(self):
        self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
        self.cursor = self.connection.cursor() 
        response = self.cursor.execute(self.check_string).fetchall()
        for row in response:
            logger.info(row)
        self.connection.close()  

    def getUser(self, name='*'):
        self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
        self.cursor = self.connection.cursor() 
        check_string = f"""SELECT role FROM {self.table_name} where username ='{name}'"""
        response = self.cursor.execute(check_string).fetchall()
        out = ""
        for row in response:
            logger.info(row)
            out = row
        self.connection.close()    
        return out[0]   


# TODO: Implement both classes
class StudentDatabase:
    def __init__(self, db_name, table_name):
        try:
            logger.info("Connecting to sqlite database with name: " + db_name)
            # self.connection = sqlite3.connect(
            #     db_name,  check_same_thread=False)
            self.table_name = table_name
            logger.info("Connecting established successfully: " + table_name)
        except Exception as e:
            logger.info("Error connecting to database: " + str(e))
        # self.cursor = self.connection.cursor()
        self.db_name = db_name
        self.check_string = f"""SELECT * FROM {self.table_name}"""
        self.query_string = f"""SELECT * FROM {self.table_name} WHERE email=? and type=?"""
        self.insert_string = f"""INSERT INTO {self.table_name} (name, email, type, status) VALUES(?,?,?,?)"""
        self.update_string = f"""UPDATE {self.table_name} SET status=?, type=? where name=? and email=?"""
        self.delete_string = f"""DELETE FROM {self.table_name} WHERE name=? and email=?"""

    def validate(self, name, type):
        self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
        self.cursor = self.connection.cursor() 
        response = self.cursor.execute(
            self.query_string, (name, type)).fetchone()
        print("Validation successful for username: " + str(name))
        print(response)
        self.connection.close()
        # return True if response else False
        if response:
            if int(response[-1]) != 2:
                return True
        return False    


    def update_entry(self, name, email, type, status='1'):
        try:
            self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
            self.cursor = self.connection.cursor() 
            if name is None:
                result_list = [status, email, type]
                self.cursor.execute(
                    f"""UPDATE {self.table_name} SET status=? where email=? and type=?""", result_list)
                self.connection.commit()
                logger.info(
                    f"Successfully updated table corresponding to user: {name}")
                return True
            if email is None:
                result_list = [status, name, type]
                self.cursor.execute(
                    f"""UPDATE {self.table_name} SET status=? where name=? and type=?""", result_list)
                self.connection.commit()
                logger.info(
                    f"Successfully updated table corresponding to user: {name}")
                return True
            if name is not None and email is not None and type is not None:
                result_list = [status, type, name, email]
                print("####", result_list)
                self.cursor.execute(self.update_string, result_list)
                self.connection.commit()
                self.connection.close()
                logger.info(
                    f"Successfully updated table corresponding to user: {name}")
                return True

            else:
                logger.info("Unable to update database: ")
                return False
        except Exception as e:
            logger.info("Unable to update database: "+str(e))
            return False

    def insert_entry(self, name, email, type, status='0'):
        try:
            self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
            self.cursor = self.connection.cursor() 
            self.cursor.execute(self.insert_string,
                                (name, email, type, status))
            self.connection.commit()
            self.connection.close()
            logger.info("Successfully inserted entry: " + str(name))
        except Exception as e:
            logger.info("Error inserting entry: " + str(e))

    def delete_entry(self, name, email):
        try:
            self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
            self.cursor = self.connection.cursor() 
            self.cursor.execute(self.delete_string, (name, email))
            self.connection.commit()
            self.connection.close()
            logger.info("Successfully deleted entry: " + str(name))
        except Exception as e:
            logger.info("Error deleting entry: " + str(e))

    def check_database(self):
        self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
        self.cursor = self.connection.cursor() 
        response = self.cursor.execute(self.check_string).fetchall()
        out = {}  # name: email
        for row in response:
            logger.info(row)
            out[row[1]] = row[2]
        self.connection.close()    
        return out

    def query(self, name, type):
        self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
        self.cursor = self.connection.cursor() 
        base_query = self.query_string
        response = self.cursor.execute(base_query, (name, type,)).fetchone()
        print("*******", response)
        self.connection.close()
        return True if response else False

    def fetch(self, name, to_fetch):
        self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
        self.cursor = self.connection.cursor() 
        base_query = f"select {to_fetch}, status from {self.table_name} where email=?"
        response = self.cursor.execute(base_query, (name,)).fetchall()
        print("*******", response)
        self.connection.close()
        return response

    def getAllFeedback(self, type='', col='*'):
        self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
        self.cursor = self.connection.cursor() 
        check_string = f"""SELECT type,status FROM {self.table_name} where email ='{col}'"""
        response = self.cursor.execute(check_string).fetchall()
        out = []
        for row in response:
            logger.info(row)
            out.append(row)
        self.connection.close()    
        return out    


class QuestionDatabase:
    def __init__(self, db_name, table_name):
        try:
            logger.info("Connecting to sqlite database with name: " + db_name)
            # self.connection = sqlite3.connect(
            #     db_name,  check_same_thread=False)
            self.table_name = table_name
            self.db_name = db_name
            logger.info("Connection established successfully: " + table_name)
        except Exception as e:
            logger.info("Error connecting to database: " + str(e))
        # self.cursor = self.connection.cursor()
        self.check_string = f"""SELECT * FROM {self.table_name}  WHERE type=?"""
        self.insert_string = f"""INSERT INTO {self.table_name} (questions, type) VALUES(?,?)"""
        self.update_string = f"""UPDATE {self.table_name} SET questions=?, type=? WHERE id=?"""
        self.delete_string = f"""DELETE FROM {self.table_name} WHERE id?"""

    def update_entry(self, question, type, id):
        try:
            self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
            self.cursor = self.connection.cursor() 
            if question is not None and type is not None and id is not None:
                result_list = [question, type, id]
                self.cursor.execute(self.update_string, result_list)
                self.connection.commit()
                self.connection.close()
                logger.info(
                    f"Successfully updated table corresponding to id: {id}")
                return True
            else:
                logger.info("Unable to update database: ")
                return False
        except Exception as e:
            logger.info("Unable to update database: "+str(e))
            return False

    def insert_entry(self, question, type):
        self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
        self.cursor = self.connection.cursor() 
        try:
            self.cursor.execute(self.insert_string,
                                (question, type))
            self.connection.commit()
            self.connection.close()
            logger.info("Successfully inserted entry: " +
                        str(question) + " ->" + str(type))
        except Exception as e:
            logger.info("Error inserting entry: " + str(e))

    def delete_entry(self, id):
        self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
        self.cursor = self.connection.cursor() 
        try:
            if id is not None:
                self.cursor.execute(self.delete_string, (id))
                self.connection.commit()
                self.connection.close()
                logger.info("Successfully deleted entry: " + str(id))
            else:
                logger.info("Error deleting entry: " + str(id))
        except Exception as e:
            logger.info("Error deleting entry: " + str(e))

    def check_database(self, type='', col='*'):
        print(" inside check_database")
        self.connection = sqlite3.connect(self.db_name,  check_same_thread=False)
        self.cursor = self.connection.cursor() 
        check_string = f"""SELECT {col} FROM {self.table_name}"""
        print(check_string , type)
        if type != '':
            response = self.cursor.execute(
                self.check_string, (type,)).fetchall()
        elif col == '*':
            response = self.cursor.execute(self.check_string.replace(
                '  WHERE type=?', '')).fetchall()
        else:
            check_string = f"""SELECT id, {col} FROM {self.table_name}"""
            response = self.cursor.execute(check_string).fetchall()
        out = []
        print(check_string , type)
        for row in response:
            logger.info(row)
            out.append(row[1])
        print(out)    
        self.connection.close()    
        return out


if __name__ == "__main__":
    obj = StudentDatabase("databases/database.db", "student_table")
    # logger.info(obj.validate("sid", "123876"))
    # obj.insert_entry("gola", '0989')
    # obj.insert_entry('hello', "hello@gmail.com", "exam", "0")
    # obj.check_database()
    # print("------------------")
    # obj.update_entry('hello', 'hello@gmail.com', 'exam', status='1')
    print(obj.check_database())
    print(obj.fetch("naruto@gmail.com"))
    # print(obj.validate(name='b@gmail.com', type='Exam'))
    print("----------------")
    """obj.delete_entry('hello', 'hello@gmail.com')
    obj.check_database()"""

    # obj.check_database()
    # print("----------------")
    # obj.insert_entry(question='why are you?', type='Exam')
    # obj.insert_entry(question='jump jump?', type='Exam')
    # obj.insert_entry(question='why are you running?', type='Exam')
    # obj.update_entry('who are pizza?', 'Exam', 2)
    # obj.delete_entry(5)
    # obj.check_database()
    # print("----------------")

    # obj = StudentDatabase("databases/database.db", "student_table")
    # print(obj.check_database())
