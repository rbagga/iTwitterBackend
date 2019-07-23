# create_db.py


from app import db
import psycopg2
from config import BaseConfig

def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE login_details (
        netid VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        UIN INTEGER
        )
        """ ,
        """
        CREATE TABLE courses (
        course_number VARCHAR(255),
        term VARCHAR(255),
        title VARCHAR(255),
        instructor VARCHAR(255),
        PRIMARY KEY(course_number, term)
        )
        """,
        """
        CREATE TABLE faculty (
        netid VARCHAR(255),
        dept VARCHAR(255),
        office_number INTEGER,
        term VARCHAR(255),
        course_number VARCHAR(255),
        PRIMARY KEY(netid, term),
        FOREIGN KEY (course_number, term)
        REFERENCES courses (course_number, term)
        ON DELETE CASCADE,
        FOREIGN KEY(netid)
        REFERENCES login_details(netid)
        ON UPDATE CASCADE
        ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE students (
        netid VARCHAR(255) PRIMARY KEY,
        dept VARCHAR(255),
        year VARCHAR(255),
        FOREIGN KEY(netid)
        REFERENCES login_details(netid)
        ON UPDATE CASCADE
        ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE s_take (
        netid VARCHAR(255),
        course_number VARCHAR(255),
        term VARCHAR(255),
        PRIMARY KEY(netid, course_number, term)
        )
        """,
        """
        CREATE TABLE piazza (
        q_number INTEGER,
        date_posted TIMESTAMP without TIME ZONE NOT NULL,
        course VARCHAR(255),
        up_votes INTEGER,
        sub_group VARCHAR(255),
        PRIMARY KEY(q_number, date_posted, course)
        ) """
        #create more tables below as necessary looking at the Relational Schema
    )

    conn = None
    try:
        #DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
        params = BaseConfig()
        host_ = params.DB_SERVICE
        port_ = params.DB_PORT
        database_ = params.DB_NAME
        user_ = params.DB_USER
        password_ = params.DB_PASS
        conn = psycopg2.connect(host=host_, database=database_, user=user_, password=password_, port=port_)

        cur = conn.cursor()

        for command in commands:
                cur.execute(command)

        cur.close()
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()



create_tables()
#will not need this afterwards
db.create_all()

#     create_tables()
