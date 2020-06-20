import requests  # 获取文件
from lxml import etree  # 分析HTML
import time  # 用于暂停一段时间
import random  # 随机数生成
import os  # 调用系统功能
from selenium import webdriver  # 自动操作工具webdriver

root = os.getcwd() + '/'  # 这里加上’/‘是为了后面方便
if not os.path.exists(root + 'bilibili/'):
    os.mkdir(root + 'bilibili/')
if not os.path.exists(root + 'bilibili/content/'):
    os.mkdir(root + 'bilibili/content/')

logPath = root + 'log.txt'
log = open(logPath, 'a')  # 我用续写模式，也可也用'w'
# 开头写一些分隔符
log.write('#############################################\n')
log.write(time.strftime('%Y-%m-%d %a. %H:%M:%S',
                        time.localtime(time.time())))  # 写入时间
log.write('#############################################\n')


def logprint(text):
    print(text)
    log.write(text + '\n')


# 储存错误
brokenLogPath = root + 'bilibili/bilibiliBrokenLog.txt'
brokenLog = open(brokenLogPath, "a")
brokenLog.write('\n')
brokenLog.write('@@@@@@START@@@@@@\n')


def saveBrokenLog(url, chapterNum=-1, pageNum=-1, chapterName=''):
    logprint('>>>>存入 bilibiliBrokenLog.txt')
    logprint(
        '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
    brokenLog.write('---------------\n')
    brokenLog.write('---------------\n')
    if not chapterNum == -1 and not chapterName == '':
        brokenLog.writelines(
            '>>>>>>>> #' + str(chapterNum) + ' #' + chapterName)
    if not pageNum == -1:
        brokenLog.writelines('>>>>>>>> #'+str(pageNum))
    brokenLog.writelines('>>>>>>>> #' + url)
    brokenLog.write('---------------\n')
    brokenLog.write('---------------\n')
    brokenLog.write('\n')
    brokenLog.write('\n')

# 获取页面


def getPage(url, driver, tryNum=0):
    print('>>>>正在访问: {}'.format(url))
    # 这里我们用到了webdriver
    driver.get(url)
    # 等待动态加载，网速不好的可以等的时间长一点
    logprint(">>>>睡 5 秒")
    time.sleep(5)
    data = driver.page_source
    dataInfo = etree.HTML(data)
    # 这里是判断是否是404，由于用了webdriver，手动判断会方便一点
    is404 = dataInfo.xpath('/html/body/div[3]/img/@class')
    logprint(">>>>得到 #{}".format(url))
    if is404 == ['img-404']:
        data = 'timeout'
        # 尝试 20 次
        if tryNum <= 20:
            logprint('>>>>休息10s')
            time.sleep(10)
            logprint('>>>>重新访问: '+url+' : '+str(tryNum))
            tryNum = tryNum + 1
            getPage(url=url, driver=driver, tryNum=tryNum)  # 这里有个迭代
        else:
            logprint('>>>>尝试20次无效')
    return data  # driver.page_source，或'timeout'（我全部使用字符串'timeout'来进行错误处理，方便一点）

# 获取全部页面信息


def getAllPages(driver):
    url = 'http://www.mangabz.com/287bz/'  # 写死的
    data = getPage(url=url, driver=driver)
    # 进行错误判断
    if not data == 'timeout':
        # 把数据交给etree
        selector = etree.HTML(data)
        # 获取信息
        urls = selector.xpath('/html/body/div[5]/div[2]/a/@href')
        names = selector.xpath('/html/body/div[5]/div[2]/a/text()')
        pagenums = selector.xpath('/html/body/div[5]/div[2]/a/span/text()')
        nums = []
        returnData = []
        # 处理页面编号，得把它过滤出来并从 str 改到 int
        count = 0
        for s in pagenums:
            a = ''
            count += 1
            # 简单方法，硬上
            for i in s:
                if i == '1' or i == '2' or i == '3' or i == '4' or i == '5' or i == '6' or i == '7' or i == '8' or i == '9' or i == '0':
                    a += i
            a = int(a)
            nums.append(a)
        for i in range(count + 1):
            i = i - 1
            pageLog.write('>>>>>>>>>>>>>>>>>>>>\n')
            pageLog.write('####' + str(i+1)+names[i]+urls[i]+str(nums[i])+'\n')
            pageLog.write('\n')
            returnData.append([i + 1, names[i], urls[i], nums[i]])
            # name is a string, url is a string, nums is a int which refers to how many pages this chapter got, the first one is the chapter's id
    else:
        returnData = ['timeout']
    return(returnData)  # 返回一个list，或'timeout'


# 获取每一“页”的信息
def getInfo(url, driver, tryNum=0):
    logprint('>>>>正在获取页面信息')
    data = getPage(url=url, driver=driver)
    # 进行错误处理
    if data == 'timeout':
        logprint('data of getinfo is timeout')
        imgURL = 'timeout'
        pageNum = 404
        pageName = 'timeout'
    else:
        # 把数据交给etree
        selector = etree.HTML(data)
        imgURL = selector.xpath('//*[@id="cp_image"]/@src')
        # 如果是加载出了问题，图片还没有加载出来，不要气馁，再试几次
        if imgURL == []:
            if tryNum <= 20:
                logprint('>>>>重新获取页面: '+url+' : '+str(tryNum))
                tryNum = tryNum + 1
                imgURL = 'timeout'
                getInfo(url=url, driver=driver, tryNum=tryNum)  # 迭代自己
            else:
                logprint('>>>>尝试 20 次无效')
                imgURL = 'timeout'
                pageNum = 404
                pageName = 'timeout'
                saveBrokenLog(url)
        else:
            imgURL = imgURL[0]  # 把URL从 list 转为 str（感谢弱类型）
        # 获取当前的页码
        pageNum = selector.xpath(
            '//*[@id="lbcurrentpage"]/text()')[0]  # list 转 str
        pageNum = int(pageNum)  # str 转 int
        pageName = selector.xpath('/html/body/div[1]/div/div/p/text()')[0]
        # 把空白字符处理掉
        pageName.replace('\s', '')
        abcd = ''
        for i in pageName:
            if not i == '\t':
                if not i == ' ':
                    abcd += i
        pageName = abcd

        logprint('>>>> #' + str(pageNum))
        logprint('>>>> #' + pageName)
        logprint('>>>> #' + imgURL)
    return [pageNum, imgURL, pageName]


# 获取图片
def saveImage(imgUrl, path, name):
    img = requests.get(imgUrl)
    img = img.content
    file = open(path, "wb")  # 二进制写入
    file.write(img)
    logprint('>>>>file #' + name + ' written.')


################################################################################
######################################MAIN######################################
################################################################################
# 储存获取的每一页的数据
pageLogPath = root + 'bilibili/bilibiliPageLog.txt'
pageLog = open(pageLogPath, "w")
pageLog.write('\n')
pageLog.write('@@@@@@START@@@@@@\n')


# 打开webdriver，这里用的是FireFox（也推荐使用Safari）
driver = webdriver.Firefox(executable_path='path/to/your/geckodriver')
# 开始
logprint('@@@@@@START@@@@@@')
# 获取目录里的全部页面信息，返回的是一个list嵌套的list
allChapter = getAllPages(driver=driver)
# 准备根URL
URL_b = 'http://www.mangabz.com/'
# 判断是否有返回
if allChapter == ['timeout']:
    saveBrokenLog(url='none is got')
else:
    # 获取每一话（chapter）
    for ss in range(0, 5):  # 只获取 5 个即可
        currentChapter = allChapter[ss]
        # 处理这一话的URL
        chapterURLhref = currentChapter[2]
        chapterURL = ''
        # 要把多余的'/'删去，没有在获取的时候删是为了函数里的代码更清晰一点
        for i in chapterURLhref:
            if not i == '/':
                chapterURL += i
        # 获取其他信息
        chapterTotalPages = currentChapter[3]  # 总页数
        chapterName = currentChapter[1]  # 话名称
        chapterNum = currentChapter[0]  # 话的编号
        # 获取每一个单页
        for currentPageIndex in range(chapterTotalPages):
            currentPageIndex += 1  # list是从0开始的，所以这里要转换一下
            # 当前“页”的URL
            currentPageURL = URL_b + chapterURL + \
                '/#ipg{}'.format(currentPageIndex)
            logprint('######## '+str(currentPageIndex)+'  '+currentPageURL)
            # 获取当前“页”的信息
            info = getInfo(currentPageURL, driver)
            currentImgURL = info[1]
            currentImgNum = info[0]
            currentImgName = info[2]
            # 打印每一页的数据
            logprint('>>>>当前章名: #' + currentImgName)
            logprint('>>>>当前页数: #' + str(currentImgNum))
            logprint('>>>>当前URL: #' + str(currentImgURL))
            if currentImgURL == 'timeout':
                logprint('>>>>获取页面失败')
                saveBrokenLog(currentImgURL, chapterNum,
                              currentPageIndex, currentImgName)
            else:
                # 储存路径的创立
                chapterRootPath = root + 'bilibili/content/' + \
                    str(chapterNum) + '-' + currentImgName+'/'
                if not os.path.exists(chapterRootPath):
                    os.mkdir(chapterRootPath)
                    logprint('>>>>章节路径: #{} 创建好了'.format(chapterRootPath))
                # 判断是编号是否一致，以免错误的出现
                if currentPageIndex == currentImgNum:
                    logprint('>>>>序号是一致的')
                else:
                    logprint('>>>>序号不一致')
                # 文件路径
                fileName = str(chapterNum) + '-' + str(currentImgName) + \
                    '_p_' + str(currentPageIndex)+'.jpeg'
                imgPath = chapterRootPath + fileName
                # 是否已经存在，不要重复获取
                if os.path.exists(imgPath):
                    logprint('>>>>file #{} already existed'.format(fileName))
                else:
                    # 获取图片
                    saveImage(currentImgURL, imgPath, fileName)
        # 下一话
        logprint('---------------')
        logprint('---------------')
        logprint('######NEXT######')
        logprint('---------------')
# 结束了，退出
driver.close()
brokenLog.write('@@@@@@OVER@@@@@@')
logprint('@@@@@@OVER@@@@@@')
