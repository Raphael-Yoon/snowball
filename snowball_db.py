import sqlite3

def get_user_list():
    print('get_login function')
    con = sqlite3.connect("snowball.db")
    cur = con.cursor()
    sql = "select company_name from sb_user order by user_name"
    cur.execute(sql)
    result = cur.fetchall()
    con.close()
    
    modified_result = [item for sublist in result for item in sublist]

    return modified_result

def get_login(company_name, login_key):
    con = sqlite3.connect("snowball.db")
    cur = con.cursor()
    sql = "select company_name from sb_user where company_name='{}' and login_key='{}'".format(company_name, login_key)
    cur.execute(sql)
    result = cur.fetchone()
    con.close()
    
    return result

def set_user_regist_request(company_name, user_name, user_email):
    con = sqlite3.connect("snowball.db")
    cur = con.cursor()
    sql = "insert into sb_user_request(company_name, user_name, user_email, interface_yn, creation_date) values('{}', '{}', '{}', 'N', current_timestamp)".format(company_name, user_name, user_email)
    print('sql = ', sql)
    result = cur.execute(sql)
    print('result = ', result)
    con.commit()
    con.close()
    
    return result
