import ftplib
import numpy as np
import datetime
import time
import pandas as pd
import os
import re
# GSFF为GetSCMOCFromFTP缩写

def timer(function):
    def wrapper(*args, **kwargs):
        time_start = time.time()
        res = function(*args, **kwargs)
        cost_time = time.time() - time_start
        print("运行时间：【%.4f】秒" %  cost_time)
        return res

    return wrapper

def get_now_time(duringDays):
    '''
    按当天日期和时间判断指导报起报时间
    获取当前时间，判断当前时间是否超过中午12点，如果超过则返回当天日期+'2000'，如果未超过则返回当天日期+'0800'
    :return: 起报时间
    '''

    startTimeStr = '2020051407'
    startTime = datetime.datetime.strptime(startTimeStr, '%Y%m%d%H')
    getTime = startTime + datetime.timedelta(hours=12*duringDays)
    getTimeStr = getTime.strftime('%Y%m%d%H')#时间格式转化为字符串格式
    nowHour = int(getTimeStr[-2:])#字符串中获取小时并转为整数
    # 若当前时间在下午13时之前，则设置起报时间为0800，否则设置为2000
    if nowHour < 13:
        qiBaoShiJian = getTimeStr[:-2] + '0800'
    else:
        qiBaoShiJian = getTimeStr[:-2] + '2000'
    return qiBaoShiJian

def check_dir_mkdir(path1):
    '''
    检查路径文件夹是否存在，如不存在则新建
    :param path1:
    :return:
    '''
    if not os.path.exists(path1):
        os.mkdir(path1)
    else:
        print('存在')

def grib2_to_txt(origPathANDFileName, savePathANDFileName, num):
    '''
    用grads自带wgrib解码SCMOC文件，并输出为一个txt文件
    :param origPathANDFileName: SCMOC文件目录和文件名的字符串组合
    :param savePathANDFileName: 输出的txt文件目录和文件名的字符串组合
    :return:
    '''
    os.chdir("D:\\Program Files (x86)\\opengrads\\Contents\\Cygwin\\Versions\\2.1.a2.oga.1\\i686\\")
    readGrib2File = "wgrib2 " + origPathANDFileName + " -v"  # os.system中wgrib需要的资料路径
    os.system(str(readGrib2File))
    # 用wgrib将grib2资料转为txt文本文件
    executePath = "wgrib2 " + origPathANDFileName + " -d " + num + " -no_header -text " + savePathANDFileName
    os.system(executePath)

class GetDataFromFTP(object):

    def __init__(self,host,port,username,passwd,nowTime,ftpBasePath,localBasePath):
        self.host = host
        self.port = port
        self.username = username
        self.passwd = passwd
        self.nowTime = nowTime
        self.ftpBasePath = ftpBasePath
        self.localBasePath = localBasePath

    def ftp_connect(self):
        '''
        连接FTP
        :param host: FTP地址
        :param port: FTP端口
        :param username: FTP用户名
        :param passwd: FTP密码
        :return: 返回ftp对象
        '''
        ftp = ftplib.FTP()
        try:
            ftp.connect(self.host, self.port)
        except:
            raise IOError("FTP服务器连接失败")
        try:
            ftp.login(self.username, self.passwd)
        except:
            raise IOError("FTP用户名或密码错误")
        else:
            print("FTP连接登录成功")
            return ftp

    def download_ftp_file(self,eleList):
        '''
        从ftp中下载资料，用之前ftpconnect返回的对象
        :param ftpHost: ftp地址
        :param ftpPort: ftp端口
        :param ftpUsr: ftp用户名
        :param ftpPwd: ftp密码
        :param nowTime: 当前时间
        :param eleList: 要素列表
        :param ftpFilePath: ftp内文件路径
        :param localFilePath: 本地文件路径
        :return:
        '''
        # 引用mkdir_new_dir函数
        filePath = self.mkdir_new_dir()
        ftpFilePath = filePath[0]
        localFilePath = filePath[1]
        # 连接ftp函数
        ftpconnect = self.ftp_connect()
        # 遍历FTP下ftpFilePath路径文件
        fileList = ftpconnect.nlst(ftpFilePath)
        print(ftpFilePath)
        # 分别读取不同要素，匹配要素名、起报时间，并将符合要求的文件写入listtemp1列表中
        for eEle in eleList:
            listtemp1 = []
            for eFile in fileList:
                eleName = eFile.split('_')
                # eleName[7]为SCMOC_TXXXX,[8]为起报时间
                if eEle == eleName[7]:
                    if eleName[8] == self.nowTime:
                        sizeOfFile = ftpconnect.size(ftpFilePath + eFile)
                        # 判断该文件是否大于1m，小于1m的文件可能是坏文件，不下载
                        if sizeOfFile > 1000:
                            listtemp1.append(eFile)
            # 对listtemp1进行排序，最后一个即最新的预报
            if listtemp1 == []:
                continue
            else:
                donwloadFile = sorted(listtemp1)[-1]
            # 下载并写入本地
            file_handle = open(localFilePath + donwloadFile, "wb").write
            ftpconnect.encoding = 'utf-8'
            ftpconnect.retrbinary('RETR %s' % ftpFilePath + '\\' + donwloadFile, file_handle)
            print('%s已下载完成'%donwloadFile)


    def mkdir_new_dir(self):
        '''
        检查是否有当天日期的文件夹，如有则pass，没有则新建
        :param nowTime: 获取当天日期
        :param localFilePath: 本地路径
        :return:
        '''
        listTemp = sorted(os.listdir(self.localBasePath))
        if self.nowTime[:-4] not in listTemp:
            os.mkdir(self.localBasePath + '\\' + self.nowTime[:-4])
            print('%s文件夹不存在，已新建'%self.nowTime[:-4])
            ftpFilePath = self.ftpBasePath + nowTime[:-4] + '\\'  # FTP文件内的目录
            localFilePath = self.localBasePath + nowTime[:-4] + '\\'  # 本地文件内的目录
        else:
            ftpFilePath =  self.ftpBasePath + listTemp[-1] + '\\'
            localFilePath = self.localBasePath + listTemp[-1] + '\\'
        return ftpFilePath, localFilePath


