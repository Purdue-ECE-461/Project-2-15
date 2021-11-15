from flask import Flask, request
from gcp_bigtable import table_search_by_name, table_search_by_id, table_update_by_id,table_insert

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/project2/package', methods=['POST'])
def pk_create():
    request_body = request.get_json()
    ID = request_body["metadata"]["ID"]
    Name = request_body["metadata"]["Name"]
    Version = request_body["metadata"]["Version"]
    Content = request_body["data"]["Content"]
    URL = request_body["data"]["URL"]
    JSProgram = request_body["data"]["JSProgram"]
    result = table_insert(ID,Name,Version,Content,URL,JSProgram)
    if result == "Error, already exists":
        return {"message": "Package exists, cannot insert, try udpate"}
    else:
        return {"message": "successed"}

@app.route('/project2/package/<pk_id>', methods=['GET'])
def get_by_id(pk_id):
    query = table_search_by_id(pk_id)
    result = [dict(row) for row in query]
    if len(result) == 0:
        return {"message": "package {} not found".format(pk_id)}
    result = result[0]
    output = {
        "metadata":{},
        "data":{}
    }
    output["metadata"]["Name"] = result["Name"]
    output["metadata"]["Version"] = result["Version"]
    output["metadata"]["ID"] = result["ID"]
    output["data"]["Content"] = result["Content"]
    output["data"]["URL"] = result["URL"]
    output["data"]["JSProgram"] = result["JSProgram"]
    return output

@app.route('/project2/package/<pk_id>', methods=['PUT'])
def put_by_id(pk_id):
    request_body = request.get_json()
    ID = request_body["metadata"]["ID"]
    Name = request_body["metadata"]["Name"]
    Version = request_body["metadata"]["Version"]
    Content = request_body["data"]["Content"]
    table_update_by_id(ID, Name, Version, Content)


app.run()