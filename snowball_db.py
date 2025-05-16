import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='itap.mysql.pythonanywhere-services.com',
        user='itap',
        password='qpspelrxm27',
        database='itap$snowball',
        port=3306
    )

def get_user_list():
    print('get_user_list function')
    return []

def get_login(company_name, login_key):
    print('get_login function')
    return None

def set_login(company_name, login_key):
    print('set_login function')
    return None

def get_user_request():
    print('get_user_request function')
    return []

def set_user_regist_request(company_name, user_name, user_email):
    print('set_user_regist_request function')
    return None

def set_rcm_request(pi_request_type, pi_request_file, pi_client_name, pi_email_address):
    print('set_rcm_request function')
    return None

def set_paper_request(pi_client_name, pi_email, pi_request_file, pi_request_content):
    print('set_paper_request function')
    return None