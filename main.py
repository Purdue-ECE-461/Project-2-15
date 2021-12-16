import codecs

from flask import Flask, request, jsonify
from parser import *
from gcp_bigtable import *
import subprocess
import reqwer as re
import base64

app = Flask(__name__)

try:
    os.mkdir("zips")
except Exception as e:
    print(e)

@app.before_request
def log_request():
    try:
        print(request.__dict__)
        print("//////////")
        print(request.get_data())
    except:
        pass
    return None

#GET by ID
@app.route('/project2/package/<pk_id>', methods=['GET'])
def get_by_id(pk_id):
    try:
        auth_token = request.headers.get('X-Authorization') #check token
        isUser, isAdmin = check_is_admin(auth_token)
        if not isUser:
            return ({"ERROR":"Invalid Token, not a user"},401)
        query = table_search_by_id(pk_id) #search by id
        result = [dict(row) for row in query]
        if len(result) == 0:
            return {"code": -1,
                    "message": "An error occurred while retrieving package"},500
        result = result[0]
        output = {   #format output
            "metadata":{},
            "data":{}
        }
        output["metadata"]["Name"] = result["Name"]
        output["metadata"]["Version"] = result["Version"]
        output["metadata"]["ID"] = result["ID"]
        filename = "zips/" + pk_id + ".txt"
        file1 = open(filename, "r")
        content = file1.read() ##obtain content from file
        output["data"]["Content"] = content
        output["data"]["URL"] = result["URL"]
        output["data"]["JSProgram"] = result["JSProgram"]

        push_to_history(auth_token, result["Name"], result["Version"], result["ID"], "DOWNLOAD")
        return output
    except e:
        return {"code" : -1,
                "message": "An error occurred while retrieving package"},500

#PUT by id: update version
@app.route('/project2/package/<pk_id>', methods=['PUT'])
def put_by_id(pk_id):
    request_body = request.get_json(force=True)

    auth_token = request.headers.get('X-Authorization') ## check token
    isUser, isAdmin = check_is_admin(auth_token)
    if not isUser:
        return ({"ERROR": "Invalid Token, not a user"}, 401)
    if not isAdmin:
        return ({"ERROR": "Invalid Token, not a admin"}, 401)

    query = table_search_by_id(pk_id) #search from table
    result = [dict(row) for row in query]
    if len(result) == 0:
        return '', 400

    ID = request_body["metadata"]["ID"]
    Name = request_body["metadata"]["Name"]
    Version = request_body["metadata"]["Version"]
    Content = request_body["data"]["Content"]
    url = request_body["data"]["URL"]
    result= table_update_by_id(ID, Name, Version, Content, url) #update the table

    push_to_history(auth_token, Name, Version, ID, "UPDATE") #save history
    return "",200

#del by id
@app.route('/project2/package/<pk_id>', methods=['DELETE'])
def del_by_id(pk_id):
    auth_token = request.headers.get('X-Authorization')
    isUser, isAdmin = check_is_admin(auth_token) #check token
    if not isUser:
        return ({"ERROR": "Invalid Token, not a user"}, 401)
    if not isAdmin:
        return ({"ERROR": "Invalid Token, not a admin"}, 401)

    query = table_search_by_id(pk_id) #check if the package exist
    result = [dict(row) for row in query]
    if len(result) > 0:
        result = result[0]
        push_to_history(auth_token, result['Name'], result['Version'], result['ID'], "DELETE")
    else:
        return '',400 #if not exist, return error code

    table_del_by_id(pk_id) #delete
    filename = "zips/" + pk_id + ".txt"
    os.remove(filename) #delete the file

    return '', 200
    pass

#rate by id
@app.route('/project2/package/<pk_id>/rate', methods=['GET'])
def rate_package(pk_id):
    auth_token = request.headers.get('X-Authorization') #check users priv
    isUser, isAdmin = check_is_admin(auth_token)
    if not isUser:
        return ({"ERROR": "Invalid Token, not a user"}, 401)

    query = table_search_by_id(pk_id) #check if the package exists
    result = [dict(row) for row in query]
    if len(result) == 0:
        return "", 400
    result = result[0]
    url = result["URL"]
    if not url:
        return "", 500
    os.chdir("rating_package")
    with open('buffer.txt', 'w') as f:
        f.write(url)

    output = str(subprocess.check_output(['./run', 'buffer.txt'])) #call team 14 code
    result = re.findall(r"[-+]?\d*\.\d+|\d+", output) #obtain command output
    if len(result) == 0:
        return "", 500
    total = result[0]
    ramp_up = result[1]
    correct = result[2]
    bus_factor = result[3]
    response = result[4]
    license = result[5]
    output = {
        "RampUp" : ramp_up,
        "Correctness" : correct,
        "BusFactor" : bus_factor,
        "ResponsiveMaintainer" : response,
        "LicenseScore" : license,
        "GoodPinningPractice" : total
    }
    os.chdir("..")
    return output

#get by name, history
@app.route('/project2/package/byName/<pk_name>', methods=['GET'])
def get_by_name(pk_name):
    query = table_search_by_name(pk_name)
    result = [dict(row) for row in query]
    if len(result) == 0:
        return '', 400
    query = query_history(pk_name) #check the history
    result = [dict(row) for row in query]
    output = []
    for row in result:
        if int(row['isAdmin']) == 1:
            isAdmin = True
        else:
            isAdmin = False
        temp = {
            "User":{
                "name": row['user'],
                "isAdmin" : isAdmin
            },
            "Date": row['date'],
            "PackageMetadata": {
                "Name": row['pk_name'],
                "Version": row['Version'],
                "ID": row['ID']
            },
            "Action" : row['action']
        }
        output.append(temp)
    return jsonify(output)

