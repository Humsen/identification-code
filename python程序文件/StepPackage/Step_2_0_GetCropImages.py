import os
from PIL import Image
from numpy import *
import numpy
from StepPackage.Step_1_0_Pretreatment import removeNoise

### 根据去噪后的二值化图像切割
### 得到验证码的每个字母图像

def main():
    #遍历去噪后的图片
    rootdir = "../AllFile/pic2_preared_images/"
    filenames = []
    for parent, dirnames, _filenames in os.walk(rootdir):
        _filenames.sort(key=lambda x: int(x[:-4]))
        filenames = _filenames

    # count = 0
    for filename in filenames:
        image = Image.open(os.path.join(parent, filename))
        img_bin = binarization(image)#二值化
        image = beforCrop(img_bin)#切割前处理
        is_once, image = removeNoise(image)#去噪
        res_img_list = getCropImages(image)#切割
        same_img_list = []
        #大小归一化
        for img in res_img_list:
            width, height = img.size  # 获取图像的宽和高
            # 删除异常图片
            if width < 3 or height < 4:
                continue

            same_img_list.append(imageZoom(img))

        saveCropImages(same_img_list, filename.split('.')[0])#保存
        # count += 1
        # if count == 5000:
        #     break

### 保存验证码切割后的图像
def saveCropImages(img_list, ori_name):
    for num in range(len(img_list)):
        img_list[num].save('../AllFile/pic2_preared_images_crop/'+ori_name+'-'+str(num+1)+'.jpg')

### 去除图像每列黑点小于等于2的噪声
def beforCrop(image):
    width, height = image.size  # 获取宽和高
    # 遍历每一列
    for x_column in range(width):
        count = 0 #每列黑点数量
        for y_row in range(height):
            if image.getpixel((x_column, y_row)) == 0:
                count += 1

        #如果黑点小于等于2
        if count <= 2:
            for i in range(height):
                image.putpixel((x_column, i), 1)

    return image

### 切割后去除周围噪声
def afterCrop(image):
    width, height = image.size  # 获取宽和高
    # 遍历每一行得到上面是否有小于等于2的黑点
    top_row = 0 #上面从哪行切割
    bottom_row = height #下面从哪行切割

    for y_row in range(height):
        count_top = 0  # 从上面开始的行数量
        count_bottpm = 0  # 从下面开始的行数量
        for x_column in range(width):
            if image.getpixel((x_column, y_row)) == 0:
                count_top += 1
            if image.getpixel((x_column, height-1 - y_row)) == 0:
                count_bottpm += 1

        # 如果黑点小于等于2
        if count_top <= 2 or count_bottpm <= 2:
            top_row = y_row+1 if count_top < 3 else top_row
            bottom_row = height-1-y_row if count_bottpm < 3 else bottom_row
        else:
            break

    if top_row != 0 or bottom_row != height:
        ## 有的为空
        if bottom_row == top_row:
            return False
        image.show()
        # image.save('1.jpg')
        image = image.crop((0, top_row, width, bottom_row))  # 切割一次
        image.show()
        # print(image)
        # image.save('2.jpg')

    return image

