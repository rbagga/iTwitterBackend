# transaction.py

from sqlalchemy import text
from app import db


# how to restart a transaciton
# while True:
#   try:
#        ts = startTransaction()
#        all the queries, setting readTS or writeTS to ts
#             before reads, update the read TS of the exact same query second, first do the read query
#             example: read:
#               select from Bags that are red
#               update Bags that are red with readTS = ts, writeTS = null
#             example: write:
#               update Bags that are red with writeTS = ts, readTS = null
#        endTransaction()
#   except:
#        pass
#   else:
#        break


# Lock the timestamp table while we get and increment the next available timestamp.
# The timestamp MUST be unique for every transaction.
def getTimestamp():
    begin = text('BEGIN')
    db.engine.execute(begin)
    setTS = text('SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED')
    db.engine.execute(setTS)

    lockTimestamp = text('LOCK TABLE timestamp IN ACCESS EXCLUSIVE')
    db.engine.execute(lockTimestamp)

    queryTimestamp = text('SELECT nextAvailable FROM timestamp')
    ts = db.engine.execute(queryTimestamp).fetchone()

    incTimestamp = text('UPDATE timestamp SET nextAvailable = :tsInc')
    db.engine.execute(incTimestamp, tsInc = ts + 1)

    end = text('COMMIT')
    db.engine.execute(end)
    return ts

def startTransaction():
    ts = getTimestamp()
    begin = text('BEGIN')
    db.engine.execute(begin)
    setTS = text('SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED')
    db.engine.execute(setTS)
    return ts


def endTransaction():
  end = text('COMMIT')
  db.engine.execute(end)