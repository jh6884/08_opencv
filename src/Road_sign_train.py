import cv2
import numpy as np
import os, glob, time, json

startT = time.time()
categories =  ['triangle', 'circle']
dictionary_size = 50
base_path = "../img/road_sign/"
dict_file = './roadsign_dict.npy'
svm_model_file = './roadsign_svm.xml'
json_path = "../img/data_json/"

detector = cv2.xfeatures2d.SIFT_create()
matcher = cv2.BFMatcher(cv2.NORM_L2)
bowTrainer = cv2.BOWKMeansTrainer(dictionary_size)
bowExtractor = cv2.BOWImgDescriptorExtractor(detector, matcher)

paths = []
labels = []
print('Adding descriptor to BOWTrainer...')
for idx, category in enumerate(categories): # 카테고리 순회
    dir_path = base_path + category          
    img_paths = glob.glob(dir_path +'/*.jpg') 
    img_len = len(img_paths)
    for i, img_path in enumerate(img_paths): # 카테고리 내의 모든 이미지 파일 순회
        paths.append(img_path)        
        labels.append(idx)            # 학습 데이타 레이블, 0 또는 1 
        img = cv2.imread(img_path)

        filename = os.path.basename(img_path)
        json_file = json_path + filename[:9] +'.json'
        with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data["annotation"]:
                     if item["box"]:
                          bbox = item["box"]
                          print(bbox)
                          break
        cropped_img = img[bbox[1]:bbox[3],bbox[0]:bbox[2]]
        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        # 특징점과 특징 디스크립터 추출 및 bowTrainer에 추가 ---④
        kpt, desc= detector.detectAndCompute(gray, None) 
        bowTrainer.add(desc)
        print('\t%s %d/%d(%.2f%%)' \
              %(category,i+1, img_len, (i+1)/img_len*100), end='\r')
    print()
print('Adding descriptor completed...')

# KMeans 클러스터로 군집화하여 시각 사전 생성 및 저장---⑤
print('Starting Dictionary clustering(%d)... \
        It will take several time...'%dictionary_size)
dictionary = bowTrainer.cluster() # 군집화로 시각 사전 생성  
np.save(dict_file, dictionary)    # 시각 사전 데이타(넘파일)를 파일로 저장
print('Dictionary Clustering completed...dictionary shape:',dictionary.shape)

# 시각 사전과 모든 이미지의 매칭점으로 히스토그램 계산---⑥
bowExtractor.setVocabulary(dictionary)      # bowExtractor에 시각 사전 셋팅 
train_desc = []                             # 학습 데이타 
for i, path in enumerate(paths):      # 모든 학습 대상 이미지 순회
    img = cv2.imread(path)                  # 이미지 읽기 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    # 매칭점에 대한 히스토그램 계산 --- ⑦
    hist = bowExtractor.compute(gray, detector.detect(gray)) 
    train_desc.extend(hist)                 
    print('Compute histogram training set...(%.2f%%)'\
                    %((i+1)/len(paths)*100),end='\r')
print("\nsvm items", len(train_desc), len(train_desc[0]))

# 히스토그램을 학습데이타로 SVM 훈련 및 모델 저장---⑧
print('svm training...')
svm = cv2.ml.SVM_create()
svm.trainAuto(np.array(train_desc), cv2.ml.ROW_SAMPLE, np.array(labels))
svm.save(svm_model_file)
print('svm training completed.')
print('Training Elapsed: %s'\
        %time.strftime('%H:%M:%S', time.gmtime(time.time()-startT)))

# 원래의 이미지로 테스트 --- ⑨
print("Accuracy(Self)")
for label, dir_name in enumerate(categories):
    labels = []
    results = []
    img_paths = glob.glob(base_path + '/'+dir_name +'/*.*')
    for img_path in img_paths:
        labels.append(label)
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        feature = bowExtractor.compute(gray, detector.detect(gray))
        ret, result = svm.predict(feature)
        resp = result[0][0]
        results.append(resp)

    labels = np.array(labels)
    results = np.array(results)
    err = (labels != results)
    err_mean = err.mean()
    print('\t%s: %.2f %%' % (dir_name, (1 - err_mean)*100))