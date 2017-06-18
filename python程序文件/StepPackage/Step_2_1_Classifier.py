from StepPackage import Step_3_GetFeatures
from svmutil import *
from PIL import Image
import os
import time

### 切割后的字母进行分类
### 识别字母并移动到指定文件夹

def main():
    for i in range(10):
        print('\n\n\n\n第{}个文件夹'.format(i))
        characterClassifier(str(i))

def characterClassifier(num):
    # 遍历去噪后的图片
    rootdir = "../AllFile/classificated-images/"+num+'/'
    filenames = []
    for parent, dirnames, _filenames in os.walk(rootdir):
        # _filenames.sort(key=lambda x: int(x[:-6]))
        filenames = _filenames

    count = 1
    for filename in filenames:
        ori_image_path = os.path.join(parent, filename)
        image = Image.open(ori_image_path)
        character = resultClassifier(image)

        if count%100 == 0:
            print('100次过去了， 第' + str(count) + '张图片, 图片名称', filename, '， 文件夹名称：', num, '， 识别结果：', character)

        if character != num:
            print('第'+str(count) +'张图片, 图片名称', filename,'， 文件夹名称：',num, '， 识别结果：', character)
            os.remove(ori_image_path)
            image.save('../AllFile/classificated-images/'+character+'/'+filename)
        count += 1
        # image.save('../AllFile/gotoclass/' + filename)

def resultClassifier(image):
    img = Step_3_GetFeatures.binValue(image)
    feature_list = Step_3_GetFeatures.getFeatureValue160(img)  # 获取特征值

    # 特征值整合成一行
    dict = {}
    # print(dict)
    for num in range(len(feature_list)):
        dict[num + 1] = feature_list[num]

    list = [dict]
    model = svm_load_model('../AllFile/model_file_3')  # 加载模型
    p_label, p_acc, p_val = svm_predict([0], list, model, '-q')  # 预测识别
    # print(p_label)
    return str(int(p_label[0]))  # 添加到结果字符串

if __name__ == '__main__':
    # characterClassifier()
    main()