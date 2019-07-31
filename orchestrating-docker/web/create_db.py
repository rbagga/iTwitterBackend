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
        CREATE TABLE courses (
        course_number VARCHAR(255),
        term VARCHAR(255),
        title VARCHAR(255),
        instructor VARCHAR(255),
        instructor_netid VARCHAR(255),
        piazza_nid VARCHAR(255) DEFAULT NULL,
        piazza_netid VARCHAR(255) DEFAULT NULL,
        piazza_passwd VARCHAR(255) DEFAULT NULL,
        readts INTEGER NOT NULL DEFAULT 0,
        writets INTEGER NOT NULL DEFAULT 0,
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
        readts INTEGER NOT NULL DEFAULT 0,
        writets INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(netid, term, course_number),
        FOREIGN KEY (course_number, term)
        REFERENCES courses (course_number, term)
        ON DELETE CASCADE
        -- FOREIGN KEY(netid)
        -- REFERENCES login_details(netid)
        -- ON UPDATE CASCADE
        -- ON DELETE CASCADE
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
        readts INTEGER NOT NULL DEFAULT 0,
        writets INTEGER NOT NULL DEFAULT 0
        -- FOREIGN KEY(netid)
        -- REFERENCES login_details(netid)
        -- ON UPDATE CASCADE
        -- ON DELETE CASCADE
        )
        """
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

# def insert_login_details(login_list):
#      """ insert multiple vendors into the vendors table  """
#      sql = "INSERT INTO login_details(netid, firstname, lastname, email) VALUES(%s, %s, %s, %s)"

#      conn = None
#      try:
#          params = BaseConfig()
#          host_ = params.DB_SERVICE
#          port_ = params.DB_PORT
#          database_ = params.DB_NAME
#          user_ = params.DB_USER
#          password_ = params.DB_PASS
#          conn = psycopg2.connect(host=host_, database=database_, user=user_, password=password_, port=port_)

#          cur = conn.cursor()
#          cur.executemany(sql, login_list)
#          conn.commit()
#          cur.close()

#      except (Exception, psycopg2.DatabaseError) as error:
#         print(error)

#      finally:
#         if conn is not None:
#             conn.close()

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
     sql = "INSERT INTO faculty(netid, firstname, lastname, email, term, course_number) VALUES(%s, %s, %s, %s, %s, %s)"

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

def insert_courses(login_list):
     """ insert multiple vendors into the vendors table  """
     sql = "INSERT INTO courses(course_number, instructor, term, title, instructor_netid) VALUES(%s, %s, %s, %s, %s)"

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

def insert_abdu_course(login_list):
     """ insert multiple vendors into the vendors table  """
     sql = "INSERT INTO courses(course_number, term, title, instructor, instructor_netid, piazza_nid) VALUES(%s, %s, %s, %s, %s, %s)"

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

def insert_abdu(login_list):
     """ insert multiple vendors into the vendors table  """
     sql = "INSERT INTO faculty(netid, firstname, lastname, email, dept, term, course_number) VALUES(%s, %s, %s, %s, %s, %s, %s)"

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

# def insert_abdu_login(login_list):
#      """ insert multiple vendors into the vendors table  """
#      sql = "INSERT INTO login_details(netid, firstname, lastname, email) VALUES(%s, %s, %s, %s)"

#      conn = None
#      try:
#          params = BaseConfig()
#          host_ = params.DB_SERVICE
#          port_ = params.DB_PORT
#          database_ = params.DB_NAME
#          user_ = params.DB_USER
#          password_ = params.DB_PASS
#          conn = psycopg2.connect(host=host_, database=database_, user=user_, password=password_, port=port_)

#          cur = conn.cursor()
#          cur.executemany(sql, login_list)
#          conn.commit()
#          cur.close()

#      except (Exception, psycopg2.DatabaseError) as error:
#         print(error)

#      finally:
#         if conn is not None:
#             conn.close()

def create_concurrency_triggers():  #### may still need to write an insert trigger
    """ create concurrency triggers for all sql tables  """
    commands = (
        """
        CREATE OR REPLACE FUNCTION trigger_update_timestamp()
        RETURNS  trigger AS $$
        BEGIN
            -- RAISE NOTICE 'Checking ability to read/write';
            IF NEW.readts IS NULL THEN
            RAISE NOTICE 'Checking for ability to write';
            IF OLD.writets>NEW.writets OR OLD.readts>NEW.writets THEN
            RAISE EXCEPTION 'UPDATE concurrency: row has been read or written to by a more recent transaction';
            ELSE
            NEW.readts = OLD.readts;
            END IF;
            ELSEIF NEW.writets IS NULL THEN
            RAISE NOTICE 'Checking for ability to read';
            IF OLD.writets>NEW.readts THEN
            RAISE EXCEPTION 'READ concurrency: row has been written to by a more recent transaction with timestamp %', OLD.writeTS;
            ELSE
            IF OLD.readts>NEW.readts THEN
            NEW.readts = OLD.readts;
            END IF;
            NEW.writets = OLD.writets;
            END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
        """
        CREATE TRIGGER update_timestamp
        BEFORE UPDATE
        ON timestamptest
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_update_timestamp();
        """,
        """
        CREATE TRIGGER update_timestamp
        BEFORE UPDATE
        ON courses
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_update_timestamp();
        """,
        """
        CREATE TRIGGER update_timestamp
        BEFORE UPDATE
        ON faculty
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_update_timestamp();
        """,
        """
        CREATE TRIGGER update_timestamp
        BEFORE UPDATE
        ON students
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_update_timestamp();
        """,
        """
        CREATE TRIGGER update_timestamp
        BEFORE UPDATE
        ON session
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_update_timestamp();
        """,
        """
        CREATE TRIGGER update_timestamp
        BEFORE UPDATE
        ON question
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_update_timestamp();
        """,
        """
        CREATE TRIGGER update_timestamp
        BEFORE UPDATE
        ON upvotes
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_update_timestamp();
        """,
        """
        CREATE TRIGGER update_timestamp
        BEFORE UPDATE
        ON iclickerresponse
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_update_timestamp();
        """,
        """
        CREATE TRIGGER update_timestamp
        BEFORE UPDATE
        ON enrollment
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_update_timestamp();
        """,
        """
        CREATE TRIGGER update_timestamp
        BEFORE UPDATE
        ON iclickerresponse
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_update_timestamp();
        """
    )

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

        for command in commands:
                cur.execute(command)

        cur.close()
        conn.commit()

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

filename_3 = 'ece_cs_faculty_term_course_added.csv'
login_list_3 = sql_list(filename_3)
login_list_3.pop(0)

filename_4 = 'ece_cs_courses.csv'
login_list_4 = sql_list(filename_4)
login_list_4.pop(0)

create_tables()
#will not need this afterwards
db.create_all()

#insert_login_details(login_list)
#insert_login_details(login_list_2)
insert_students(login_list)
insert_faculty(login_list_3)
insert_courses(login_list_4)
login_list_7 = [('alawini', 'Abdussalam', 'Alawini', 'alawini@illinois.edu')]
#insert_abdu_login(login_list_7)
login_list_6 = [('CS-411', '2019-su', 'Database System', 'Alawini, Abdussalam', 'alawini', 'jvl5vt2p49j72t')]
insert_abdu_course(login_list_6)
login_list_5 = [('alawini', 'Abdussalam', 'Alawini', 'alawini@illinois.edu', 'CS', '2019-su', 'CS-411')]
insert_abdu(login_list_5)


create_concurrency_triggers()

# insert_faculty(login_list_2)
#     create_tables()
