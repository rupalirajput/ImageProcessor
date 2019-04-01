import base64
import time
from flask import Flask, render_template, request, redirect
import requests
from werkzeug.datastructures import FileStorage

app = Flask(__name__)

URL = "http://127.0.0.1:5000/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def send_process_request(image_data, operations):
    image_data = base64.b64encode(image_data).decode("ascii")
    task = {"image_data": image_data, "operations": operations}
    resp = requests.post(URL + 'process', json=task)
    if resp.status_code != 200:
        print("Error code: " + str(resp.status_code))
    else:
        taskid = resp.json()["taskid"]
        print("Successful. Task ID: " + taskid)
        return taskid


def download_result(taskid):
    resp = requests.get(URL + 'process/' + taskid)
    if resp.status_code == 404:
        print("Not yet done. Please retry.")
    elif resp.status_code != 200:
        print("Error code: " + str(resp.status_code))
        raise Exception(str(resp))
    else:
        # image_data = base64.b64decode(resp.json()["image_data"])
        print("Task finished.")
        # return image_data
        return resp.json()["image_data"]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return render_template('test.html', error_msg='No file selected')
        file: FileStorage = request.files['file']
        strOperation = request.form['txtOperation']
        if strOperation == '':
            return render_template('test.html', error_msg='No operation entered')
        if file.filename == '':
            return render_template('test.html', error_msg='No file selected')
        if file and allowed_file(file.filename):
            try:
                taskid = send_process_request(file.stream.read(), strOperation.split())
                if taskid is not None:
                    while True:
                        image_data = download_result(taskid)
                        if image_data is not None:
                            return render_template('test.html', image_data=image_data, image_type=file.mimetype)
                        time.sleep(1)
            except:
                return render_template('test.html', error_msg='Invalid operation code')
        else:
            return render_template('test.html', error_msg='Not a valid file')

    return render_template('test.html')


if __name__ == "__main__":
    app.run(port='5010')
