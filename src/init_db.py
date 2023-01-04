import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_user_table():
    connection = sqlite3.connect('databases/database.db')

    f = """
    DROP TABLE IF EXISTS user;

    CREATE TABLE user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        response TEXT NULL
    );
    """
    connection.executescript(f)

    cur = connection.cursor()

    cur.execute("INSERT INTO user (username, password, response) VALUES (?, ?,?)",
                ('sid', '123', '')
                )

    cur.execute("INSERT INTO user (username, password, response) VALUES (?, ?,?)",
                ('sid0911', '12345', '')
                )

    connection.commit()
    logger.info(cur.execute("select * from user").fetchall())
    connection.close()


def make_question_table():
    connection = sqlite3.connect('databases/database.db')

    f = """
    DROP TABLE IF EXISTS question_table;

    CREATE TABLE question_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        questions TEXT NOT NULL,
        type TEXT NOT NULL
    );
    """
    connection.executescript(f)

    cur = connection.cursor()

    cur.execute("INSERT INTO question_table (questions, type) VALUES (?,?)",
                ('what is you?', 'Exam')
                )

    cur.execute("INSERT INTO question_table (questions, type) VALUES (?,?)",
                ('How is you?', 'TEST')
                )
    cur.execute("INSERT INTO question_table (questions, type) VALUES (?,?)",
                ('Where is you?', 'TEST')
                )

    cur.execute("INSERT INTO question_table (questions, type) VALUES (?,?)",
                ('When is you?', 'TEST')
                )

    connection.commit()
    logger.info(cur.execute("select * from question_table").fetchall())
    connection.close()


def make_student_table():
    connection = sqlite3.connect('databases/database.db')

    f = """
    DROP TABLE IF EXISTS student_table;

    CREATE TABLE student_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        type TEXT NOT NULL,
        status TEXT NOT NULL
    );
    """
    connection.executescript(f)

    cur = connection.cursor()

    cur.execute("INSERT INTO student_table (name, email, type, status) VALUES (?,?,?,?)",
                ('sid', 'rsiddhant73@gmail.com', 'exam', '0')
                )

    cur.execute("INSERT INTO student_table (name, email, type, status) VALUES (?,?,?,?)",
                ('ronaldo', 'sidlovesml@gmail.com', 'exam', '0')
                )
    cur.execute("INSERT INTO student_table (name, email, type, status) VALUES (?,?,?,?)",
                ('test', 'testingid0911@gmail.com', 'feed', '0')
                )

    connection.commit()
    logger.info(cur.execute("select * from student_table").fetchall())
    connection.close()


if __name__ == "__main__":
    pass
    # make_user_table()
    # make_question_table()
    # make_student_table()
