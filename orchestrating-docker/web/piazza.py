# piazza.py


from piazza_api import Piazza
import datetime

p = Piazza()

def piazzaLogin(netid, passwd=""):
    try:
        p.user_login(netid+"@illinois.edu", passwd)
    except:
        return False
    return True

def piazzaMigration(questions="", networkid="", netid="", passwd=""):
    # if questions, netid, networkid, or password are empty return
    # else:
    #p.user_login(netid+"@illinois.edu", passwd)
    p.user_login() #test

    #course = p.network(networkid)
    course = p.network("jvl5vt2p49j72t") #test

    d = datetime.datetime.today()

    #course.create_post('question', ('folder to put into', 'another folder'), 'Lecture Question Overflow: ',d.month+'/'+d.day, "post content", False, False, False)
    course.create_post('question', ('project', 'other'), 'IGNORE: wasted potentials piazza api test', "post body", False, False, False) #test
