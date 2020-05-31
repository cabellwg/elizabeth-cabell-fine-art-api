def decorate_image_filename(filename, attribute):
    """Adds attribute and extension to the end of the filename"""
    return "{}-{}.jpg".format(filename, attribute)


def resize_image(image, max_axis_length):
    """Resizes an image so that the maximum width of an axis is max_axis_length"""
    w = image.width
    h = image.height

    if w > h:
        return image.resize((max_axis_length, max_axis_length * (h / w)))
    elif h > w:
        return image.resize((max_axis_length * (w / h), max_axis_length))
    else:
        return image.resize((max_axis_length, max_axis_length))