#del by name
@app.route('/project2/package/byName/<pk_name>', methods=['DELETE'])
def del_by_name(pk_name):
    try:
        auth_token = request.headers.get('X-Authorization')
        isUser, isAdmin = check_is_admin(auth_token)
        if not isUser:
            return ({"ERROR": "Invalid Token, not a user"}, 401)
        if not isAdmin:
            return ({"ERROR": "Invalid Token, not a admin"}, 401)
        query = table_search_by_name(pk_name)
        result = [dict(row) for row in query]
        if len(result) == 0:
            return '',400
        result = result[0]
        push_to_history(auth_token, result['Name'], result['Version'], result['ID'], "DELETE")

        table_del_by_name(pk_name)
        return '', 200
    except e:
        return {"code": -1,
                "message": "An error occurred while retrieving package"}, 500



#POST package create
@app.route('/project2/package', methods=['POST'])
def pk_create():
    request_body = request.get_json(force=True)
    print("request body : %s", request_body)
    auth_token = request.headers.get('X-Authorization')
    isUser, isAdmin = check_is_admin(auth_token)
    if not isUser:
        return ({"ERROR": "Invalid Token, not a user"}, 401)
    if not isAdmin:
        return ({"ERROR": "Invalid Token, not a admin"}, 401)

    if not request_body:
        return {"Error" : "JSON not received"}, 400
    if "data" not in request_body:
        return {"message" : "malformed request, missing data section"}, 400
    if "metadata" not in request_body:
        return {"message" : "malformed request, missing metadata section"}, 400

    if "Content" in request_body["data"]:    #create package
        ID = request_body["metadata"]["ID"]
        Name = request_body["metadata"]["Name"]
        Version = request_body["metadata"]["Version"]
        Content = request_body["data"]["Content"]
        JSProgram = request_body["data"]["JSProgram"]
        #url = request_body["data"]["URL"]
        url = None
        result = table_insert(ID,Name,Version,Content,JSProgram, url)
        if result == "Error, already exists":
            return "",403
        else:
            push_to_history(auth_token, Name, Version, ID, "CREATE")
            return {"Name": Name,
                    "Version": Version,
                    "ID": ID
                    }
    elif "URL" in request_body["data"]:    #Package ingest
        url = request_body['data']['URL']
        os.chdir("rating_package")
        with open('buffer.txt', 'w') as f:
            f.write(url)

        output = str(subprocess.check_output(['./run', 'buffer.txt']))
        os.chdir("..")
        result = re.findall(r"[-+]?\d*\.\d+|\d+", output)
        total = float(result[0])
        ramp_up = float(result[1])
        correct = float(result[2])
        bus_factor = float(result[3])
        response = float(result[4])
        license = float(result[5])
        ingestiable = True
        for i in result: #check quality
            if float(i) < 0.1:
                ingestiable = False
        if ingestiable:
            url = getGithubLink(url)
            response = getzip(url)
            zip = response.content
            zip = base64.b64encode(zip)
            ID = request_body["metadata"]["ID"]
            Name = request_body["metadata"]["Name"]
            Version = request_body["metadata"]["Version"]
            Content = zip
            JSProgram = request_body["data"]["JSProgram"]
            result = table_insert(ID, Name, Version, Content, JSProgram, url) #insert to table
            if result == "Error, already exists":
                return {"message": "Package exists, cannot insert, try udpate"}
            push_to_history(auth_token, Name, Version, ID, "INGEST")
            return {"Name": Name,
                    "Version": Version,
                    "ID": ID
                    }
    else:
        return "", 201



    return '', 200


#get packages
@app.route('/project2/packages', methods=['POST'])
def get_pag_list():
    auth_token = request.headers.get('X-Authorization')
    isUser, isAdmin = check_is_admin(auth_token)
    if not isUser:
        return ({"ERROR": "Invalid Token, not a user"}, 401)

    page = int(request.args.get("offset",default=1))
    query = query_all()
    result = [dict(row) for row in query]
    result = result[(page-1)*10 : (page)*10-1 ]
    return jsonify(result)

#reset
@app.route('/project2/reset', methods=['DELETE'])
def reset():
    auth_token = request.headers.get('X-Authorization')
    isUser, isAdmin = check_is_admin(auth_token)
    if not isUser:
        return ({"ERROR": "Invalid Token, not a user"}, 401)
    if not isAdmin:
        return ("You do not have permission to reset the registry.", 401)

    table_reset()
    return '', 200

#create auth token
@app.route('/project2/authenticate', methods=['PUT'])
def create_auth_token():
    request_body = request.get_json(force=True)
    name = request_body["User"]["name"]
    isAdmin = request_body["User"]["isAdmin"]
    pwd = request_body["Secret"]["password"]
    if isAdmin == True:
        isAdmin = 1
    else:
        isAdmin = 0
    query = get_auth(name, pwd, isAdmin)
    result = [dict(row) for row in query]
    result = result[0]
    if len(result) == 0:
        return '',401
    return jsonify("bearer " + result['auth_token'])

if __name__ == '__main__':
    app.run(debug=True)