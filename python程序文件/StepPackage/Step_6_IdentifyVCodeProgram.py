# -*- coding: cp936 -*-
import os
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from PIL import Image, ImageTk
import sys
sys.path.append('../')
import StepPackage
from StepPackage.Step_5_VCodeAPI import startValidate

### 图形界面应用类
class Application(tkinter.Tk):
    ## 初始化界面
    def __init__(self):
        super().__init__() # 有点相当于tk.Tk()
        # self.geometry("500x300")  # 设置窗口大小
        self.center_window()# 水平居中
        self.createWidgets()#创建部件

    ## 创建部件
    def createWidgets(self):
        self.title('验证码识别')
        self.columnconfigure(0, minsize=50)

        # 顶部放置按钮和标签的frame
        first_frame = tkinter.Frame(self, height=80)
        first_frame.pack(side=tkinter.TOP)
        # 定义显示验证码图片和识别结果的frame
        self.second_frame = tkinter.Frame(self, height=80)
        self.second_frame.pack()

        # 定义按钮和标签
        choose_button = Button(first_frame, command=self.openImage, text='点击此处选择验证码图片')
        img_path_label = Label(first_frame, text='当前验证码图片路径:')
        # cur_image_path = Label(first_frame, text='当前没有路径信息')
        cur_image_path = Entry(first_frame, borderwidth = 3, relief = 'sunken', state = 'disabled',\
                               width=56, font = ('宋体', '10', 'bold'))
        self.pre_image_btn = Button(first_frame, command=self.preImage, text='上一张图片')
        self.next_image_btn = Button(first_frame, command=self.nextImage, text='下一张图片')
        img_name_label = Label(self.second_frame, text='验证码图片：', font = ('宋体', '15', 'bold'))
        img_label = Label(self.second_frame, text="当前无图片", relief='flat', borderwidth=10)
        interval = Label(self.second_frame, text='  ')
        img_res_label = Label(self.second_frame, text='识别结果:', font = ('宋体', '15', 'bold'))
        res_label = Label(self.second_frame, relief='flat', text='暂无', borderwidth=10)
        btn_quit = Button(self.second_frame, text='退出', font = ('黑体', '15', 'bold'), command=self.colseProgram)

        # 动态显示当前验证码路径
        self.img_path_txt = StringVar() # 存储验证码路径
        cur_image_path["textvariable"] = self.img_path_txt
        self.img_path_txt.set('当前没有路径信息')

        # 放置的位置
        choose_button.grid(row=0, rowspan=3, column = 3, sticky=tkinter.E+tkinter.W, padx=5, pady=20)

        img_path_label.grid(row=3, rowspan=3, column=0, pady=20)
        cur_image_path.grid(row=3, rowspan=3, column=2, columnspan=8, padx=5, pady=20)

        self.pre_image_btn.grid(row=6, rowspan=3, column=2, padx=5, pady=20)
        self.next_image_btn.grid(row=6, rowspan=3, column=4, padx=5, pady=20)

        img_name_label.grid(row=0, column=0, pady=60)
        img_label.grid(row=0, column=1, columnspan=2, pady=60, sticky=tkinter.W)
        interval.grid(row=0, column=3)
        img_res_label.grid(row=0, column=4, pady=60, sticky=tkinter.E)
        res_label.grid(row=0, column=5, columnspan=2, pady=60, sticky=tkinter.W)
        btn_quit.grid(row = 3, column=2, columnspan=2, pady=100)

    ## 程序界面居中对齐
    def center_window(self):
        width, height = 800, 600

        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()

        self.maxsize(screenwidth, screenheight)
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())

        size = '{}x{}+{}+{}'.format(width, height, int((screenwidth-width)/2), int((screenheight-height)/2))
        self.geometry(size)

    ## 打开图片
    def openImage(self):
        # 选择路径
        dirname = filedialog.askopenfilename(\
            filetypes=[("jpg格式", "jpg"), ("png格式", "png")], initialdir='../')

        # 错误处理
        if not dirname:
            tkinter.messagebox.showerror('错误', '尚未选择文件！')
            return

        self.img_path_txt.set(dirname)#更新路径
        self.cur_img_name = dirname# 存储当前图片的路径

        ## 切割路径 得到当前图片所在文件夹
        list = dirname.split('/')
        rootdir = ''
        for i in range(len(list) - 1):
            rootdir += (list[i] + '/')
        # print(rootdir)

        ## 找到当前文件夹下所有图片
        self.filenames = []  # 图片名称集合
        for parent, dirnames, _filenames in os.walk(rootdir):
            _filenames.sort(key=lambda x: int(x[:-4]))
            for name in _filenames:
                self.filenames.append(parent+name)

        ### 打开当前图片
        load = Image.open(dirname)
        load = load.resize((200,100))
        img = ImageTk.PhotoImage(load)
        ##显示图片
        self.img_label = Label(self.second_frame, image=img)
        self.img_label.image = img
        ##显示识别结果
        res_label = Label(self.second_frame, font = ('宋体', '20', 'bold'))
        self.res_txt = StringVar()
        res_label["textvariable"] = self.res_txt
        ## 部件位置
        self.img_label.grid(row=0, column=1, columnspan=2, pady=60, sticky=tkinter.W)
        res_label.grid(row=0, column=5, columnspan=2, pady=60, sticky=tkinter.W)
        #调用逻辑程序识别
        ori_image = Image.open(dirname)
        result = startValidate(ori_image)
        self.res_txt.set(result)

    ## 识别上一张图片
    def preImage(self):
        #当前图片在当前图片文件夹list中的位置下标
        try:
            cur_num = self.filenames.index(self.cur_img_name)
        except:
            messagebox.showerror('警告', '尚未选择图片！')
            return

        # 针对到达第1张图片警告
        if cur_num == 0:
            tkinter.messagebox.showwarning('提示', '已经是第1张图片！')
            self.pre_image_btn['state'] = DISABLED
            return

        #启用下一张按钮
        if cur_num == len(self.filenames)-1:
            self.next_image_btn['state'] = NORMAL

        #找到前一张图片完整路径
        self.cur_img_name = self.filenames[cur_num - 1]
        #更新路径
        self.img_path_txt.set(self.cur_img_name)
        #显示图片
        self.showImg(self.cur_img_name)

    ## 识别下一张图片
    def nextImage(self):
        # 当前图片在当前图片文件夹list中的位置下标
        try:
            cur_num = self.filenames.index(self.cur_img_name)
        except:
            messagebox.showerror('警告', '尚未选择图片！')
            return
        # 针对到达最后一张图片警告
        if cur_num == len(self.filenames)-1:
            tkinter.messagebox.showwarning('提示', '已经是最后一张图片！')
            self.next_image_btn['state'] = DISABLED
            return

        # 启用上一张按钮
        if cur_num == 0:
            self.pre_image_btn['state'] = NORMAL

        # 找到后一张图片完整路径
        self.cur_img_name = self.filenames[cur_num + 1]
        # 更新路径
        self.img_path_txt.set(self.cur_img_name)
        # 显示图片
        self.showImg(self.cur_img_name)

    ## 显示图片
    def showImg(self, path):
        # 加载图片
        load = Image.open(path)
        load = load.resize((200, 100), Image.ANTIALIAS)
        self.next_img = ImageTk.PhotoImage(load)
        # 切换图片
        self.img_label.configure(image=self.next_img)
        # 启用逻辑程序识别
        ori_image = Image.open(path)
        result = startValidate(ori_image)
        # print('result', result)
        self.res_txt.set(result)

    ## 添加菜单栏
    def addmenu(self, Menu):
        Menu(self)#添加当前

    ## 退出
    def colseProgram(self):
        self.quit()

### 菜单类
class MyMenu():
    ## 初始化
    def __init__(self, root):
        self.menubar = tkinter.Menu(root) # 创建菜单栏
        # 创建“文件”下拉菜单
        filemenu = tkinter.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="打开", command=root.openImage)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=root.quit)
        # 将前面两个菜单加到菜单栏
        self.menubar.add_cascade(label="文件", menu=filemenu)
        self.menubar.add_cascade(label="关于", command=self.help_about)
        # 最后再将菜单栏整个加到窗口 root
        root.config(menu=self.menubar)

    ## 帮助菜单
    def help_about(self):
        messagebox.showinfo('关于', '作者：何明胜 \n版本： Version 1.0 \n邮箱：husen@hemingsheng.cn \n\n\t\t\t感谢您的使用！ \n\n\n\t版权所有@2017')  # 弹出消息提示框


if __name__ == '__main__':
    #### 验证码识别的图形化界面
    application = Application()  # 实例化Application
    application.addmenu(MyMenu)  # 添加菜单
    application.mainloop()  # 主消息循环
