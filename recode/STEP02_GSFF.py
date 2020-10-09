import ftplib
import numpy as np
import datetime
import time
import os
import shutil
from GNT.get_now_time import GetNowTime
from FL.ftp_load import FtpLoad

# GSFF为GetSCMOCFromFTP缩写




def check_dir_mkdir(path1):
    '''
    检查路径文件夹是否存在，如不存在则新建
    :param path1:
    :return:
    '''
    if not os.path.exists(path1):
        os.mkdir(path1)
    else:
        print('已新建文件夹')


def check_data(pathG, element, pathS):
    global timeStr
    if os.path.exists(pathG + timeStr[1][:4] + '\\' + timeStr[1][:-2] + '\\' + element + '_' + timeStr[1] + '.024'):
        gridDataPath = pathG + timeStr[1][:4] + '\\' + timeStr[1][:-2] + '\\' + element + '_' + timeStr[1] + '.024'
        savePath = pathS + timeStr[1] + '_' + element + '.txt'
        shutil.copyfile(gridDataPath, savePath)
        print('【当前%s指导预报存在，已完成拷贝】' % timeStr[1])
    elif os.path.exists(pathG + timeStr[2][:4] + '\\' + timeStr[2][:-2] + '\\' + element + '_' + timeStr[2] + '.048'):
        gridDataPath = pathG + timeStr[2][:4] + '\\' + timeStr[2][:-2] + '\\' + element + '_' + timeStr[2] + '.048'
        savePath = pathS + timeStr[1] + '_' + element + '.txt'
        shutil.copyfile(gridDataPath, savePath)
        print('【当前%s指导预报不存在，已完成拷贝前一天%s指导预报拷贝】' % (timeStr[0], timeStr[2]))

    elif os.path.exists(pathG + timeStr[3][:4] + '\\' + timeStr[3][:-2] + '\\' + element + '_' + timeStr[3] + '.072'):
        gridDataPath = pathG + timeStr[3][:4] + '\\' + timeStr[3][:-2] + '\\' + element + '_' + timeStr[3] + '.072'
        savePath = pathS + timeStr[1] + '_' + element + '.txt'
        shutil.copyfile(gridDataPath, savePath)
        print('【今日、昨日指导预报不存在，已完成拷贝%s指导预报拷贝】' % timeStr[3])
    else:
        print('近三个时次无资料')


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


