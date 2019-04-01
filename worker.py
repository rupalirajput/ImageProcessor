import base64
import imghdr
from PIL import Image
from celery import Celery
import io

THUMBNAIL_HEIGHT = 300
THUMBNAIL_WIDTH = 300


def flip_vertical(image_obj):
    return image_obj.transpose(Image.FLIP_TOP_BOTTOM)


def flip_horizontal(image_obj):
    return image_obj.transpose(Image.FLIP_LEFT_RIGHT)


def rotate_n_degrees(image_obj, degrees_to_rotate):
    return image_obj.rotate(degrees_to_rotate)


def grayscale(image_obj):
    return image_obj.convert('L')


def generate_thumbnail(image_obj):
    image_obj.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), Image.ANTIALIAS)
    return image_obj


def resize(image_obj, x, y):
    image_obj.thumbnail((x, y), Image.ANTIALIAS)
    return image_obj


celery = Celery('imgProcessorAPI', backend='db+sqlite:///response-cache.sqlite', broker='amqp://guest@localhost//')


@celery.task
def DSLExecuter(image_data, operations):
    image_data = base64.b64decode(image_data)
    image_obj = Image.open(io.BytesIO(image_data))
    for op in operations:
        if op == "FV":
            image_obj = flip_vertical(image_obj)
        elif op == "FH":
            image_obj = flip_horizontal(image_obj)
        elif op.startswith("R:"):
            image_obj = rotate_n_degrees(image_obj, int(op.split(':')[1]))
        elif op == "G":
            image_obj = grayscale(image_obj)
        elif op == "T":
            image_obj = generate_thumbnail(image_obj)
        elif op == "RL":
            image_obj = rotate_n_degrees(image_obj, -90)
        elif op == "RR":
            image_obj = rotate_n_degrees(image_obj, 90)
        elif op.startswith("RS:"):
            image_obj = resize(image_obj, *map(int, op.split(':')[1].split(',')))
        else:
            raise Exception("invalid op-code " + op)

    imgByteArr = io.BytesIO()
    image_obj.save(imgByteArr, imghdr.what(None, h=image_data).upper())

    return base64.b64encode(imgByteArr.getvalue()).decode("ascii")
