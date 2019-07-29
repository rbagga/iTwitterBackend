# piazza.py


from piazza_api import Piazza


p = Piazza()

def piazzaLogin(netid, passwd=""):
    try:
        p.user_login(netid+"@illinois.edu", passwd)
    except:
        return False
    return True
