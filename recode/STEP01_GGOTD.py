import numpy as np
import datetime
import time
import os
import sys
sys.path.append('E:\\workspace\\work\\Correct\\CorrectClass\\')
from get_now_time import GetNowTime
from ftp_load import FtpLoad


# GSFF为GetGribObversationTmpDataFromFTP缩写


def check_dir_mkdir(path1):
    '''
    检查路径文件夹是否存在，如不存在则新建
    :param path1:
    :return:
    '''
    # print('path1为',path1)
    if not os.path.exists(path1):
        os.mkdir(path1)
    else:
        print('已新建文件夹')


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
    print('【开始运行获取实况格点程序】')
    ftpHost = '10.1.72.215'
    ftpPort = 21
    ftpUsr = 'bexn'
    ftpPwd = 'BEXN111'

    timeStart = time.time()
    getTimeOb = GetNowTime()
    # getTimeOb.print_all_attribute_of_object()
    nowTime = getTimeOb.nowBJTStr + '00'

    ftpBasePath = '\\ANALYSIS\\CLDAS\\V2\\0P05\\' + nowTime[:4] + '\\'  # FTP一级目录
    logPath = 'F:\\work\\2020Correct\\data\\log\\'
    localSaveGBasePath = 'F:\\work\\2020Correct\\data\\TEM_ob_1h_CLDAS\\' + nowTime[:4] + '\\'  # 本地GRIB一级目录
    localSaveTBasePath = 'F:\\work\\2020Correct\\data\\TEM_ob_1h_CLDAS_GRID\\' + nowTime[:4] + '\\'  # 本地存储一级目录
    eleList = ['TEM']  # 所需下载要素的列表
    finalSaveGPath = localSaveGBasePath + nowTime[:-4]
    finalSaveTPath = localSaveTBasePath + nowTime[:-4]
    ftpFilePath = ftpBasePath + nowTime[:-4]
    #####################################下载资料##################################################################
    check_dir_mkdir(localSaveGBasePath)
    check_dir_mkdir(localSaveTBasePath)
    ftpOb = FtpLoad(ftpHost, ftpPort, ftpUsr, ftpPwd)
    ftpConnect = ftpOb.ftpConnet
    fileList = ftpConnect.nlst(ftpFilePath)

    for eEle in eleList:
        listtemp1 = []
        for eFile in fileList:
            eleTemp = eFile.split('_')[10]
            eleName = eleTemp.split('-')
            # eleName[7]为SCMOC_TXXXX,[8]为起报时间
            if eEle == eleName[1]:
                if eleName[2][:-5] == nowTime[:-2]:
                    sizeOfFile = ftpConnect.size(ftpFilePath + '\\' + eFile)
                    # 判断该文件是否大于1m，小于1m的文件可能是坏文件，不下载
                    if sizeOfFile > 1000:
                        listtemp1.append(eFile)

        # 对listtemp1进行排序，最后一个即最新的预报
        if listtemp1 == []:
            print('当前时刻实况格点文件不存在')
            aaa = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            if int(aaa[-4:-2]) > 35:
                with open(logPath + 'GRID_1hOB_' + aaa[:-4] + '.log', 'w') as logf1:
                    logf1.write('当前时刻为' + aaa + '\n')
                    logf1.write('%s时实况资料尚未能获取' % nowTime)
            continue
        else:
            donwloadFile = sorted(listtemp1)[-1]
        # # 下载并写入本地
        ftpOb.ftp_download(finalSaveGPath + '\\' + donwloadFile, ftpFilePath + '\\' + donwloadFile)
    # # ################转资料为TXT#####################
    aa = sorted(os.listdir(finalSaveGPath + '\\'))
    for i in aa:
        nameTemp = i.split('_')[10]
        realName = i.split('-')
        # eleName[7]为SCMOC_TXXXX,[8]为起报时间
        if realName[1] == 'TEM':
            # eleName[2][:-5] == self.nowTime[:-2]:
            # wgrib中需要1.x作为索引，以SCMOC为例（其他grib文件不一定如此），1.1为第一个时次要素，1.2为第二个，以此类推。
            # TMP选1-25是1.1开始至1.24，为前72h逐三小时的各时次资料，TMAX和TMIN为1.1开始至1.3的前72h逐24h资料
            if realName[2][:-5] == nowTime[:-2]:
                numStr = '1'
                # print(finalSaveTPath + '\\' + i.split('_')[7][6:] + '_' + nowTime[:-2] + '.txt')
                grib2_to_txt(finalSaveGPath + '\\' + i, finalSaveTPath + '\\' + 'TMP_' + nowTime[:-2] + '.txt', numStr)
            else:
                continue
    ###############转TXT为MICAPS4######################
    bb = sorted(os.listdir(finalSaveTPath + '\\'))
    for j in bb:
        pathTemp = finalSaveTPath + '\\' + j
        # print(pathTemp)
        # print(j[-14:-4])
        if j[-14:-4] == nowTime[:-2]:
            arrTemp = np.loadtxt(pathTemp).reshape(1201, 1401)[628:789, 386:660] - 273.15
            array2 = arrTemp < 100  # 数据小于100才写入文件
            if array2.any():
                np.savetxt(finalSaveTPath + '\\' + j, arrTemp, fmt='%.2f')  #

    costTime = time.time() - timeStart
    print("【程序已执行完成，总计运行时间：%.4f秒】" % costTime)