if __name__ == '__main__':
    # 一些参数和路径
    print('【开始运行获取预报格点程序】')
    ftpHost = '10.1.72.215'
    ftpPort = 21
    ftpUsr = 'bexn'
    ftpPwd = 'BEXN111'
    # 从get_now_time函数中获取时间
    timeStart = time.time()

    getTimeOb = GetNowTime()
    getTimeOb.print_all_attribute_of_object()
    timeStr = [getTimeOb.qiBaoShiJian,getTimeOb.nowTimeStr,getTimeOb.previousTimeS,getTimeOb.previousBeforeTimeS]

    nowTime = getTimeOb.qiBaoShiJian
    logPath = 'F:\\work\\2020Correct\\data\\log\\'
    ftpBasePath = '\\SCMOC\\BEXN\\' + nowTime[:4] + '\\'  # FTP一级目录
    localSaveGBasePath = 'F:\\work\\2020Correct\\data\\NWGD\\' + nowTime[:4] + '\\'  # 本地GRIB一级目录
    localSaveTBasePath = 'F:\\work\\2020Correct\\data\\GRID\\' + nowTime[:4] + '\\'  # 本地存储一级目录
    eleList = ['SCMOC-TMP', 'SCMOC-TMAX', 'SCMOC-TMIN']  # 所需下载要素的列表
    finalSaveGPath = localSaveGBasePath + nowTime[:-4]
    finalSaveTPath = localSaveTBasePath + nowTime[:-4]
    ftpFilePath = ftpBasePath + nowTime[:-4]
    pathG = 'F:\\work\\2020Correct\\data\\GRID\\'
    pathS = 'F:\\work\\2020Correct\\data\\TM_md_24h_Grid\\'
    element = ['TMAX', 'TMIN']
    #############下载资料#########################
    ftpOb = FtpLoad(ftpHost, ftpPort, ftpUsr, ftpPwd)
    ftpConnect = ftpOb.ftpConnet
    fileList = ftpConnect.nlst(ftpFilePath)

    for eEle in eleList:
        listtemp1 = []
        for eFile in fileList:
            # print(eFile.split('_'))
            eleName = eFile.split('_')
            # eleName[7]为SCMOC_TXXXX,[8]为起报时间
            if eEle == eleName[7]:
                if eleName[8] == nowTime:
                    sizeOfFile = ftpConnect.size(ftpFilePath + '\\' +  eFile)
                    # 判断该文件是否大于1m，小于1m的文件可能是坏文件，不下载
                    if sizeOfFile > 1000:
                        listtemp1.append(eFile)

        # 对listtemp1进行排序，最后一个即最新的预报
        if listtemp1 == []:
            print('当前时刻%s格点指导文件不存在' % eEle)
            aaa = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            if int(nowTime[-4:-2]) == 20 and int(aaa[-6:-4]) >= 15 and int(aaa[-6:-4]) < 18:
                with open(logPath + 'GRID_SCMOC_' + eEle + aaa[:-4] + '.log', 'w') as logf1:
                    logf1.write('当前时刻为' + eEle + aaa + '\n')
                    logf1.write('{}时{}指导报尚未能获取'.format(nowTime, eEle))
                continue
            if int(nowTime[-4:-2]) == 8 and int(aaa[-6:-4]) > 4 and int(aaa[-6:-4]) < 9:
                with open(logPath + 'GRID_SCMOC_' + eEle + aaa[:-4] + '.log', 'w') as logf1:
                    logf1.write('当前时刻为' + aaa + '\n')
                    logf1.write('{}时{}指导报尚未能获取'.format(nowTime, eEle))
                continue
            continue
        else:
            donwloadFile = sorted(listtemp1)[-1]

        ftpOb.ftp_download(finalSaveGPath + '\\' + donwloadFile, ftpFilePath + '\\' + donwloadFile)
    # ################转资料为TXT#####################
    aa = sorted(os.listdir(finalSaveGPath + '\\'))
    print(aa)
    for i in aa:
        # eleName[7]为SCMOC_TXXXX,[8]为起报时间
        if i.split('_')[7] == 'SCMOC-TMP':
            # wgrib中需要1.x作为索引，以SCMOC为例（其他grib文件不一定如此），1.1为第一个时次要素，1.2为第二个，以此类推。
            # TMP选1-25是1.1开始至1.24，为前72h逐三小时的各时次资料，TMAX和TMIN为1.1开始至1.3的前72h逐24h资料
            if i.split('_')[8] == nowTime:
                for num in range(1, 25):
                    numStr = '1.' + str(num)
                    grib2_to_txt(finalSaveGPath + '\\' + i, finalSaveTPath + '\\' + i.split('_')[7][6:] + '_' + nowTime[:-2] + '.' + str(num * 3).zfill(3),
                                 numStr)
            else:
                continue
        elif i.split('_')[7] == 'SCMOC-TMAX' or i.split('_')[7] == 'SCMOC-TMIN':
            if i.split('_')[8] == nowTime:
                for num in range(1, 4):
                    numStr = '1.' + str(num)
                    grib2_to_txt(finalSaveGPath + '\\' + i, finalSaveTPath + '\\' + i.split('_')[7][6:] + '_' + nowTime[:-2] + '.' + str(num * 24).zfill(3),
                                 numStr)
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
                print('%s完成转码' % j)
    ####################################################
    for eEle in element:
        aa = check_data(pathG, eEle, pathS)

    costTime = time.time() - timeStart
    print("【程序已执行完成，总计运行时间：%.4f秒】" % costTime)
