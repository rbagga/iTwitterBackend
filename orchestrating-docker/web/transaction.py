# transaction.py

from sqlalchemy import text
from app import db

# Lock the timestamp table while we get and increment the next available timestamp.
# The timestamp MUST be unique for every transaction.
def getTimestamp():
    begin = text('BEGIN')
    db.engine.execute(begin)

    lockTimestamp = text('LOCK TABLE Timestamp IN ACCESS EXCLUSIVE')
    db.engine.execute(lockTimestamp)

    queryTimestamp = text('SELECT NextAvailable FROM Timestamp')
    ts = db.engine.execute(queryTimestamp).fetchone()

    incTimestamp = text('UPDATE Timestamp SET NextAvailable = :tsInc')
    db.engine.execute(incTimestamp, tsInc = ts + 1)

    end = text('COMMIT')
    db.engine.execute(end)
    return ts

def startTransaction():
    ts = getTimestamp()
    begin = text('BEGIN')
    db.engine.execute(begin)
    return ts


def endTransaction():
  end = text('COMMIT')
  db.engine.execute(end)