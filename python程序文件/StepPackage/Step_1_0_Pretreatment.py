from PIL import Image
import os.path
import numpy
from numpy import *
from StepPackage.Step_1_2_RemoveLine import *

### No.1 灰度化
### No.2 大小归一化
### No.3 去干扰线
### No.4 二值化
### No.5 去除噪声


def main():
    #遍历源文件的所有图片 并去噪
    rootdir = "D:\Desktop\数字图像处理\期末大作业\软件相关\图片集\历史图片及原图\pictures2/" # 图片文件的根目录
    filenames = [] # 图片名称集合
    count = 1 #计数器
    for parent, dirnames, _filenames in os.walk(rootdir):
        _filenames.sort(key=lambda x: int(x[:-4]))
        filenames = _filenames

    for filename in filenames:
        if count < 4022:
            count += 1
            continue

        print('预处理', filename, 'count:', count)
        image = Image.open(rootdir + filename)
        image = imageZoom(image)# NO.1 NO.2
        ### NO.3
        image_refine = Step_1_1_ImageRefine.startRefine(image) #抽取骨架
        remove_noise_line = Step_1_2_RemoveLine.RemoveNoiseLine(image_refine, image)
        line_has, image_result = remove_noise_line.start()
        image = binarization(image_result)# No.4
        is_once, image = removeNoise(image)# No.5
        while is_once:
            is_once, image = removeNoise(image)  # No.5
            # image.show()

        ##再次查找是否有干扰线 直到没有
        while line_has:
            image_refine = startRefine(image)  # 抽取骨架
            remove_noise_line = Step_1_2_RemoveLine.RemoveNoiseLine(image_refine, image)
            line_has, image_result = remove_noise_line.start()
            image = binarization(image_result)  # No.4
            is_once, image = removeNoise(image)  # No.5
            # image.show()
            while is_once:
                is_once, image = removeNoise(image)  # No.5
                # image.show()

        # res_img.show()
        image.save("../AllFile/pic2_preared_images/"+str(count)+'.jpg')
        count += 1
        # if count is 100:
        #     break

### No.1 灰度化  No.2 图形切割前缩放 变成 60 × 20 便于处理
def imageZoom6020(image):
    image = image.convert('L')  # 灰度化
    width, height = image.size # 获取图像的宽和高
    zoom_k = min(width/60, height/20)# 缩放倍数
    # print('缩放倍数', zoom_k)

    # 缩放后的长宽
    new_w = int(width / zoom_k)
    new_h = int(height / zoom_k)
    # print("宽和高", new_w, " ", new_h)

    # 缩放后的新数组
    image_matrix = zeros([new_h, new_w])

    for x_column in range(new_w):
        for y_row in range(new_h):
            # 新图像坐标对应原图像的坐标
            x = x_column * zoom_k
            y = y_row * zoom_k
            #print(x, end=" ")
            #print(y)

            # 向下取整
            m = int(x)
            n = int(y)

            # 获取浮点数
            float_x = x - m
            float_y = y - n
            # print(float_x, end=" ")
            # print(float_y)

            # 边界判断
            if m+1 >= width:
                m = width-2
            if n+1 >= height:
                n = height-2

            # print(m, ' ', n)
            # print("4个点{},{},{},{}".format(image.getpixel((m,n)),image.getpixel((m,n+1)),image.getpixel((m+1,n)), image.getpixel((m+1,n+1))))
            first_n_pix = (image.getpixel((m,n+1))-image.getpixel((m,n))) * float_y + image.getpixel((m,n))
            second_n_pix = (image.getpixel((m+1, n+1)) - image.getpixel((m+1,n))) * float_y + image.getpixel((m+1,n))
            #print(int((second_n_pix - first_n_pix) * float_x + first_n_pix))
            image_matrix[y_row][x_column] = int((second_n_pix - first_n_pix) * float_x + first_n_pix)

    new_data = numpy.reshape(image_matrix,(new_h,new_w))
    #print(type(new_data))
    new_im = Image.fromarray(new_data)
    #new_im.show()## 显示图片

    return new_im

### No.4 二值化
def binarization(image):
    img_grey = image.convert('L')  # 灰度化

    threshold = 128  # 二值化阀值
    table = [] #二值化依据
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    img_bin = img_grey.point(table, '1')  # 二值化

    return img_bin

