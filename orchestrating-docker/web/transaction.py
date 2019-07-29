# transaction.py

from sqlalchemy import text
from app import db


# how to restart a transaciton
# while True:
#   try:
#        ts = startTransaction()
#        all the queries, setting readts or writets to ts
#             before reads, update the read TS of the exact same query second, first do the read query
#             example: read:
#               select from Bags that are red
#               update Bags set readts = ts, writets = NULL where <read query where>
#             example: write:
#               update Bags set <write action>, writets = ts, readts = NULL where <write query where>
#        endTransaction()
#   except:
#        pass
#   else:
#        break

# def concurrencyStart():
#     # set a single value in timestamp table to 0
#     checkts = text('SELECT nextavailable FROM timestamp')
#     if db.engine.execute(checkts).fetchone() is None:
#       createts = text('INSERT INTO timestamp VALUES (0)')
#       db.engine.execute(createts)
#     else:
#       resetts = text('UPDATE timestamp SET nextavailable=0')
#       db.engine.execute(resetts)

def getTimestamp():
    # Lock the timestamp table while we get and increment the next available timestamp.
    # The timestamp MUST be unique for every transaction.
    begin = text('BEGIN')
    db.engine.execute(begin)
    setTS = text('SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED')
    db.engine.execute(setTS)

    lockTimestamp = text('LOCK TABLE timestamp IN ACCESS EXCLUSIVE MODE')
    db.engine.execute(lockTimestamp)

    queryTimestamp = text('SELECT nextavailable FROM timestamp')
    ts = db.engine.execute(queryTimestamp).fetchone()
    if ts is None:
      createts = text('INSERT INTO timestamp VALUES (0)')
      db.engine.execute(createts)
      ts = 0

    incTimestamp = text('UPDATE timestamp SET nextavailable = :tsInc')
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