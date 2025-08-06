import os, json, shutil

dir = '../img/data_json/'

def file_match(directory, key_to_check, value_to_check, destination):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for item in data["annotation"]:
                    # 딕셔너리 내부에 원하는 키가 있는지 확인합니다.
                    if key_to_check in item and item[key_to_check] == value_to_check:
                        paths = '../img/daylight/'+filename[:9]+'.jpg'
                        try:
                            print('../img/daylight/'+filename[:9]+'.jpg 이동 시도')
                            shutil.move(paths, destination)
                            print(filename[:9]+'.jpg 파일 이동 성공')
                        except:
                            continue
    return

file_match(dir, "shape", "triangle", "../img/road_sign/triangle/")
file_match(dir, "shape", "circle", "../img/road_sign/circle/")