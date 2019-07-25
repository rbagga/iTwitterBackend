# create_db.py


from app import db
import psycopg2
import os
from config import BaseConfig
from dataset_to_sql import *

def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE login_details (
        netid VARCHAR(255) PRIMARY KEY,
        firstname VARCHAR(255) NOT NULL,
        lastname VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        UIN INTEGER DEFAULT NULL
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
        firstname VARCHAR(255) NOT NULL,
        lastname VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        dept VARCHAR(255) DEFAULT 'ECE',
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
        firstname VARCHAR(255) NOT NULL,
        lastname VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        dept VARCHAR(255) DEFAULT 'ECE',
        year VARCHAR(255) DEFAULT 'Grad',
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

def insert_login_details(login_list):
     """ insert multiple vendors into the vendors table  """
     sql = "INSERT INTO login_details(netid, firstname, lastname, email) VALUES(%s, %s, %s, %s)"

     conn = None
     try:
         params = BaseConfig()
         host_ = params.DB_SERVICE
         port_ = params.DB_PORT
         database_ = params.DB_NAME
         user_ = params.DB_USER
         password_ = params.DB_PASS
         conn = psycopg2.connect(host=host_, database=database_, user=user_, password=password_, port=port_)

         cur = conn.cursor()
         cur.executemany(sql, login_list)
         conn.commit()
         cur.close()

     except (Exception, psycopg2.DatabaseError) as error:
        print(error)

     finally:
        if conn is not None:
            conn.close()

def insert_students(login_list):
     """ insert multiple vendors into the vendors table  """
     sql = "INSERT INTO students(netid, firstname, lastname, email) VALUES(%s, %s, %s, %s)"

     conn = None
     try:
         params = BaseConfig()
         host_ = params.DB_SERVICE
         port_ = params.DB_PORT
         database_ = params.DB_NAME
         user_ = params.DB_USER
         password_ = params.DB_PASS
         conn = psycopg2.connect(host=host_, database=database_, user=user_, password=password_, port=port_)

         cur = conn.cursor()
         cur.executemany(sql, login_list)
         conn.commit()
         cur.close()

     except (Exception, psycopg2.DatabaseError) as error:
        print(error)

     finally:
        if conn is not None:
            conn.close()

def insert_faculty(login_list):
     """ insert multiple vendors into the vendors table  """
     sql = "INSERT INTO faculty(netid, firstname, lastname, email) VALUES(%s, %s, %s, %s)"

     conn = None
     try:
         params = BaseConfig()
         host_ = params.DB_SERVICE
         port_ = params.DB_PORT
         database_ = params.DB_NAME
         user_ = params.DB_USER
         password_ = params.DB_PASS
         conn = psycopg2.connect(host=host_, database=database_, user=user_, password=password_, port=port_)

         cur = conn.cursor()
         cur.executemany(sql, login_list)
         conn.commit()
         cur.close()

     except (Exception, psycopg2.DatabaseError) as error:
        print(error)

     finally:
        if conn is not None:
            conn.close()


filename = 'ece_grad_students_netid_added.csv'
login_list = sql_list(filename)
login_list.pop(0)

filename_2 = 'ece_faculty_netid_added.csv'
login_list_2 = sql_list(filename_2)
login_list_2.pop(0)

create_tables()
#will not need this afterwards
db.create_all()

insert_login_details(login_list)
insert_login_details(login_list_2)
insert_students(login_list)
# insert_faculty(login_list_2)
#     create_tables()
