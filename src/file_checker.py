import os, json

dir = '../img/data_json/'

def file_match(directory, key_to_check):
    matching_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    for item in data["annotation"]:
                        # 딕셔너리 내부에 원하는 키가 있는지 확인합니다.
                        if key_to_check in item:
                            matching_files.append(item[key_to_check])
      
            except (json.JSONDecodeError, FileNotFoundError, TypeError) as e:
                print(f"Error processing file {filename}: {e}")
                continue
    return matching_files

bboxes = file_match(dir, "box")
print(bboxes)