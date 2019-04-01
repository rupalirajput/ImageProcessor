import requests
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = './images/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
URL = "http://127.0.0.1:5000/"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# def main():
# direction = sys.argv[1]
# flip_vertical_hori(direction)
# degrees_to_rotate = sys.argv[1]
# rotate_left_right(degrees_to_rotate)
# convert_to_grayscale()
# width = sys.argv[1]
# height = sys.argv[2]
# resize_generate_thumbnail(width, height)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            lbl = request.form['ErrMsg']
            lbl.text = 'No file part'
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            lbl = request.form['ErrMsg']
            lbl.text = 'No selected file'
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flip_vertical_hori("vertical", os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('test.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def flip_vertical_hori(direction, imageFile):
    imageFile = imageFile.split('/', 1)[1]
    task = {"img": imageFile, "direction": direction}
    resp = requests.post(URL + 'FlipVertical_Horizontal/', json=task)
    if resp.status_code != 200:
        print("Error code: " + str(resp.status_code))
    else:
        print("Successful")


def rotate_left_right(degrees_to_rotate):
    task = {"imgPath": "images/home_icon.png", "degrees_to_rotate": degrees_to_rotate}
    resp = requests.post(URL + 'RotateLeft_Right/', json=task)
    if resp.status_code != 200:
        print("Error code: " + str(resp.status_code))
    else:
        print("Successful")


def convert_to_grayscale():
    task = {"imgPath": "images/colorful_img.png"}
    resp = requests.post(URL + 'ConvertToGrayscale/', json=task)
    if resp.status_code != 200:
        print("Error code: " + str(resp.status_code))
    else:
        print("Successful")


def send_process_request(image_data, operations):
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
    if resp.status_code == 400:
        print("Not yet done. Please retry.")
    elif resp.status_code != 200:
        print("Error code: " + str(resp.status_code))
    else:
        image_data = resp.json()["image_data"]
        print("Task finished.")
        return image_data

if __name__ == "__main__":
    taskid = send_process_request(open("/path/to/image/file", "rb").read(), ["FV", "FH", "R90", "G"])
    if taskid is not None:
        while True:
            image_data = download_result(taskid)
            if image_data is not None:
                open("/path/to/processed/image/file", "wb").write(image_data)
                break
