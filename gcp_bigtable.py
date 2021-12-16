import os
from datetime import datetime
from google.cloud import bigquery
import hashlib
from pymysql.converters import escape_string

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "driven-actor-331522-1a1bc26b5b15.json"
project_id = "driven-actor-331522"
client = bigquery.Client()
repo_table_id = "driven-actor-331522.461p2.repo_info"

def query_history(pk_name):
    sql = "SELECT * FROM `driven-actor-331522.461p2.history` WHERE pk_name = '{}'".format(pk_name)
    query = client.query(sql)
    return query

def table_insert(ID, name, version, content, JSProgram, url):
    sql = "SELECT * FROM `{}` WHERE ID= \'{}\'".format(repo_table_id, ID)
    query = client.query(sql)
    records = [dict(row) for row in query]
    if len(records) > 0:
        return "Error, already exists"
    sql = "INSERT INTO `{}` (ID, Name, Version, Content, URL, " \
          "JSProgram) VALUES ('{}','{}','{}','{}','{}', '{}')".format(repo_table_id,ID,name,version,

                                                                     "content", url, escape_string(JSProgram))
    print(sql)

    try:
        os.mkdir("zips")
    except Exception as e:
        print(e)
        pass
    filename = "zips/" + ID + ".txt"
    file1 = open(filename, "w")
    file1.write(str(content))
    query = client.query(sql)
    return query
    pass

def table_update_by_id(ID, name, version, content, url):
    sql = "UPDATE `{}` SET Content='{}', URL = '{}' WHERE ID='{}' AND Name='{}' AND Version='{}'".format(
                                                                                                    repo_table_id,
                                                                                                   "content", url,
                                                                                             ID,name,
                                                                                    version)
    #print(sql)

    try:
        os.mkdir("zips")
    except Exception as e:
        print(e)
    filename = "zips/" + ID + ".txt"
    file1 = open(filename, "w")
    query = client.query(sql)
    file1.write(content)
    return query

def table_search_by_name(repo_name):
    sql = "SELECT * FROM `{}` WHERE name='{}'".format(repo_table_id, repo_name)
    query = client.query(sql)
    records = [dict(row) for row in query]
    return query

def table_del_by_name(pk_name):
    sql = "DELETE FROM `{}` WHERE name='{}'".format(repo_table_id, pk_name)
    query = client.query(sql)
    return query

def table_search_by_id(pk_id):
    sql = "SELECT * FROM `{}` WHERE ID='{}'".format(repo_table_id, pk_id)
    query = client.query(sql)
    return query

def table_del_by_id(pk_id):
    sql = "DELETE FROM `{}` WHERE ID = '{}'".format(repo_table_id, pk_id)
    query = client.query(sql)
    return query

def query_all():
    sql = "SELECT Version, Name FROM `{}`".format(repo_table_id)
    query = client.query(sql)
    return query

def auth_init():
    user_name = "ece461defaultadminuser";
    password = "correcthorsebatterystaple123(!__+@**(A"
    user_auth_hash = hashlib.sha256(password.encode()).hexdigest()
    auth_token = hashlib.sha256((user_name + password).encode()).hexdigest()
    sql = "INSERT INTO `driven-actor-331522.461p2.user_info` (user_name, user_auth_hash, user_auth_level, " \
          "auth_token) VALUES (" \
            "'{}', '{}', {}, '{}')".format(user_name, user_auth_hash, 1, auth_token)
    query = client.query(sql)
    pass

def get_auth(user_name, user_auth, user_auth_level):
    user_auth_hash = hashlib.sha256(user_auth.encode()).hexdigest()
    sql = "SELECT auth_token FROM `driven-actor-331522.461p2.user_info` WHERE user_name = '{}' AND user_auth_hash = " \
          "'{}' AND user_auth_level = {}".format(user_name, user_auth_hash, user_auth_level)
    query = client.query(sql)
    return query

def table_reset():
    sql = "DELETE FROM `{}` WHERE true".format(repo_table_id)
    query = client.query(sql)
    sql = "DELETE FROM `driven-actor-331522.461p2.user_info` WHERE user_name <> 'ece461defaultadminuser'"
    query = client.query(sql)
    sql = "DELETE FROM `driven-actor-331522.461p2.history` WHERE true "
    query = client.query(sql)
    return query


def check_is_admin(auth_token):    ##(isUser, isAdmin)
    if auth_token == None:
        return (False, False)
    auth_token = auth_token.strip("bearer ")
    sql = "SELECT user_auth_level FROM `driven-actor-331522.461p2.user_info` WHERE auth_token = '{}'".format(auth_token)
    #print(sql)
    query = client.query(sql)
    result = [dict(row) for row in query]
    if len(result) == 0:
        return (False, False)
    result = result[0]
    if result['user_auth_level'] == 1:
        return (True, True)
    else:
        return (True, False)
    pass

def push_to_history(auth_token, pk_name, pk_version, pk_id, action):
    auth_token = auth_token.strip("bearer ")
    sql = "SELECT user_name, user_auth_level FROM `driven-actor-331522.461p2.user_info` WHERE auth_token = '{}'".format(
        auth_token)
    print(sql)
    query = client.query(sql)
    result = [dict(row) for row in query]
    result = result[0]
    user = result['user_name']
    isAdmin = result['user_auth_level']
    date = datetime.now()
    sql = "INSERT INTO `driven-actor-331522.461p2.history` (ID, user, action, date, isAdmin, pk_name, Version" \
          ") VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(pk_id, user, action, date, isAdmin,pk_name,
                                                                        pk_version)
    print(sql)
    query = client.query(sql)
    return query



if __name__ == '__main__':
    auth_init()
    #get_auth("ece461defaultadminuser", "correcthorsebatterystaple123(!__+@**(A", 1)
    #print(check_is_admin('3252598aed44f1f541cb169be0d547d45735d9be4737163e2eb7090fd206f5c6'))
    # auth_token = "3252598aed44f1f541cb169be0d547d45735d9be4737163e2eb7090fd206f5c6"
    # pk_name = "test1"
    # pk_version = "1.0.0"
    # pk_id = "wacswadcsdcc"
    # push_to_history(auth_token, pk_name, pk_version, pk_id, "Download")
    pass

