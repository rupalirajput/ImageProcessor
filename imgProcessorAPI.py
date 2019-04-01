import werkzeug
from flask import Flask, abort
from flask_restful import Api, Resource, request
import worker

app = Flask(__name__)
api = Api(app)


class ProcessImage(Resource):
    def get(self, taskid):
        result = worker.celery.AsyncResult(taskid)
        if result.ready():
            try:
                return {"image_data": result.get()}
            except werkzeug.exceptions.InternalServerError as err:
                abort(500, str(err))

        abort(404)

    def post(self):
        args = request.get_json(force=True)
        result = worker.DSLExecuter.apply_async(args=(args["image_data"], args["operations"]))
        return {"taskid": result.id}


api.add_resource(ProcessImage, "/process/<string:taskid>", endpoint="get-processimage")
api.add_resource(ProcessImage, "/process", endpoint="post-processimage")

if __name__ == '__main__':
    app.run(port='5000')