class TxtToMICAPS(object):

    def __init__(self):
        pass







if __name__ == '__main__':
    #一些参数和路径
    ftpHost = '10.1.72.215'
    ftpPort = 21
    ftpUsr = 'bexn'
    ftpPwd = 'BEXN111'
    # 从get_now_time函数中获取时间
    timeStart = time.time()

    for i in range(5):

        nowTime = get_now_time(i)
        print(nowTime)
        ftpBasePath = '\\SCMOC\\BEXN\\' + nowTime[:4] + '\\' # FTP一级目录
        localSaveGBasePath = 'E:\\work\\2020Correct\\data\\NWGD\\' + nowTime[:4] + '\\'#本地GRIB一级目录
        localSaveTBasePath = 'E:\\work\\2020Correct\\data\\GRID\\' + nowTime[:4] + '\\'#本地存储一级目录
        eleList = ['SCMOC-TMP', 'SCMOC-TMAX', 'SCMOC-TMIN']  # 所需下载要素的列表
        finalSaveGPath = localSaveGBasePath + nowTime[:-4]
        finalSaveTPath = localSaveTBasePath + nowTime[:-4]
        ##############下载资料#########################
        ob1 = GetDataFromFTP(ftpHost,ftpPort,ftpUsr,ftpPwd,nowTime,ftpBasePath,localSaveGBasePath)# 调用GDFF类创建对象
        ob1.download_ftp_file(eleList)# 调用GDFF类对象方法
        check_dir_mkdir(finalSaveTPath)
        ################转资料为TXT#####################
        aa = sorted(os.listdir(finalSaveGPath + '\\'))
        print(aa)
        for i in aa:
            # eleName[7]为SCMOC_TXXXX,[8]为起报时间
            if i.split('_')[7] == 'SCMOC-TMP':
                # wgrib中需要1.x作为索引，以SCMOC为例（其他grib文件不一定如此），1.1为第一个时次要素，1.2为第二个，以此类推。
                # TMP选1-25是1.1开始至1.24，为前72h逐三小时的各时次资料，TMAX和TMIN为1.1开始至1.3的前72h逐24h资料
                if i.split('_')[8] == nowTime:
                    for num in range(1,25):
                        numStr = '1.' + str(num)
                        grib2_to_txt(finalSaveGPath + '\\' + i ,finalSaveTPath + '\\' + i.split('_')[7][6:]+ '_' + nowTime[:-2] + '.' + str(num * 3).zfill(3), numStr)
                else:
                    continue
            elif i.split('_')[7] == 'SCMOC-TMAX' or i.split('_')[7] == 'SCMOC-TMIN':
                if i.split('_')[8] == nowTime:
                    for num in range(1,4):
                        numStr = '1.' + str(num)
                        grib2_to_txt(finalSaveGPath + '\\' + i ,finalSaveTPath + '\\' + i.split('_')[7][6:] + '_' + nowTime[:-2]  + '.' + str(num * 24).zfill(3), numStr)
                else:
                    continue
        ################转TXT为MICAPS4######################
        bb = sorted(os.listdir(finalSaveTPath + '\\'))
        for j in bb:
            pathTemp = finalSaveTPath + '\\' + j
            if j[-14:-4] == nowTime[:-2]:
                arrTemp = np.loadtxt(pathTemp).reshape(256, 373)[51:212, 48:322] - 273.15
                array2 = arrTemp < 100  # 数据小于100才写入文件
                if array2.any() == True:
                    np.savetxt(finalSaveTPath + '\\' + j, arrTemp, fmt='%.2f')


    costTime = time.time() - timeStart
    print("运行时间：【%.4f】秒" % costTime)




