import sqlite3
from datetime import datetime, timedelta

import bot_init
from bot_init import DB_NAME
USERID_IDX = 0
USERNAME_IDX = 1
USERGROUP_IDX = 2
ISADMIN_IDX = 3
SCHEDULE_TIME_IDX = 2
SCHEDULE_EVENT_IDX = 3


def create_db():
    connector = sqlite3.connect(DB_NAME)
    cursor = connector.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            user_group TEXT,
            is_admin INTEGER,
            morning_notifications INTEGER,
            lessons_notifications INTEGER,
            activities_notifications INTEGER,
            premium_sub INTEGER
        );
        
        CREATE TABLE IF NOT EXISTS schedule(
            group_name TEXT NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            event TEXT,
            warning INTEGER,
            suggestion TEXT,
            PRIMARY KEY (group_name,day)
        );
    ''')
    connector.commit()

    connector = sqlite3.connect(DB_NAME)
    cursor = connector.cursor()
    try:
        cursor.execute(f"INSERT INTO users VALUES(?,?,?,?,?,?,?,?)",
                       (765194149, "alexmeshr", None, 1, 0, 0, 0, 0))
        connector.commit()
    except Exception as e:
        print(e)
        print("Already exists")
    connector.close()


def get_users(user_id: int = None):
    """
        user_id: id of user

        returns a list of users info

        return: [(user_id:INT, username:TEXT, group:TEXT, is_admin:INT),...]
    """
    res = None
    connector = sqlite3.connect(DB_NAME)
    cursor = connector.cursor()
    try:
        if user_id is None:
            cursor.execute("SELECT * FROM users "
                           "WHERE user_id > 0")
        else:
            cursor.execute("SELECT * FROM users "
                           "WHERE user_id = ?", (user_id, ))
        res = cursor.fetchall()
    except Exception as e:
        print(e)
    connector.close()
    if res is not None:
        for i in range(len(res)):
            res[i] = list(res[i])
    return res


def add_user(user_id:int, username:str, user_group:str = None, is_admin:int = 0):
    """
        Adds a new user

    """
    try:
        connector = sqlite3.connect(DB_NAME)
        cursor = connector.cursor()
        cursor.execute("SELECT COUNT(user_id) FROM users WHERE user_id = ?", (user_id,))
        is_exist = cursor.fetchone()[0]
        if is_exist == 0:
            cursor.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?)", (user_id, username, user_group, is_admin, 0,0,0,0))
            connector.commit()
            connector.close()
        else:
            connector.close()
            #upd_user(user_id=user_id, username=username)
    except Exception as e:
        print(e)
        print(f"ERROR(add_users): Can't INSERT INTO users ({user_id}, {username})")


def upd_user(user_id, username = None, user_group = None, is_admin = None):
    """
        Updates user info
    """
    q = ""
    data = ()
    if username is not None:
        q = q+" username = ?,"
        data = data.__add__((username,))
    if user_group is not None:
        q = q+" user_group = ?,"
        data = data.__add__((user_group,))
    if is_admin is not None:
        q = q+" is_admin = ?,"
        data = data.__add__((is_admin,))
    data = data.__add__((user_id,))
    q = q[:-1]
    try:
        connector = sqlite3.connect(DB_NAME)
        cursor = connector.cursor()
        print("UPDATE users SET "+q+" WHERE user_id = ?")
        cursor.execute("UPDATE users SET "+q+" WHERE user_id = ?", data)
        connector.commit()
        connector.close()
    except Exception as e:
        print(e)
        print(f"ERROR(upd_user): Can't UPDATE user in users ({user_id}, {username}, {user_group}, {is_admin})")


def upd_subscriptions(user_id, morning_notifications = None, lessons_notifications = None,
                      activities_notifications = None, premium_sub = None):
    """
        Updates user info
    """
    q = ""
    data = ()
    if morning_notifications is not None:
        q = q+" morning_notifications = ?,"
        data = data.__add__((morning_notifications,))
    if lessons_notifications is not None:
        q = q+" lessons_notifications = ?,"
        data = data.__add__((lessons_notifications,))
    if activities_notifications is not None:
        q = q+" activities_notifications = ?,"
        data = data.__add__((activities_notifications,))
    if premium_sub is not None:
        q = q+" premium_sub = ?,"
        data = data.__add__((premium_sub,))
    data = data.__add__((user_id,))
    q = q[:-1]
    try:
        connector = sqlite3.connect(DB_NAME)
        cursor = connector.cursor()
        cursor.execute("UPDATE users SET "+q+" WHERE user_id = ?", data)
        connector.commit()
        connector.close()
    except Exception as e:
        print(e)
        print(f"ERROR(upd_user): Can't UPDATE sub in users ({user_id})")


def get_ids():
    connector = sqlite3.connect(DB_NAME)
    cursor = connector.cursor()
    cursor.execute("SELECT user_id FROM users")
    res = cursor.fetchall()
    connector.close()
    return res


def check_admin(user_id):
    res = False
    connector = sqlite3.connect(DB_NAME)
    cursor = connector.cursor()
    try:
        cursor.execute("SELECT is_admin FROM users "
                           "WHERE user_id = ?", (user_id,))
        res = (1 in cursor.fetchall()[0])
    except Exception as e:
        print(e)
    connector.close()
    return res


def append_schedule(cursor, group_name, day, time):
    pass

"""
        CREATE TABLE IF NOT EXISTS schedule(
            group_name TEXT NOT NULL,
            day INTEGER NOT NULL,
            time TEXT NOT NULL,
            event TEXT,
            warning INTEGER,
            suggestion TEXT,
            PRIMARY KEY (group_name,day)
"""

def update_schedule_table(schedule_array):
    connector = sqlite3.connect(DB_NAME)
    cursor = connector.cursor()
    first_day = next(iter(schedule_array))
    try:
        cursor.execute("DELETE FROM schedule WHERE day < ?", (first_day,))
        connector.commit()
    except Exception as e:
        print(e)
        print(f"ERROR(update_schedule_table): Can't DELETE from schedule_table")
    for day in schedule_array:
        starting_day = datetime.now().date().replace(month=1, day=1)
        date = starting_day + timedelta(days=int(day-1))
        day_schedule = schedule_array[day]
        for group_name in day_schedule:
            for t in bot_init.times:
                content = day_schedule[group_name][t.replace("-", "").replace(" ", "")]
                event = ""
                for c in content:
                    event+=c[0]+"\n"
                #if event != "":
                #    print(date, group_name, t, event)
                try:
                    cursor.execute("SELECT COUNT(day) FROM schedule WHERE day = ? AND group_name = ?", (day,group_name))
                    is_exist = cursor.fetchone()[0]
                    if is_exist == 0:
                        cursor.execute("INSERT INTO schedule VALUES (?,?,?,?,?,?)",
                                       (group_name, day, t, event, 0, None))
                        connector.commit()
                    else:
                        cursor.execute("UPDATE schedule SET event = ? WHERE day = ? AND group_name = ?", (event, day,group_name))
                        connector.commit()

                except Exception as e:
                    print(e)
                    print(f"ERROR(update_schedule_table): Can't UPDATE schedule_table")
    connector.close()



def get_schedule_for_days(days, group_name):
    res = {}
    connector = sqlite3.connect(DB_NAME)
    cursor = connector.cursor()
    for d in days:
        try:
            cursor.execute("SELECT * FROM schedule WHERE day = ? AND group_name = ?", (d,group_name))
            d_res = cursor.fetchall()
            for i in range(len(d_res)):
                d_res[i] = list(d_res[i])
            res[d]=d_res
        except Exception as e:
            print(e)
            print(f"ERROR(get_schedule): Can't get schedule")
    return res

if __name__=="__main__":
    create_db()
    admin = 765194149
    print(get_ids(), check_admin(admin))
    upd_user(admin, user_group="ВМ-123")
    upd_subscriptions(admin, premium_sub=1)
    print(get_users(admin)[0])