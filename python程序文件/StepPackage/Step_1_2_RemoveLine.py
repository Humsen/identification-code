from math import *
from StepPackage.Step_1_1_ImageRefine import *
from StepPackage.Step_1_0_Pretreatment import *
from numpy import *
import numpy

## 去除干扰线
## 采用深度优先算法

class RemoveNoiseLine:
    ####### 初始化
    def __init__(self, image_refine, image_ori):
        ## 初始化
        self.line_list = []  # 存储所有干扰线
        self.line_matrix = zeros([28, 60]) + 255
        self.head_node_list = []  # 存储干扰线的头结点 防止重复
        self.reserve_set = set()  # 存储防止误删的点
        self.is_one_head_line = [] #是否是只有一个头结点的干扰线
        img_grey = image_refine.convert('L')  # 灰度化

        threshold = 128  # 二值化阀值
        table = []  # 二值化依据
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)

        image = img_grey.point(table, '1')  # 二值化
        # image.save('1.jpg')
        self.image = image
        self.image_ori = image_ori
        self.width, self.height = image.size
        self.image_matrix = zeros([self.height+2,self.width+2], numpy.int16)-1

        for x_row in range(self.height):
            for y_col in range(self.width):
                self.image_matrix[x_row + 1][y_col + 1] = image.getpixel((y_col, x_row))

    # 开始搜索
    def start(self):
        # 遍历图像
        for x_row in range(self.height):
            for y_col in range(self.width):
                # 不为黑色节点 跳过
                if self.image.getpixel((y_col, x_row)) != 0:
                    continue

                # 不为端节点 跳过
                neighbor_list = self.getNeighborNodes((x_row, y_col))
                if len(neighbor_list) != 1:
                    continue

                # print('\n\n\n\n出发节点', (x_row, y_col), end=' ,')
                cur_node = (x_row, y_col)# 第一个节点
                node_list = [cur_node]   # 初始化节点列表
                chain_angle_list = []    # 初始化角度列表
                cur_visited = [cur_node] # 初始化访问列表
                line_length = 0          # 初始化路径长度
                direction = [(180 - 45 * i) for i in range(8)] # 初始化干扰线大方向

                # 只有一个邻居节点
                neighbor = neighbor_list[0]
                next_direction = self.getTheta(cur_node, neighbor)  # 邻居和当前节点的夹角
                # print('第一个邻居', neighbor, '方向', next_direction, '\n')
                once_length = 1 if next_direction % 90 == 0 else 1.414  # 路径长度

                # 大方向
                direction = [direction[(direction.index(next_direction) - 1 + i) % 8] for i in range(3)]
                # print('\n大方向', direction, '\n')

                line_length += once_length # 添加路径长度

                node_list.append(neighbor)  # 添加到干扰线节点列表
                chain_angle_list.append(next_direction)
                cur_visited.append(neighbor)  # 把邻居添加到已访问

                # 以当前邻居节点为邻居继续搜索
                self.dfsLine(neighbor, node_list, line_length, chain_angle_list, cur_visited, cur_node, direction)

        # 如果没有找到干扰线 返回False和原图
        if not self.line_list:
            return 0, self.image_ori
        # print('干扰线：', self.line_list)
        # print('干扰线数量', len(self.line_list))

        # 画出每一条干扰线
        # new_image = zeros([self.height, self.width])+255
        # for line in self.line_list:
        #     print(len(line))
            # print(line)
            # for node in line:
            #     if node not in self.reserve_set:
            #         new_image[node[0]][node[1]] = 0
        #
        # new_data = numpy.reshape(new_image, (self.height, self.width))
        # new_im = Image.fromarray(new_data)
        # new_im.show()
        # new_im = new_im.convert('L')
        # new_im.save('r.jpg')

        # 将干扰线应用于图像
        for line in self.line_list:
            # 如果是只有一个头结点的线 尾部为字符 去掉最后5个节点
            if line[0] in self.is_one_head_line:
                for i in range(5):
                    line.pop()

            for node in line:
                if node not in self.reserve_set:
                    self.image_ori.putpixel((node[1], node[0]), 255)

        # self.image_ori.show()
        # self.image_ori.save('res.jpg')
        return 1, self.image_ori

    # 深度优先搜索干扰线
    def dfsLine(self, cur_node, node_list, line_length, chain_angle_list, cur_visited, head_node, direction):
        neighbor_list = self.getNeighborNodes(cur_node)# 获得像素为0 的邻居

        # 如果邻居数量大于2 表明该点不为纯干扰线 不删除
        if len(neighbor_list) > 2:
            self.reserve_set.add(cur_node)

        # 如果邻居为1 表明是当前点只有上一个点为邻居
        if len(neighbor_list) == 1:
            if head_node in neighbor_list:
                # print(cur_node, '孤立的两个黑点')
                return False

            # 如果当前节点已在头结点链表 说明反向重复
            if cur_node in self.head_node_list:
                return False

            #如果长度小于30 不为干扰线 干扰线一般较长
            if line_length < 30:
                return False

            self.line_list.append(node_list.copy())
            self.head_node_list.append(head_node)
            return True

        # 遍历每一个邻居节点
        for neighbor in neighbor_list:
            # 如果被访问过 跳过
            if neighbor in cur_visited:
                continue

            next_direction = self.getTheta(cur_node, neighbor)
            # print('cur_node', cur_node, '邻居', neighbor, '方向', next_direction, '上一方向', chain_angle_list[-1])
            # 如果这个邻居与上一条链的夹角小于90度
            if abs(abs(next_direction) - abs(chain_angle_list[-1])) < 90 and next_direction in direction:
                if abs(abs(next_direction)-abs(chain_angle_list[-1])) == 0: # 夹角为0 方向不变
                    line_length += 1
                else:# 夹角方向改变  链角度添加一个元素
                    line_length += sqrt(2)

                    # if not self.direction_determine:
                    #     self.direction_determine = True
                    #     大方向
                        # if next_direction > 0:
                        #     direction = [direction[(direction.index(next_direction) - i) % 8] for i in range(4)]
                        # else:
                        #     direction = [direction[(direction.index(next_direction) + i) % 8] for i in range(4)]
                        # print('\n大方向', direction, '\n')

                # print('添加方向', next_direction, '邻居', neighbor, '\n')
                chain_angle_list.append(next_direction)

                node_list.append(neighbor)# 添加到干扰线节点
                cur_visited.append(neighbor)# 把邻居添加到已访问

                # 以当前邻居节点为邻居继续搜索
                self.dfsLine(neighbor,node_list, line_length, chain_angle_list, cur_visited, head_node, direction)

                node_list.pop()
                # print('弹出方向', next_direction,'邻居', neighbor)
                chain_angle_list.pop()

            # 或者尾节点因角度无法到达 则在深度搜索返回处 根据长度找出干扰线
            elif line_length >= 30:
                ## 这种只能留一条 可能有多条
                if head_node in self.head_node_list:
                    if line_length < len(self.line_list[-1]):
                        return False
                    else:
                        self.line_list.pop(-1)
                        self.line_list.append(node_list.copy())
                        return True
                else:
                    self.is_one_head_line.append(head_node)
                    self.line_list.append(node_list.copy())
                    self.head_node_list.append(head_node)
                    return True

    ## 得到两个结点之间的方向和角度
    def getTheta(self, cur_node, nebr_node):
        x = nebr_node[1] - cur_node[1]
        y = cur_node[0] - nebr_node[0]

        hypotenuse = sqrt(x*x+y*y)
        if y >= 0:
            theta = int(acos(x/hypotenuse)*180/pi)
        else:
            theta =  - int(acos(x/hypotenuse)*180/pi)

        # print(theta)
        return theta

    # 获得每个节点的邻居节点
    def getNeighborNodes(self, cur_node):
        neighbor_list = [] # 存储邻居的list
        #print(cur_node)
        x_row, y_col = cur_node  # 获得节点坐标

        #获取节点周围的8个坐标
        for i in range(3):
            for j in range(3):
                # 去掉本身
                if i == 1 and j == 1:
                    continue

                # 去掉边缘 -1 的点
                if self.image_matrix[x_row+i][y_col+j] == -1 :
                    continue

                # 如果为黑点 则添加
                if self.image_matrix[x_row+i][y_col+j] == 0:
                    neighbor_list.append((x_row+i-1, y_col+j-1))
        # print(neighbor_list)
        return neighbor_list

def imageZoom(image):
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

if __name__ == '__main__':
    image = Image.open("D:\Desktop\数字图像处理\期末大作业\图片集\pictures2/25.jpg")
    image = image.convert('L')

    image = imageZoom(image)
    image = image.convert('L')
    image.show()
    # image.save('ori.jpg')

    image_refine = startRefine(image)
    # image.show()
    image_refine.save('ori1.jpg')
    remove_noise_line = RemoveNoiseLine(image_refine, image)
    # remove_noise_line.getNeighborNodes((4,39))
    line_has, image_result = remove_noise_line.start()
    # remove_noise_line.getTheta((1,1), (1,0))
    image = binarization(image_result)
    image = removeNoise(image)
    image.save('res1.jpg')
    while line_has:
        print('是否找到', line_has)
        image_refine = startRefine(image)
        remove_noise_line = RemoveNoiseLine(image_refine, image)
        line_has, image_result = remove_noise_line.start()
        image = binarization(image_result)
        image = removeNoise(image)

    # im.show()
    # im.show()
    # im.save('im.jpg')
    # im = removeNoise(im)
    # im.show()
    # im.save('im1.jpg')