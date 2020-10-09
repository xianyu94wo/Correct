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
    fangFa = ['TM_Result_Grid_20\\', 'TM_Result_DA\\']
    fangfa1h = 'TM_Result_Grid_1h\\'
    listEle = ['TMAX', 'TMIN', 'TMP']
    getTimeOb = GetNowTime()
    nowTime = getTimeOb.qiBaoShiJian
    ftpOb = FtpLoad(ftpHost, ftpPort, ftpUsr, ftpPwd)
    ftpConnect = ftpOb.ftpConnet

    print(nowTime[2:-2])
    for i in listEle:
        if i == 'TMAX' or i == 'TMIN':
            for eFangFa in fangFa:
                ftpOb.ftp_upload(localBasePath + eFangFa + i + '\\' + nowTime[2:-2] + '.024', ftpBasePath + eFangFa + i + '\\' + nowTime[2:-2] + '.024')
        elif i == 'TMP':
            listTemp2 = [i + '\\' + nowTime[2:-2] + '.' + str(x * 3).zfill(3) for x in range(1, 9)]

            for j in listTemp2:
                ftpOb.ftp_upload(localBasePath + fangFa[0] + j, ftpBasePath + fangFa[0] + j)
            listTemp3 = [nowTime[2:-2] + '.' + str(x).zfill(3) for x in range(1, 25)]
            for k in listTemp3:
                ftpOb.ftp_upload(localBasePath + fangfa1h + k, ftpBasePath + fangfa1h + k)
            print(listTemp3)

    costTime = time.time() - timeStart
    print("运行时间：【%.4f】秒" % costTime)
