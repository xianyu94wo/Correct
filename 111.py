import sys
import numpy as np
import datetime
import time
import os
import shutil

sys.path.append('E:\\workspace\\work\\Correct\\CorrectClass\\')
from get_now_time import GetNowTime
from ftp_load import FtpLoad
from FNP import FindNearestPoint

'''
本段代码功能为下载格点指导预报资料并解码
GSFF为GetSCMOCFromFTP缩写
'''


def check_dir_mkdir(path1):
    '''
    检查路径文件夹是否存在，如不存在则新建
    :param path1:
    :return:
    '''
    if not os.path.exists(path1):
        os.mkdir(path1)


def check_data(pathG, element, pathS):
    '''
    检查指导报存在情况，如当日不存在，则获取前一日
    :param pathG: 获取格点指导原始路径
    :param element: 要素
    :param pathS:  获取格点指导拷贝路径
    :return:
    '''
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
    timeStart = time.time()
    print('【开始运行获取预报格点程序】')
    ##################################### 一些参数和路径
    # 格点范围
    sPLat = 31.40
    mRLat = 0.05
    sPLon = 89.3
    mRLon = 0.05
    # FTP参数
    ftpHost = '10.1.72.215'
    ftpPort = 21
    ftpUsr = 'bexn'
    ftpPwd = 'BEXN111'
    # 从GetNowTime对象中获取时间参数
    getTimeOb = GetNowTime()
    # getTimeOb.print_all_attribute_of_object()
    timeStr = [getTimeOb.qiBaoShiJian, getTimeOb.nowTimeStr, getTimeOb.previousTimeS, getTimeOb.previousBeforeTimeS]
    nowTime = getTimeOb.qiBaoShiJian  # 当前时次的起报时间
    # 路径
    stationInfoFilePath = 'E:\\work\\2020Correct\\data\\StationInfo_648.txt' # 站点目录
    logPath = 'F:\\work\\2020Correct\\data\\log\\'  # 日志目录
    ftpFilePath = '\\SCMOC\\BEXN\\' + nowTime[:4] + '\\' + nowTime[:-4]  # FTP二级目录
    finalSaveGPath = 'F:\\work\\2020Correct\\data\\NWGD\\' + nowTime[:4] + '\\' + nowTime[:-4]  # 本地GRIB二级目录
    finalSaveTPath = 'F:\\work\\2020Correct\\data\\GRID\\' + nowTime[:4] + '\\' + nowTime[:-4]  # 本地存储二级目录
    copySrcPath = 'F:\\work\\2020Correct\\data\\GRID\\'  # 拷贝原始目录
    copyDstPath = 'F:\\work\\2020Correct\\data\\TM_md_24h_Grid\\'  # 拷贝目标目录
    stationResPath = 'F:\\work\\2020Correct\\data\\TM_md_24h_648\\'
    # 要素列表
    eleFTPList = ['SCMOC-TMP', 'SCMOC-TMAX', 'SCMOC-TMIN']  # 所需下载要素的列表，为SCMOC中的文件名，其-与_不同，如切片需多做一步，故有此列表，与下列表区分
    element = ['TMAX', 'TMIN']  # 要素名
    ################################开始执行
    # 检查是否有当天文件夹，如无则新建
    # check_dir_mkdir(finalSaveGPath)
    # check_dir_mkdir(finalSaveTPath)
    # #############从FTP下载格点指导资料#########################
    # ftpOb = FtpLoad(ftpHost, ftpPort, ftpUsr, ftpPwd)  # 建立FTP对象
    # ftpConnect = ftpOb.ftpConnet
    # fileList = ftpConnect.nlst(ftpFilePath)  # 遍历FTP目录
    # for eEle in eleFTPList:  # 对每个要素在FTP下查找
    #     listtemp1 = []  # 存放符合当前起报时次的相应要素的指导预报
    #     for eFile in fileList:
    #         eleName = eFile.split('_')  # 对FTP下每个文件名进行切片，继续
    #         if eEle == eleName[7]:  # 如果列表中的要素与文件名切片后第八段相等，则表示有该要素的文件，继续（eleName[7]为SCMOC_TXXXX,[8]为起报时间）
    #             if eleName[8] == nowTime:  # 如果该文件第九段与所需起报时间一致，继续
    #                 sizeOfFile = ftpConnect.size(ftpFilePath + '\\' + eFile)  # 判断文件大小，如果大于1000，则认为非坏文件，则将其文件名添加到listtemp1中
    #                 if sizeOfFile > 1000:  # 判断该文件是否大于1m，小于1m的文件可能是坏文件，不下载
    #                     listtemp1.append(eFile)
    #     if listtemp1 == []:  # 当该列表为空时，表示无符合条件的文件
    #         print('当前时刻%s格点指导文件不存在' % eEle)
    #         aaa = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # 此处aaa为当前时间，方便写log
    #         if int(nowTime[-4:-2]) == 20 and int(aaa[-6:-4]) >= 15 and int(aaa[-6:-4]) < 18:  # 20时指导报文没来，则执行下列log写入功能
    #             with open(logPath + 'GRID_SCMOC_' + eEle + aaa[:-4] + '.log', 'w') as logf1:
    #                 logf1.write('当前时刻为' + eEle + aaa + '\n')
    #                 logf1.write('{}时{}指导报尚未能获取'.format(nowTime, eEle))
    #             continue
    #         if int(nowTime[-4:-2]) == 8 and int(aaa[-6:-4]) > 4 and int(aaa[-6:-4]) < 9:  # 08时指导报文没来，则执行下列log写入功能
    #             with open(logPath + 'GRID_SCMOC_' + eEle + aaa[:-4] + '.log', 'w') as logf1:
    #                 logf1.write('当前时刻为' + aaa + '\n')
    #                 logf1.write('{}时{}指导报尚未能获取'.format(nowTime, eEle))
    #             continue
    #         continue
    #     else:
    #         donwloadFile = sorted(listtemp1)[-1]  # 考虑到SCMOC实时更新，因此对listtemp1进行排序，最后一个即最新的预报
    #     ftpOb.ftp_download(finalSaveGPath + '\\' + donwloadFile, ftpFilePath + '\\' + donwloadFile)
    # #################转GRIB资料为TXT#####################
    # aa = sorted(os.listdir(finalSaveGPath + '\\'))  # 遍历GRIB文件夹，考虑到文件名随机并可能有多个，此处只能用遍历
    # for i in aa:
    #     # eleName[7]为SCMOC_TXXXX,[8]为起报时间
    #     if i.split('_')[7] == 'SCMOC-TMP':
    #         # wgrib中需要1.x作为索引，以SCMOC为例（其他grib文件不一定如此），1.1为第一个时次要素，1.2为第二个，以此类推。
    #         # TMP选1-25是1.1开始至1.24，为前72h逐三小时的各时次资料，TMAX和TMIN为1.1开始至1.3的前72h逐24h资料
    #         if i.split('_')[8] == nowTime:
    #             for num in range(1, 25):
    #                 numStr = '1.' + str(num)
    #                 grib2_to_txt(finalSaveGPath + '\\' + i, finalSaveTPath + '\\' + i.split('_')[7][6:] + '_' + nowTime[:-2] + '.' + str(num * 3).zfill(3),
    #                              numStr)
    #         else:
    #             continue
    #     elif i.split('_')[7] == 'SCMOC-TMAX' or i.split('_')[7] == 'SCMOC-TMIN':
    #         if i.split('_')[8] == nowTime:
    #             for num in range(1, 4):
    #                 numStr = '1.' + str(num)
    #                 grib2_to_txt(finalSaveGPath + '\\' + i, finalSaveTPath + '\\' + i.split('_')[7][6:] + '_' + nowTime[:-2] + '.' + str(num * 24).zfill(3),
    #                              numStr)
    #         else:
    #             continue
    # #################转TXT为MICAPS4######################
    # bb = sorted(os.listdir(finalSaveTPath + '\\'))
    # for j in bb:
    #     pathTemp = finalSaveTPath + '\\' + j
    #     if j[-14:-4] == nowTime[:-2]:
    #         arrTemp = np.loadtxt(pathTemp).reshape(256, 373)[51:212, 48:322] - 273.15
    #         array2 = arrTemp < 100  # 数据小于100才写入文件
    #         if array2.any() == True:
    #             np.savetxt(finalSaveTPath + '\\' + j, arrTemp, fmt='%.2f')
    #             print('    【%s完成转码】' % j)
    # #################拷贝到所需文件夹###########################
    # for eEle in element:  # 检查是否有当天指导预报，如果没有，则取前一天，具体可看函数注释
    #     cc = check_data(copySrcPath, eEle, copyDstPath)
    ################选取模式的站点预报结果###########################
    FNPob = FindNearestPoint(sPLat, sPLon, mRLat, mRLon)
    gridNumList = FNPob.output_grid_num()
    for eEle in element:
        listTemp = []
        gridDataPath = copyDstPath + getTimeOb.nowTimeStr + '_' + eEle + '.txt'
        gridData = np.loadtxt(gridDataPath)
        for eNum in gridNumList:
            singleData = gridData[eNum[0] - 1, eNum[1] - 1]
            listTemp.append(singleData)
        ar1 = np.array(listTemp)
        np.savetxt(stationResPath + getTimeOb.nowTimeStr + '_' + eEle + '.txt', ar1, fmt='%.2f')

    ########################
    costTime = time.time() - timeStart
    print("【程序已执行完成，总计运行时间：%.4f秒】" % costTime)
