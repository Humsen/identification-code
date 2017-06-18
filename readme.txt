在python程序文件夹下有四个文件：

1.StepPackage——Python程序的包
2.AllFile——包括特征文件以及模型
  其中feature代表特征文件，model_file代表模型，final表示为最终版本。
3.pictures1——第一类验证码图片选取200张
4.pictures2——第二类验证码图片选取200张

python程序包中的Step_6_IdentifyVCodeProgram为主程序，只需运行该程序即可。然后可选择pictures1和pictures2中的图片进行验证识别。

运行程序所需环境：python3
以及python第三方库libsvm包，此包安装比较复杂。
libsvm包安装可参考博客：http://blog.csdn.net/eunicechen/article/details/51555427