### No.5 去除噪声
def removeNoise(image):
    width, height = image.size  # 获取宽和高

    is_once = False #是否继续去噪
    for x_column in range(width):
        for y_row in range(height):
            # 黑点周围黑点数（包括自己）少于3的 去掉黑点 设为白色
            if 0 < findIsolatedPoints(image, x_column, y_row) < 3:
                image.putpixel((x_column, y_row), 1)
                is_once = True

    return is_once, image#返回去噪声的图片

# 寻找孤立点 返回黑点8领域的黑点数量
def findIsolatedPoints(image, x_column, y_row):
    # 判断图片的长宽度下限
    cur_pixel = image.getpixel((x_column, y_row))  # 当前像素点的值
    width, height = image.size # 获取宽和高

    if cur_pixel == 1:  # 如果当前点为白色区域,则不统计邻域值
        return 0

    if y_row == 0:  # 第一行
        if x_column == 0:  # 左上顶点,4邻域
            # 中心点旁边3个点
            sum = cur_pixel + image.getpixel((x_column, y_row + 1)) \
                  + image.getpixel((x_column + 1, y_row)) + image.getpixel((x_column + 1, y_row + 1))
            return 4 - sum
        elif x_column == width - 1:  # 右上顶点
            sum = cur_pixel  + image.getpixel((x_column, y_row + 1)) \
                  + image.getpixel((x_column - 1, y_row)) + image.getpixel((x_column - 1, y_row + 1))
            return 4 - sum
        else:  # 最上非顶点,6邻域
            sum = image.getpixel((x_column - 1, y_row)) + image.getpixel((x_column - 1, y_row + 1)) \
                  + cur_pixel + image.getpixel((x_column, y_row + 1)) \
                  + image.getpixel((x_column + 1, y_row)) + image.getpixel((x_column + 1, y_row + 1))
            return 6 - sum
    elif y_row == height - 1:  # 最下面一行
        if x_column == 0:  # 左下顶点
            # 中心点旁边3个点
            sum = cur_pixel  + image.getpixel((x_column + 1, y_row)) \
                  + image.getpixel((x_column + 1, y_row - 1)) + image.getpixel((x_column, y_row - 1))
            return 4 - sum
        elif x_column == width - 1:  # 右下顶点
            sum = cur_pixel  + image.getpixel((x_column, y_row - 1)) \
                  + image.getpixel((x_column - 1, y_row)) + image.getpixel((x_column - 1, y_row - 1))
            return 4 - sum
        else:  # 最下非顶点,6邻域
            sum = cur_pixel  + image.getpixel((x_column - 1, y_row)) \
                  + image.getpixel((x_column + 1, y_row)) + image.getpixel((x_column, y_row - 1)) \
                  + image.getpixel((x_column - 1, y_row - 1)) + image.getpixel((x_column + 1, y_row - 1))
            return 6 - sum
    else:  # y不在边界
        if x_column == 0:  # 左边非顶点
            sum = image.getpixel((x_column, y_row - 1)) + cur_pixel \
                  + image.getpixel((x_column, y_row + 1)) + image.getpixel((x_column + 1, y_row - 1)) \
                  + image.getpixel((x_column + 1, y_row)) + image.getpixel((x_column + 1, y_row + 1))
            return 6 - sum
        elif x_column == width - 1:  # 右边非顶点
            sum = image.getpixel((x_column, y_row - 1)) + cur_pixel \
                  + image.getpixel((x_column, y_row + 1)) + image.getpixel((x_column - 1, y_row - 1)) \
                  + image.getpixel((x_column - 1, y_row)) + image.getpixel((x_column - 1, y_row + 1))
            return 6 - sum
        else:  # 具备9领域条件的
            sum = image.getpixel((x_column - 1, y_row - 1)) + image.getpixel((x_column - 1, y_row)) \
                  + image.getpixel((x_column - 1, y_row + 1)) + image.getpixel((x_column, y_row - 1)) \
                  + cur_pixel  + image.getpixel((x_column, y_row + 1)) + image.getpixel((x_column + 1, y_row - 1)) \
                  + image.getpixel((x_column + 1, y_row)) + image.getpixel((x_column + 1, y_row + 1))
            return 9 - sum

if __name__ == '__main__':
    main()