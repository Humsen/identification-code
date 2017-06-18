import requests
from PIL import Image
from selenium import webdriver

### 下载验证码

### 此处为东南大学信息门户预约场馆验证码和教务处验证码
def main():
    #图片地址
    #img_url = "http://xk.urp.seu.edu.cn/jw_css/getCheckCode"
    # img_url = "http://ids2.seu.edu.cn/amserver/verify/image.jsp"
    img_url = ''

    # 模拟浏览器的头文件
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
        'Upgrade-Insecure-Requests': '1',
        'Connection': 'keep-alive',
        'Host': 'xk.urp.seu.edu.cn',
    }

    for i in range(10000):
        print("正在下载第",i+1,"个...")
        img = requests.get(img_url, headers=headers)
        pic_name = '../pictures1/'+str(i+1)+'.jpg'
        file_pic = open(pic_name, 'ab')  # 存储图片，多媒体文件需要参数b（二进制文件）
        file_pic.write(img.content)  # 多媒体存储content
        file_pic.close()

## 模拟浏览器登录 截图今日头条登录界面验证码
def getPictures():
    ## 加载驱动器 打开浏览器
    path = "C:\chromedriver.exe"
    browser = webdriver.Chrome(executable_path=path)
    browser.set_page_load_timeout(30)  # 防止页面加载个没完
    # self.browser.maximize_window()
    browser.set_window_size(1366, 768)

    for i in range(10000):
        print("正在下载第", i + 1, "个...")
        ##跳转到今日头条登录界面
        browser.get('https://sso.toutiao.com/login/')
        element = browser.find_element_by_xpath("html/body/div/div[1]/div[2]/div/div/div/form/div[2]/div/img")
        pic_url = element.get_attribute('src')
        # 跳转到验证码页面
        browser.get(pic_url)
        # 截屏
        browser.save_screenshot('screen.jpg')
        element = browser.find_element_by_xpath("xhtml:html/xhtml:body/xhtml:img")
        left = element.location['x']  # 验证码图片左上角横坐标
        top = element.location['y']  # 验证码图片左上角纵坐标
        right = left + element.size['width']  # 验证码图片右下角横坐标
        bottom = top + element.size['height']  # 验证码图片右下角纵坐标
        ## 截取验证码
        im = Image.open('screen.jpg')
        im_crop = im.crop((left, top, right, bottom))  # 这个im_crop就是从整个页面截图中再截出来的验证码的图片
        pic_name = 'D:\Desktop\数字图像处理\期末大作业\图片集\pictures3/' + str(i + 293) + '.jpg'
        im_crop.save(pic_name)

if __name__ == '__main__':
    # main()
    getPictures()