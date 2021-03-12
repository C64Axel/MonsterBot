dbversion = 1

def check_db_version(cursor):
        cursor.execute("select version from dbversion")
        result = cursor.fetchone()
        return result[0]

def db_need_update(cursor):
        version = check_db_version(cursor)
        if version < dbversion:
                return 1
        else:
                return 0
