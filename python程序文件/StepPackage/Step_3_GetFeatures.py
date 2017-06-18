import os
from PIL import Image

## 获取每张图片的特征值
## 一张图片的特征值为一行
## 并写入txt文件

# 批量操作
def main():
    # 遍历去噪后的图片
    rootdir = "../AllFile/classificated-images/"
    for parent, dirnames, filenames in os.walk(rootdir):
        # filenames.sort(key=lambda x: int(x[:-4]))
        for filename in filenames:
            image = Image.open(os.path.join(parent, filename))
            image = binValue(image)
            feature_list = getFeatureValue160(image)
            saveFeatureValue(parent.split('/', 3)[3].strip(), feature_list)

#保存特征值到txt文件
def saveFeatureValue(label, list):
    file_write = open('../AllFile/feature_final.txt', mode='a', encoding='utf-8')

    file_write.write(label)# 写入标签
    #写入list
    for num in range(len(list)):
        file_write.writelines(" " + str(num+1) + ":" + str(list[num]))

    file_write.write("\n")
    file_write.close()

#获取特征值 数量 = 行数 + 列数
def getFeatureValue26(image):
    width, height = image.size # 获取宽和高
    feature_value_list = [] # 特征值列表
    ## 第一次遍历 得到每行的特征值
    for y_row in range(height):
        pix_cnt_x = 0 # 黑点数量
        for x_column in range(width):
            if image.getpixel((x_column, y_row)) == 0:  # 黑色点
                pix_cnt_x += 1

        feature_value_list.append(pix_cnt_x)

    ## 第二次遍历 得到每列的特征值
    for x_column in range(width):
        pix_cnt_y = 0 # 黑点数量
        for y_row in range(height):
            if image.getpixel((x_column, y_row)) == 0:  # 黑色点
                pix_cnt_y += 1

        feature_value_list.append(pix_cnt_y)

    return feature_value_list

#获取特征值 数量 = 行数 × 列数
def getFeatureValue160(image):
    width, height = image.size # 获取宽和高

    feature_value_list = [] # 特征值列表

    # total_0 = 0
    for y_row in range(height):
        # row_0 = 0
        for x_column in range(width):
            feature_value_list.append(find0Points(image, x_column, y_row))
            # if image.getpixel((x_column, y_row)) == 0:
            #     row_0 += 1

        # feature_value_list.append(row_0)

    # feature_value_list.append(total_0)


    return feature_value_list

# 寻找孤立点 返回黑点8领域的黑点数量加自己
def find0Points(image, x_column, y_row):
    # 判断图片的长宽度下限
    cur_pixel = image.getpixel((x_column, y_row))  # 当前像素点的值
    width, height = image.size # 获取宽和高

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


def binValue(image):
    img_grey = image.convert('L')  # 灰度化

    threshold = 128  # 阀值
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    img_bin = img_grey.point(table, '1')  # 二值化

    """
     for i in range(img_bin.width):
            for j in range(img_bin.height):
                print(img_bin.getpixel((i, j)), end=" ")
            print()
        print()
    """

    return img_bin


if __name__ == '__main__':
    main()