from svmutil import *

####  训练特征集
####  并生成model文件


def main():
    # 读取测试模型
    yt, xt = svm_read_problem('../ALLfile/feature_3.txt')
    model = trainSvmModel()

    print('测试:')
    p_label, p_acc, p_val = svm_predict(yt, xt, model)
    print("结果:\n", p_label)


# 训练模型
def trainSvmModel():
    # 读取特征值文件
    y, x = svm_read_problem('../AllFile/feature_final.txt')

    #训练得到模型
    model = svm_train(y, x, '-q')# 静默模式

    # 保存模型
    svm_save_model('../AllFile/model_file_final', model)

    return model # 返回模型

if __name__ == '__main__':
    main()