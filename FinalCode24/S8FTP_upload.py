import os
import pandas as pd
import numpy as np
import time
import sys

sys.path.append('E:\\workspace\\work\\Correct\\CorrectClass\\')
from get_now_time import GetNowTime
from ftp_load import FtpLoad

np.set_printoptions(suppress=True)

if __name__ == '__main__':
    timeStart = time.time()
    print('【开始运行上传报文程序】')
    ftpHost = '10.181.8.180'
    ftpPort = 21
    ftpUsr = 'forecast'
    ftpPwd = 'forecast'
    ftpBasePath = '\\Temperature\\'
    localBasePath = 'F:\\work\\2020Correct\\data\\'
    fangFa = ['TM_Result_Grid_20\\', 'TM_Result_DA\\', 'TM_Result_StaionAdd\\DA\\', 'TM_Result_StaionAdd\\MB\\']
    fangfa1h = 'TM_Result_Grid_1h\\'
    logPath = 'F:\\work\\2020Correct\\data\\log\\'
    listEle = ['TMAX', 'TMIN', 'TMP']
    getTimeOb = GetNowTime('2020100108')
    nowTime = getTimeOb.qiBaoShiJian
    ftpOb = FtpLoad(ftpHost, ftpPort, ftpUsr, ftpPwd)
    ftpConnect = ftpOb.ftpConnet
    for i in listEle:
        if i == 'TMAX' or i == 'TMIN':
            for eFangFa in fangFa:
                try:
                    ftpOb.ftp_upload(localBasePath + eFangFa + i + '\\' + nowTime[2:-2] + '.024', ftpBasePath + eFangFa + i + '\\' + nowTime[2:-2] + '.024')
                except Exception as e:
                    print('无法上传文件，原因为:')
                    print(e)
                    with open(logPath + '上传资料报错_' + getTimeOb.nowBJTStr + '.log', 'a+') as logfo:
                        logfo.writelines(localBasePath + eFangFa + i + '\\' + nowTime[2:-2] + '.024无法上传\n')
                        logfo.writelines(str(e) + '\n')
        elif i == 'TMP':
            listTemp2 = [i + '\\' + nowTime[2:-2] + '.' + str(x * 3).zfill(3) for x in range(1, 9)]
            for j in listTemp2:
                try:
                    ftpOb.ftp_upload(localBasePath + fangFa[0] + j, ftpBasePath + fangFa[0] + j)
                except Exception as e:
                    print('无法上传文件，原因为:')
                    print(e)
                    with open(logPath + '上传资料报错_' + getTimeOb.nowBJTStr + '.log', 'a+') as logfo:
                        logfo.writelines(localBasePath + fangFa[0] + j + '无法上传\n')
                        logfo.writelines(str(e) + '\n')
            listTemp3 = [nowTime[2:-2] + '.' + str(x).zfill(3) for x in range(1, 25)]
            for k in listTemp3:
                try:
                    ftpOb.ftp_upload(localBasePath + fangfa1h + k, ftpBasePath + fangfa1h + k)
                except Exception as e:
                    print('无法上传文件，原因为:')
                    print(e)
                    with open(logPath + '上传资料报错_' + getTimeOb.nowBJTStr + '.log', 'a+') as logfo:
                        logfo.writelines(localBasePath + fangfa1h + k + '无法上传\n')
                        logfo.writelines(str(e) + '\n')

    costTime = time.time() - timeStart
    print("运行时间：【%.4f】秒" % costTime)
