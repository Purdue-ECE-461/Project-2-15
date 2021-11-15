import os
from datetime import datetime
from google.cloud import bigquery

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "driven-actor-331522-1a1bc26b5b15.json"
project_id = "driven-actor-331522"
client = bigquery.Client()
repo_table_id = "driven-actor-331522.461p2.repo_info"

def table_insert(ID, name, version, content, URL, JSProgram):
    sql = "SELECT * FROM `{}` WHERE ID='{}'".format(repo_table_id, ID)
    query = client.query(sql)
    records = [dict(row) for row in query]
    if len(records) > 0:
        return "Error, already exists"
    sql = "INSERT INTO `{}` (ID, Name, Version, Content, URL, " \
          "JSProgram) VALUES ('{}','{}','{}','{}','{}','{}')".format(repo_table_id,ID,name,version,
                                                                     content,URL,JSProgram)
    print(sql)
    query = client.query(sql)
    return query
    pass

def table_update_by_id(ID, name, version, content):
    sql = "UPDATE `{}` SET Content='{}' WHERE ID='{}' AND Name='{}' AND Version='{}'".format(repo_table_id,content,
                                                                                             ID,name,
                                                                                    version)
    print(sql)
    query = client.query(sql)
    return query

def table_search_by_name(repo_name):
    sql = "SELECT * FROM `{}` WHERE name='{}'".format(repo_table_id, repo_name)
    query = client.query(sql)
    records = [dict(row) for row in query]
    return query

def table_search_by_id(pk_id):
    sql = "SELECT * FROM `{}` WHERE ID='{}'".format(repo_table_id, pk_id)
    query = client.query(sql)
    return query

if __name__ == '__main__':
    query = table_update_by_id("underscore", "Underscore", "1.0.0", "content_test_1")
    result = query.result()
    pass

