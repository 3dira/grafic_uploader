import sqlite3

con = sqlite3.connect('boomilia.sqlite3')
cur = con.cursor()

def init_db():
    # First Init
    cur.execute('CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id VARCHAR(50), csrftoken VARCHAR(100), sessionid VARCHAR(100), phone_number VARCHAR(20), active INTEGER);')
    con.commit()

def get_user(user_id):
    user = cur.execute('SELECT * FROM user WHERE user_id="'+user_id+'" and active="1"')
    user_information = user.fetchone()
    if user_information == None:
        return None
    information = {
        'user_id': user_information[1],
        'csrftoken': user_information[2],
        'sessionid': user_information[3],
        'phone_number': user_information[4],
    }
    return information

def create_user(user_id):
    cur.execute('INSERT INTO user (user_id, active) VALUES ("'+user_id+'", "1")')
    con.commit()

def update_user(user_id, datas:dict):
    command = "UPDATE user SET "
    for key in datas:
        command += key+' = "'+datas[key]+'",'
    command = command[:-1] + ' WHERE ' + 'user_id="' + user_id + '"'
    cur.execute(command)
    con.commit()
