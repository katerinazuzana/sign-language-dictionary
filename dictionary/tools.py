import PIL


def getImage(path, width, height):
    
    with PIL.Image.open(path) as img:
        img = img.resize((width, height), PIL.Image.LANCZOS)
        image = PIL.ImageTk.PhotoImage(img)
    return image




