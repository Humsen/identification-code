from PIL import Image
from StepPackage import Step_1_0_Pretreatment, Step_1_2_RemoveLine


## 细化图像 抽取骨架

####### 开始

def startRefine(ori_image):
    img_grey = ori_image.convert('L')  # 灰度化

    threshold = 200  # 二值化阀值
    table = []  # 二值化依据
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    image = img_grey.point(table, '1')  # 二值化
    # image.show()

    # for x_row in range(height):
    #     for y_col in range(width):
    #         print(image_matrix[x_row][y_col], end=' ')
    #     print()
    count = 0
    while 1:
        removeNodules(image)
        count += 1

        if count == 20:
            break

    # print('count',count)
    return image

##细化图像 抽取骨架
def removeNodules(image):
    #事先做好的表
    array = [0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, \
             1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, \
             0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, \
             1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, \
             1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
             1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, \
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
             0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, \
             1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, \
             0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, \
             1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, \
             1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
             1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, \
             1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, \
             1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0]

    is_go = True # 是否继续
    w, h = image.size
    # 水平扫描
    next = 1
    for i in range(h):
        for j in range(w):
            if next == 0:
                next = 1
            else:
                m = image.getpixel((j - 1, i)) + image.getpixel((j + 1, i)) if 0 < j < w - 1 else 1
                if image.getpixel((j, i)) == 0 and m != 0:
                    a = [1] * 9
                    for k in range(3):
                        for l in range(3):
                            if -1 < (i - 1 + k) < h and -1 < (j - 1 + l) < w and image.getpixel(
                                    (j - 1 + l, i - 1 + k)) == 0:
                                a[k * 3 + l] = 0
                    sum = a[0] * 1 + a[1] * 2 + a[2] * 4 + a[3] * 8 + a[5] * 16 + a[6] * 32 + a[7] * 64 + a[8] * 128
                    image.putpixel((j, i), array[sum] * 255)
                    if array[sum] == 1:
                        is_go = False
                        next = 0

    # 竖直扫描
    next = 1
    for j in range(w):
        for i in range(h):
            if next == 0:
                next = 1
            else:
                m = image.getpixel((j, i - 1)) + image.getpixel((j, i + 1)) if 0 < i < h - 1 else 1
                if image.getpixel((j, i)) == 0 and m != 0:
                    a = [1] * 9
                    for k in range(3):
                        for l in range(3):
                            if -1 < (i - 1 + k) < h and -1 < (j - 1 + l) < w and image.getpixel(
                                    (j - 1 + l, i - 1 + k)) == 0:
                                a[k * 3 + l] = 0
                    sum = a[0] * 1 + a[1] * 2 + a[2] * 4 + a[3] * 8 + a[5] * 16 + a[6] * 32 + a[7] * 64 + a[8] * 128
                    image.putpixel((j, i), array[sum] * 255)
                    if array[sum] == 1:
                        is_go = False
                        next = 0

    # image.show()
    # image.save('r2.jpg')

    return is_go

if __name__ == '__main__':
    image = Image.open("D:\Desktop\数字图像处理\期末大作业\软件相关\图片集\历史图片及原图\pictures1/2.jpg")
    image = Step_1_0_Pretreatment.imageZoom6020(image)  # NO.1 NO.2
    ### NO.3
    image_refine = startRefine(image)  # 抽取骨架
    remove_noise_line = Step_1_2_RemoveLine.RemoveNoiseLine(image_refine, image)
    line_has, image_result = remove_noise_line.start()
    image.show()