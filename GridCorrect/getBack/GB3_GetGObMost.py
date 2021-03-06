import pandas as pd
import numpy as np
import datetime
import os
import time


def get_now_time_GB(nowBJTStr):
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    listTime = []
    if nowHour >= 8 and nowHour < 20:
        timeTemp = nowBJTStr[:-2] + '08'
        saveTimet = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
        saveTime = saveTimet - datetime.timedelta(days=1)
        saveTimeStr = saveTime.strftime('%Y%m%d%H')
        for eHour in range(24):
            getTime = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
            getTime = getTime - datetime.timedelta(hours=eHour)
            getTimeStr = getTime.strftime('%Y%m%d%H')
            listTime.append(getTimeStr)
    elif nowHour >= 20 or nowHour < 8:
        timeTemp = nowBJTStr[:-2] + '20'
        saveTimet = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
        saveTime = saveTimet - datetime.timedelta(days=1)
        saveTimeStr = saveTime.strftime('%Y%m%d%H')
        for eHour in range(24):
            getTime = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
            getTime = getTime - datetime.timedelta(hours=eHour)
            getTimeStr = getTime.strftime('%Y%m%d%H')
            listTime.append(getTimeStr)
    return saveTimeStr, listTime


def get_now_time():
    nowBJT = datetime.datetime.today()
    nowBJTStr = nowBJT.strftime('%Y%m%d%H')
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    listTime = []
    if nowHour >= 8 and nowHour < 20:
        timeTemp = nowBJTStr[:-2] + '08'
        saveTimet = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
        saveTime = saveTimet - datetime.timedelta(days=1)
        saveTimeStr = saveTime.strftime('%Y%m%d%H')
        for eHour in range(24):
            getTime = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
            getTime = getTime - datetime.timedelta(hours=eHour)
            getTimeStr = getTime.strftime('%Y%m%d%H')
            listTime.append(getTimeStr)
    elif nowHour >= 20:
        timeTemp = nowBJTStr[:-2] + '20'
        saveTimet = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
        saveTime = saveTimet - datetime.timedelta(days=1)
        saveTimeStr = saveTime.strftime('%Y%m%d%H')
        for eHour in range(24):
            getTime = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
            getTime = getTime - datetime.timedelta(hours=eHour)
            getTimeStr = getTime.strftime('%Y%m%d%H')
            listTime.append(getTimeStr)
    return saveTimeStr, listTime


def get_Tmost_array(listTime, pathG, arBase):
        for eTime in listTime:
            try:
                pathGfile = pathG + eTime[:4] + '\\' + eTime[:-2] + '\\'
                arTemp = np.loadtxt(pathGfile + 'TMP_' + eTime + '.txt')
                data1 = np.append(arBase, arTemp)
                dim1 = arBase.shape
                dataComb = data1.reshape(dim1[0] + 1, dim1[1], dim1[2])
                arBase = dataComb.copy()
            except OSError:
                continue
        dataComb = np.delete(dataComb, [0, 1], axis=0)
        listmax = []
        listmin = []
        if dataComb.shape[0] > 21:
            for n in range(dataComb.shape[1]):
                for m in range(dataComb.shape[2]):
                    aaa = np.max(dataComb[:, n, m])
                    bbb = np.min(dataComb[:, n, m])
                    listmax.append(aaa)
                    listmin.append(bbb)
            TmaxArray = np.array(listmax).reshape(dataComb.shape[1], dataComb.shape[2])
            TminArray = np.array(listmin).reshape(dataComb.shape[1], dataComb.shape[2])
            return TmaxArray, TminArray




if __name__ == '__main__':

    timeStr = '2020092511'
    pathG = 'F:\\work\\2020Correct\\data\\TEM_ob_1h_CLDAS_GRID\\'
    pathS = 'F:\\work\\2020Correct\\data\\TM_ob_24h_Grid\\'
    for days in range(10):
        timeStart = time.time()
        getTime1 = datetime.datetime.strptime(timeStr, '%Y%m%d%H')
        getTime1 = getTime1 + datetime.timedelta(hours=12 * days)
        getTimeStrF = getTime1.strftime('%Y%m%d%H')

        saveTime, listTime = get_now_time_GB(getTimeStrF)[0], get_now_time_GB(getTimeStrF)[1]
        print(saveTime)
        print(listTime)


        arZero = np.zeros((161, 274), dtype=float)
        arOne = np.ones((161, 274), dtype=float)
        arBase = np.array([arZero, arOne])
        finalData = get_Tmost_array(listTime, pathG, arBase)
        try:
            np.savetxt(pathS + saveTime + '_TMAX.txt', finalData[0], fmt='%.2f')
            np.savetxt(pathS + saveTime + '_TMIN.txt', finalData[1], fmt='%.2f')
            timeEnd = time.time() - timeStart
            print('【运行时间%.2f秒】'%timeEnd)
        except TypeError:
            print('【逐小时资料未到齐】')

