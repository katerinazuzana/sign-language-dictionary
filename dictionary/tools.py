import PIL


def getImage(path, width, height):
    """Open an image and resize it. Return a PIL PhotoImage object."""
    with PIL.Image.open(path) as img:
        img = img.resize((width, height), PIL.Image.LANCZOS)
        image = PIL.ImageTk.PhotoImage(img)
    return image


def listOfTuplesToList(listOfTuples):
    """Convert a list of tuples into a simple list of tuple[0] items."""
    res = []
    for item in listOfTuples:
        res.append(item[0])
    return res


def leftPadItems(alist):
    """Add a space to the begining of each string in a given list."""
    return [' ' + item for item in alist]