### 切割验证码图像
def getCropImages(image):
    width, height = image.size # 获取宽和高

    ## 先将字符竖着切开 去掉左右的冗余白边
    child_img_list_temp = []
    left = -1# 每个字符左边的坐标
    is_bk = False# 是否break跳出循环
    # 从最左边一列开始一列一列遍历
    for x_column in range(width):
        # 对每一列，遍历每一行
        for y_row in range(height):
            is_bk = False
            #如果一个字符的最左边还没有定位
            if left == -1 and image.getpixel((x_column, y_row)) == 0:#左边未定位 为黑色
                left = x_column
                is_bk = True
                break
            elif left != -1 and image.getpixel((x_column, y_row)) == 0:#左边已经定位 等于黑色
                is_bk = True
                break

        # 左边已经定位,且此列全为白色,并且跳出宽度小于等于6的噪声
        if not is_bk and left != -1 and x_column-left > 6:
            child_img = image.crop((left, 0, x_column, height))# 切割一次

            ## 判断是否有多个字符连接在一起
            if x_column - left > 20:
                cut_position = 0# 切割的地方
                cur_min_count = height #初始化当前最小数量的列
                is_jump = False#是否超过跳出
                # 从最左边一列开始一列一列遍历
                for i in range(child_img.width):
                    # 对每一列，遍历每一行
                    count = 0# 每列黑点数量
                    for j in range(height):
                        if child_img.getpixel((i, j)) == 0:
                            count += 1
                            # 如果当前列黑点数大于当前最小 则不符合条件 跳出
                            if count >= cur_min_count:
                                is_jump = True
                                break

                    # 如果当前列黑点数没有大于当前最小 则为最小
                    if not is_jump:
                        cur_min_count = count
                        cut_position = i

                child_img1 = child_img.crop((0, 0, cut_position, height))  # 切割一次
                child_img2 = child_img.crop((cut_position+1, 0, child_img.width, height))  # 再切割一次
                #添加重复切割后的截图
                child_img_list_temp.append(child_img1)
                child_img_list_temp.append(child_img2)
            else:
                child_img_list_temp.append(child_img)  # 切割后的图像添加到list

            left = -1
            is_bk = False

    ## 去掉每个字符上下的冗余空白
    child_img_list = []
    for child_image in child_img_list_temp:
        top = -1  # 每个字符上面的坐标
        is_bk = False  # 是否break跳出循环
        for y_row in range(height):
            # 对每一行 遍历每一列
            for x_column in range(child_image.width):
                # 如果一个字符的最上边还没有定位
                if top == -1 and child_image.getpixel((x_column, y_row)) == 0:  # 上面未定位 为黑色
                    top = y_row
                    break
                if top != -1 and child_image.getpixel((x_column, height-1-y_row)) == 0:  # 上面已经定位 等于黑色
                    is_bk = True
                    break

            # 上面已经定位,且此行全为白色
            if top != -1 and is_bk:
                # child_image.show()
                child_img = child_image.crop((0, top, child_image.width, height-y_row)) # 再次切割
                # child_img.show()
                # child_img = afterCrop(child_img)
                # child_img.show()
                if child_img:
                    child_img_list.append(child_img) # 保存到list

                break

    return child_img_list # 返回切割后的子图

### 切割后的图像归一化 10 × 16
def imageZoom1016(image):
    image = image.convert('L')
    width, height = image.size # 获取图像的宽和高
    # print('图片宽和高', width, ' ', height)

    zoom_kx = width/10# 缩放倍数
    zoom_ky = height/16
    # print('缩放倍数', zoom_k)

    # 缩放后的长宽
    new_w = 10
    new_h = 16
    # print("宽和高", new_w, " ", new_h)

    # 缩放后的新数组
    image_matrix = zeros([new_h, new_w])

    for x_column in range(new_w):
        for y_row in range(new_h):
            # 新图像坐标对应原图像的坐标
            x = x_column * zoom_kx
            y = y_row * zoom_ky

            # 向下取整
            m = int(x)
            n = int(y)

            float_x = x - m # 浮点数x
            float_y = y - n # 浮点数y

            # 边界判断
            m = width - 2 if m+1 >= width else m
            n = height - 2 if n+1 >= height else n
            m = 0 if m < 0 else m
            n = 0 if n < 0 else n

            # print('m和n', m, ' ', n, '宽和高', width, ' ', height)
            first_n_pix = (image.getpixel((m,n+1))-image.getpixel((m,n))) * float_y + image.getpixel((m,n))
            second_n_pix = (image.getpixel((m+1, n+1)) - image.getpixel((m+1,n))) * float_y + image.getpixel((m+1,n))
            image_matrix[y_row][x_column] = int((second_n_pix - first_n_pix) * float_x + first_n_pix)

    new_data = numpy.reshape(image_matrix,(new_h,new_w))
    new_im = Image.fromarray(new_data)
    # new_im.show()## 显示图片
    new_im = new_im.convert('L')
    return new_im

### 二值化
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

if __name__ == '__main__':
    main()