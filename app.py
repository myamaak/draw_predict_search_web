import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from flask import Flask, render_template,url_for,request
from tensorflow.python.framework import ops
from tensorflow.python.keras.backend import set_session
import matplotlib.pyplot as plt
from matplotlib import image
import urllib
import base64
import cv2
from io import BytesIO
import os
from yolo import YOLO
from PIL import Image
import re
import time

from selenium import webdriver

file = open('model/class_names.txt', 'r')
categories_dict = {}
for idx, label in enumerate (file) :
    categories_dict[idx] = label.strip()
# file.close()

session = tf.compat.v1.Session()
graph = tf.compat.v1.get_default_graph()
set_session(session)
single_model = load_model('model/keras.h5')
single_model._make_predict_function()

#app = Flask('DrawingOnCanvas')
app = Flask(__name__, template_folder = 'templates')
# change to "redis" and restart to cache again
app.config["CACHE_TYPE"] = "null"



# 에러 방지.
#flask 인스턴스를 생성한다.
#__name__ is the name of the current Python module.
def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

@app.route('/')
def home():
    return render_template('drawingCanvas.html',last_updated=dir_last_updated('static'))


@app.route('/predict', methods=['POST'] )
def predict():
    search_result = {}
    if request.form.get('cnn'):
    # id가 아니라 name값으로 가져온다.
        img_url = request.form['url']
        img_url = img_url.split(",")[1]
        decode_img = base64.b64decode(img_url)


        # 시작
        img = np.asarray(bytearray(decode_img), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)

    #이번에 추가한 코드
        # img = (img < 128).astype(np.uint8) #이미지를 흑백 전환시켜줌
    # coords는 행과 열이 영벡터가 아닌 동안의 벡터의 시작점을 [x, y] 행렬로 값을 추출하고, 이들의 값 차이가 바로 너비와 높이가 된다.
        coords = cv2.findNonZero(img)
    # 그림이 시작되는 x값, y값, 그림의 너비 w 및 높이 h를 획득합니다.
        x, y, w, h = cv2.boundingRect(coords)

    # 너비와 높이의 크기를 비교하여 그림을 중심에 위치할 수 있도록 설정합니다.
        if h > w:
            norm = np.zeros((h + 2, h + 2), dtype=np.float32)
            norm[1:-1, int((h - w) / 2) + 1:int((h - w) / 2) + 1 + w] = img[y:y + h, x:x + w]
        else:
            norm = np.zeros((w + 2, w + 2), dtype=np.float32)
            norm[int((w - h) / 2) + 1:int((w - h) / 2) + 1 + h, 1:-1] = img[y:y + h, x:x + w]

    # 동일한 비율로 cropping 된 그림을 모델 입력 데이터에 맞게 1px 테두리 패딩의 28x28 픽셀 대응 2차원 NumPy 행렬로 변환시킨다.
        img = cv2.resize(norm, (26, 26), interpolation=cv2.INTER_AREA)
        img_vector = np.pad(img, pad_width=1, mode='constant', constant_values=0)

        img_vector /=255.0
    # 끝

        # img_vector = image_np.reshape(28,28,1).astype('float32')
        img_vector = img_vector.reshape(28, 28, 1).astype('float32')
        # cv2.imshow("show img", img_vector)
        # cv2.waitKey(0)

        global single_model
        with session.as_default():
            with session.graph.as_default():
                pred = single_model.predict(np.expand_dims(img_vector, axis=0))[0]
                ind = (-pred).argsort()[:5]
                latex = [categories_dict[x] for x in ind]
                print(latex)
                key = search_keyword([latex[0]])
                search_result = search_image(key)
                search_result["prediction"] = latex
    # predict with yolo
    elif request.form.get('yolo'):
        img_url = request.form['url']
        img_url = img_url.split(",")[1]
        decode_img = base64.b64decode(img_url)
        # image_data = Image.open(BytesIO(decode_img))

        image_data = BytesIO(decode_img)
        image_data = Image.open(image_data)
        # image_data = Image.open('apple1.png')
        image_data = image_data.resize((64,64), Image.ANTIALIAS)
        image_data.save("model/saved.png")

        predict = do_object_detection('model/saved.png', 'model/trained_weights_final.h5', 'model/categories.txt')
        if len(predict["detected_object"]) > 0:
            key = search_keyword(predict["detected_object"])
            search_result = search_image(key)
            search_result["prediction"] = [key]
            print(predict)
        else:
            search_result = []
    else:
        print("no input img")
    return render_template('result.html', result = search_result)

@app.route('/again', methods=['POST'] )
def again():
    if request.method == 'POST' and request.form['new_keyword']:
        keyword = request.form['new_keyword']
        keyword = search_keyword(keyword)
        search_result = search_image(keyword)
        search_result["prediction"] = [keyword]
    return render_template('search_again.html', result = search_result)


def do_object_detection(image, model_path, class_path):
    yolo = YOLO(model_path=model_path, classes_path=class_path)
    image = Image.open(image)
    # cv2.imshow("show img", np.array(image))
    # cv2.waitKey(0)
    result_image = yolo.detect_image(image)

    return result_image

def search_keyword(result):
    keys = {}
    keyword = ''
    if type(result) is not list:
        result = result.split(",")
    if len(result)== 1:
        for i in result:
            keyword = 'a '+ i
    else:
        for i in range(len(result)):
            if result[i] in keys:
              keys[result[i]] += 1
            else:
              keys[result[i]] = 1
        li = list(keys.keys())
        for j in li:
          if li.index(j) == 0:
            if keys[j] == 1:
              keyword = 'a '+j
            else:
              keyword = j+'s'
          else:
            if keys[j] == 1:
              keyword = keyword+' and a '+j
            else:
              keyword = keyword+' and '+j+'s'
    return keyword

def search_image(keyword):
    url = ''
    #창 띄우지 않고 실행
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')

    driver = webdriver.Chrome("C:/Users/Administrator/Downloads/chromedriver_win32/chromedriver.exe", chrome_options = chrome_options)
    # 접속할 url
    search_url = "https://www.google.com/imghp?hl=EN"
    # 접속 시도
    time.sleep(0.05)  ## 0.05초
    driver.get(search_url)
    element = driver.find_element_by_name('q')
    element.send_keys(keyword)
    element.submit()
    #검색
    selected = {"imgs":[], "hrefs":[]}
    for i in range(1,7):
        i = str(i)
        tag1 = driver.find_element_by_xpath("//*[@id=\"islrg\"]/div[1]/div["+i+"]/a[1]/div[1]/img")
        selected_img = tag1.get_attribute("src")
        tag2 =driver.find_element_by_xpath("//*[@id=\"islrg\"]/div[1]/div["+i+"]/a[2]")
        selected_href = tag2.get_attribute("href")
        selected["imgs"].append(selected_img)
        selected["hrefs"].append(selected_href)
    return selected

if __name__ == "__main__":
    app.run( threaded=True, debug=True)

