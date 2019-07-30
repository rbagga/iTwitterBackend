# piazza.py


from piazza_api import Piazza
from logger import logger
import datetime

p = Piazza()

def piazzaLogin(netid, passwd=""):
    try:
        p.user_login(netid+"@illinois.edu", passwd)
    except:
        return False
    return True

def piazzaMigration(questions, networkid, netid, passwd):
    if questions is None or not networkid or not netid or not passwd:
        logger.debug("piazzaMigration failure: one of the fields is empty")
        return
    p.user_login(netid+"@illinois.edu", passwd)
    course = p.network(networkid)
    course.create_post('question', ('folder to put into', 'another folder'), 'Lecture Question Overflow: '+str(datetime.datetime.now().month)+'/'+str(datetime.datetime.now().day), "post content", False, False, False)

    # test
    #p.user_login()
    #course = p.network("jvl5vt2p49j72t")
    #course.create_post('question', ('project', 'other'), 'IGNORE: wasted potentials piazza api test', "post body", False, False, False)
