import sqlite3

def get_user_list():
    print('get_login function')
    con = sqlite3.connect("snowball.db")
    cur = con.cursor()
    sql = "select user_name from sb_user order by user_name"
    cur.execute(sql)
    result = cur.fetchall()
    con.close()
    
    modified_result = [item for sublist in result for item in sublist]

    return modified_result

def get_login(user_name, login_key):
    con = sqlite3.connect("snowball.db")
    cur = con.cursor()
    sql = "select user_name from sb_user where user_name='{}' and login_key='{}'".format(user_name, login_key)
    print("sql = ", sql)
    cur.execute(sql)
    result = cur.fetchone()
    print('result = ', result)
    con.close()

    return result
