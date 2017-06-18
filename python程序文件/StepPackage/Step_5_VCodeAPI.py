from StepPackage import Step_1_0_Pretreatment
from StepPackage import Step_2_0_GetCropImages
from StepPackage import Step_3_GetFeatures
from svmutil import *
from PIL import Image
from StepPackage.Step_1_1_ImageRefine import startRefine
from StepPackage.Step_1_0_Pretreatment import removeNoise, binarization
from StepPackage.Step_2_0_GetCropImages import *
from StepPackage import Step_1_2_RemoveLine

def main():
    # 遍历源文件的所有图片 并去噪
    rootdir = "D:\Desktop\数字图像处理\期末大作业\软件相关\图片集\历史图片及原图\pictures2/"

    for count in range(100):
        print('{}.jpg'.format(count+1), end=" ---> ")
        image = Image.open(rootdir+str(count+1078)+'.jpg')
        startValidate(image)

## 开始实践
def startValidate(image):
    ### Step1 图像预处理
    res = ''# 存储结果的字符串

    image = Step_1_0_Pretreatment.imageZoom6020(image)  # NO.1 NO.2
    ### NO.3
    image_refine = startRefine(image)  # 抽取骨架
    remove_noise_line = Step_1_2_RemoveLine.RemoveNoiseLine(image_refine, image)
    line_has, image_result = remove_noise_line.start()
    image = binarization(image_result)  # No.4
    is_once, image = removeNoise(image)  # No.5
    while is_once:
        is_once, image = removeNoise(image)  # No.5

    ##再次查找是否有干扰线 直到没有
    while line_has:
        image_refine = startRefine(image)  # 抽取骨架
        remove_noise_line = Step_1_2_RemoveLine.RemoveNoiseLine(image_refine, image)
        line_has, image_result = remove_noise_line.start()
        image = binarization(image_result)  # No.4
        is_once, image = removeNoise(image)  # No.5
        while is_once:
            is_once, image = removeNoise(image)  # No.5

    ### Step2 图像切割
    image = binarization(image)  # 二值化
    image = beforCrop(image) #切割前处理
    is_once, image = removeNoise(image)#去噪
    res_img_list = getCropImages(image)  # 切割
    same_img_list = []
    # 大小归一化
    for img in res_img_list:
        width, height = img.size  # 获取图像的宽和高
        # 删除异常图片
        if width < 3 or height < 4:
            continue

        # img.show()
        same_img_list.append(imageZoom1016(img))

    ### Step3 提取特征值
    for img in same_img_list:
        img = Step_3_GetFeatures.binValue(img)
        feature_list = Step_3_GetFeatures.getFeatureValue160(img)  # 获取特征值

        # 特征值整合成一行
        dict = {}
        # print(dict)
        for num in range(len(feature_list)):
            dict[num + 1] = feature_list[num]

        list = [dict]
        ### Step4 识别字符
        model = svm_load_model('../AllFile/model_file_final')  # 加载模型
        p_label, p_acc, p_val = svm_predict([0], list, model, '-q') # 预测识别
        # print(p_label)
        res += str(int(p_label[0])) # 添加到结果字符串

    # print('识别结果：', res)
    return res