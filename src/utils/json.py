import json


def read(file_path):
    with open(file_path) as f:
        data = json.load(f)
    return data


def write(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
