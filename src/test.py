import os, json, glob
import numpy as np

directory = '../img/data_json'

for filename in os.listdir(directory):
    file_dir = os.path.join(directory, filename)
    with open(file_dir, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data["annotation"]:
            if item["box"]:
                bbox = item["box"]
                print(bbox)
                break