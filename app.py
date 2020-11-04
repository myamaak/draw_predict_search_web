import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from flask import Flask, render_template,url_for,request
from tensorflow.python.framework import ops
# ops.reset_default_graph()
import matplotlib.pyplot as plt
from matplotlib import image
import urllib
import base64
import cv2
from io import BytesIO
import os
from selenium import webdriver
import time

file = open('class_names.txt', 'r')
categories_dict = {}
for idx, label in enumerate (file) :
    categories_dict[idx] = label.strip()
# file.close()

single_model = load_model('keras.h5')

# example = cv2.imread('apple.PNG', cv2.IMREAD_GRAYSCALE)
# example = cv2.resize(example, (28,28), interpolation = cv2.INTER_AREA)
# example = example.reshape((28,28))
# img = example.reshape(28, 28,1).astype('float32')
# img /= 255.0
# pred = single_model.predict(np.expand_dims(img, axis=0))[0]
# ind = (-pred).argsort()[:5]
# print(ind)
# latex = [categories_dict[x] for x in ind]
# plt.imshow(img.squeeze())
# print(latex)
# graph = tf.compat.v1.reset_default_graph()
# single_model = load_model('keras.h5')
#https://stackoverflow.com/questions/43469281/how-to-predict-input-image-using-trained-model-in-keras
#https://towardsdatascience.com/develop-an-interactive-drawing-recognition-app-based-on-cnn-deploy-it-with-flask-95a805de10c0


#app = Flask('DrawingOnCanvas')
app = Flask(__name__, template_folder = 'templates')
# change to "redis" and restart to cache again
app.config["CACHE_TYPE"] = "null"

single_model = load_model('keras.h5')

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
#POST하면 predict 함수를 실행
def predict():
    if request.method == 'POST' and request.form['url']:
    # if request.method == 'POST':
        img_url = request.form['url']
        img_url = img_url.split(",")[1]
        decode_img = base64.b64decode(img_url)
        image_data = BytesIO(decode_img)
        img = np.asarray(bytearray(decode_img), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)
    #이번에 추가한 코드
        img = (img < 128).astype(np.uint8) #흑백 전환시켜줌
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

    #이번에 추가한 코드 끝 #https://github.com/moonyeol/quick_draw_copycat  참고
        # img = 255 - img
        #이미지 데이터 읽어서 img format으로 만들어주기
        # resize_img = cv2.resize(img, (28,28), interpolation = cv2.INTER_AREA) #사이즈를 줄일 때 쓰는 보간법
        # img_vector = np.asarray(resize_img, dtype="uint8")
        img_vector = img_vector.reshape(28,28,1).astype('float32')
        # img_vector /=255.0
        # cv2.imshow("show img", img_vector)
        # cv2.waitKey(0)

        global single_model

        pred = single_model.predict(np.expand_dims(img_vector, axis=0))[0]
        ind = (-pred).argsort()[:5]
        latex = [categories_dict[x] for x in ind]
        print(latex)
        key = search_keyword([latex[0]])
        search_result = search_image(key)
        search_result["prediction"] = latex
    else:
        print("no input img")
    return render_template('result.html', result = search_result)

def search_keyword(result):
    #만약 이미지 하나만 있다면 'a '+result
    if len(result)== 1:
        for i in result:
            keyword = 'a '+ i
    else:
        for i in range(len(result)):
            if i == 0:
                keyword = result[i]
            else:
                keyword = keyword + ' and ' + result[i]
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
    #검색 함
    selected = {"imgs":[], "hrefs":[]}
    for i in range(1,6):
        i = str(i)
        tag1 = driver.find_element_by_xpath("//*[@id=\"islrg\"]/div[1]/div["+i+"]/a[1]/div[1]/img")
        selected_img = tag1.get_attribute("src")
        tag2 =driver.find_element_by_xpath("//*[@id=\"islrg\"]/div[1]/div["+i+"]/a[2]")
        selected_href = tag2.get_attribute("href")
        selected["imgs"].append(selected_img)
        selected["hrefs"].append(selected_href)
    return selected

#/html/body/div[2]/c-wiz/div[3]/div[1]/div/div/div/div/div[1]/div[1]/div[1]/a[1]/div[1]/img
# //*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img
#구글 이미지 서치 결과 첫 이미지의 xpath
#//*[@id="islrg"]/div[1]/div[2]/a[1]/div[1]/img
#두번째 xpath
#해당 태그
#<img class="rg_i Q4LuWd" src="data:image/jpeg;base64,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" data-deferred="1" jsname="Q4LuWd" width="286" height="177" alt="Dogs vs. Cats | Kaggle" data-iml="3407.205000054091" data-atf="true">
#링크 xpath
#//*[@id="islrg"]/div[1]/div[1]/a[2]
# <a class="VFACy kGQAp sMi44c lNHeqe WGvvNb" data-ved="2ahUKEwjJ_pv2w-jsAhWOCIgKHXNqAvUQr4kDegUIARCRAQ" jsname="uy6ald" rel="noopener" target="_blank" href="https://hail.to/oaklands-te-kura-o-waka/publication/PgoekPJ/article/mck61Ci" jsaction="focus:kvVbVb; mousedown:kvVbVb; touchstart:kvVbVb;" title="A rain drop - Year 7 and 8 Poetry">A rain drop - Year 7 and 8 Poetry<div class="fxgdke">hail.to<span class="jjPwL"></span></div></a>
if __name__ == "__main__":
    app.run( threaded=True, debug=True)

