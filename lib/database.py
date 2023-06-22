import sqlite3

class Database:
    def __init__(self):
        with sqlite3.connect("sokoban.db") as connexion:
            db = connexion.cursor()
            db.execute("CREATE TABLE IF NOT EXISTS levels (level INT, maxLevel INT)")
            connexion.commit()

    def save(self, level, maxLevel):
        with sqlite3.connect("sokoban.db") as connexion:
            db = connexion.cursor()
            db.execute("SELECT * FROM levels")
            ret = len(db.fetchall())

            if ret > 0: db.execute("UPDATE levels SET level = {}, maxLevel = {}".format(level, maxLevel))
            else: db.execute("INSERT INTO levels VALUES ({}, {})".format(level, maxLevel))

            connexion.commit()

        
    def get(self):
        with sqlite3.connect("sokoban.db") as connexion:
            db = connexion.cursor()
            db.execute("SELECT * FROM levels")
            ret = db.fetchall()

            if len(ret) > 0: return (ret[0][0], ret[0][1])
            else: return (1, 1)

