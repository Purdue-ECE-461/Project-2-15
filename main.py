from flask import Flask
from flask_restful import Api, Resource
from google.cloud import storage
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'driven-actor-331522-1a1bc26b5b15.json'
storage_client = storage.Client()

bucket_name = 'repo_info'
bucket = storage_client.bucket(bucket_name)
bucket.location = 'US'
bucket = storage_client.create_bucket(bucket)


app = Flask(__name__)
api = Api(app)

class server(Resource):
    def get(self):
        return {"data": "Hello World"}

api.add_resource(server)

if __name__ == '__main__':
    app.run(debug=True)