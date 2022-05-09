import os

def list_dir(path):
    files = []
    for file in os.listdir(path):
        if file.endswith(".png"):
            files.append(file)
    return files
