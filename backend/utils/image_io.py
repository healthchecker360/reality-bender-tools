from PIL import Image
import io

def read_image(file_storage):
    return Image.open(file_storage)
