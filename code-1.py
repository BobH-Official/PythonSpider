import requests  # 获取文件
from lxml import etree  # 分析HTML
import time  # 用于暂停一段时间
import os  # 调用系统功能

root = os.getcwd() + '/'  # 这里加上’/‘是为了后面方便
# 手动储存log，我喜欢这么做，方便日后查看失败的请求
logPath = root + 'log.txt'
log = open(logPath, 'a')  # 我用续写模式，也可以用'w'
# 开头写一些分隔符
log.write('#############################################\n')
log.write(time.strftime('%Y-%m-%d %a. %H:%M:%S',
                        time.localtime(time.time())))  # 写入时间
log.write('#############################################\n')


def logprint(text):
    print(text)
    log.write(text + '\n')


# Get Page HTML


def getPageHTML(url, triedNum=0, sleepTime=5, tryNum=20):
    logprint('>>>>正在访问: {}'.format(url))
    # 获取页面
    data = requests.get(url)
    # 处理状态
    statusCode = data.status_code
    if not statusCode == 200:
        data = 'timeout'
        # 不要放弃，再试几次，我设置的20次，可以在参数设置
        if triedNum <= tryNum:
            logprint('>>>>休息 {} 秒'.format(sleepTime))
            time.sleep(sleepTime)
            logprint('>>>>重新访问: '+url+' : '+str(triedNum))
            triedNum = triedNum + 1
            getPageHTML(url=url, triedNum=triedNum, tryNum=tryNum)
        else:
            logprint('>>>>尝试 {} 次无效'.format(tryNum))
    return data


# Get Picture Data
def getInfo(page):
    # Get Picture URL
    logprint('>>>>正在获取URL信息')
    data = page
    selector = etree.HTML(data.text)
    returnUrl = selector.xpath('/html/body/div[3]/div/div/img/@src')
    # Get Picture Name
    logprint('>>>>正在获取NAME信息')
    returnName = selector.xpath('/html/body/div[3]/div/div/div[1]/h3/text()')
    # Get Picture Date
    logprint('>>>>正在获取DATE信息')
    returnDate = selector.xpath(
        '/html/body/div[3]/div/div/div[1]/p[1]/em/text()')
    return [returnUrl, returnName, returnDate]
######################
# 注意XPath，把递归的部分删去，etree 会自己递归，然后返回一个list
# MARK: - Save Image


def saveImage(imgUrl, path, imgName):
    if not os.path.exists(path):  # 判断文件夹是否已经存在
        os.makedirs(path)
    imgPath = path + imgName
    if not os.path.exists(imgPath):  # 判断文件是否已经存在
        img = requests.get(imgUrl).content  # 获取文件的二进制编码
        file = open(imgPath, "wb")  # 用二进制模式打开
        file.write(img)  # 直接写入二进制文件
        logprint('>>>>file #' + imgName + ' written')
    else:
        logprint('>>>>file #' + imgName + ' already exists')


################################################################################
######################################MAIN######################################
################################################################################
for i in range(1, 121):
    # 创建当前页面URL
    url = 'https://bing.ioliu.cn/?p={}'.format(i)
    # 获取页面
    page = getPageHTML(url)
    # 判断是不是timeout//函数抛出'timeout'
    if page == 'timeout':
        logprint('>>>>!!!!!!!BROKEN!!!!!!!\n>>>>{}\n>>>>{}\n>>>>!!!!!!!BROKEN!!!!!!!'.format(
            url, time.strftime('%Y-%m-%d %a. %H:%M:%S', time.localtime(time.time()))))
    else:
        # 获取页面信息
        dataUrl = getInfo(page).0  # get a string
        dataName = getInfo(page).1  # get a list
        dataDate = getInfo(page).2  # get a list
        # 依次获取12张图片
        for s in range(0, 12):
            # 读取图片信息
            imgUrl = dataUrl[s]
            imgName = dataDate[s] + '_[' + dataName[s] + '].jpeg'
            # 保存图片
            logprint('>>>>获取 #第 {} 页__第 {} 张'.format(i, s))
            saveImage(imgUrl=imgUrl, path=root + 'IMG/', imgName=imgName)
            # 休息 5 秒
            logprint('>>>>休息 5 秒')
            time.sleep(5)
