import pandas as pd
import numpy as np
import datetime
import os
import time
import sys

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
sys.path.append('E:\\workspace\\work\\Correct\\CorrectClass\\')
from get_now_time import GetNowTime
from FNP import FindNearestPoint
'''
此代码旨在用逐小时实况选取最高最低实况
GGOB是GetGribObversationMost的缩写
'''


def get_listTime():
    global previousTimeS, previousTimeSUTC
    listTimeBJT, listTimeUTC = [], []
    for eHour in range(24):
        getTimeBJT = datetime.datetime.strptime(previousTimeS, '%Y%m%d%H')
        getTimeUTC = datetime.datetime.strptime(previousTimeSUTC, '%Y%m%d%H')
        getTimeBJT = getTimeBJT - datetime.timedelta(hours=eHour)
        getTimeUTC = getTimeUTC - datetime.timedelta(hours=eHour)
        getTimeBJTStr = getTimeBJT.strftime('%Y%m%d%H')
        getTimeUTCStr = getTimeUTC.strftime('%Y%m%d%H')
        listTimeBJT.append(getTimeBJTStr)
        listTimeUTC.append(getTimeUTCStr)
    return listTimeBJT, listTimeUTC


def get_Tmost_Grid(listTime, pathG):
    print('  【开始格点实况最高最低气温筛选】')
    arZero = np.zeros((161, 274), dtype=float)
    arOne = np.ones((161, 274), dtype=float)
    arBase = np.array([arZero, arOne])
    for eTime in listTime:
        pathGfile = pathG + eTime[:4] + '\\' + eTime[:-2] + '\\'
        arTemp = np.loadtxt(pathGfile + 'TMP_' + eTime + '.txt')
        #print('【已载入%s时刻格点实况】' % eTime)
        data1 = np.append(arBase, arTemp)
        dim1 = arBase.shape
        dataComb = data1.reshape(dim1[0] + 1, dim1[1], dim1[2])
        arBase = dataComb.copy()
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
        print('  【格点实况最高/最低气温筛选执行完成】')
        return TmaxArray, TminArray


def get_Tmost_Station(listTimeUTC, pathS):
    print('  【开始站点实况最高最低气温筛选】')
    stationInfoFilePath = 'E:\\work\\2020Correct\\data\\StationInfo_648.txt'  # 站点信息文件，此文件中只有站点信息，为了DF索引而设
    dfSt = pd.read_csv(stationInfoFilePath, encoding='utf-8', sep=',', engine='python').set_index('Station_Num')  # 读取站点信息文件
    dfSt = dfSt['Station_Name']
    for i in listTimeUTC:
        #print('【已载入%s时刻格点实况】' % i)
        dfO = pd.read_csv(pathS + i + '.txt', sep=' ', engine='python', header=1).set_index('Station_Id_C')  # 读取各时次的逐小时文件
        dfO = dfO[~dfO.index.duplicated(keep='first')]
        dfO[dfO['TEM'] > 100] = np.nan  # 过滤较大值
        dfO = dfO['TEM']
        dfMandO = pd.concat([dfSt, dfO], axis=1)  # 将24个文件拼接在一起
        dfSt = dfMandO
    dfSt['TMAX'] = dfSt.max(axis=1)
    dfSt['TMIN'] = dfSt.min(axis=1)
    dfTMAXFinal = dfSt[['TMAX']]
    dfTMINFinal = dfSt[['TMIN']]
    print('  【站点实况最高/最低气温筛选执行完成】')
    return dfTMAXFinal,dfTMINFinal


if __name__ == '__main__':
    timeStart = time.time()
    print('【开始运行最高气温最低气温筛选】')
    #########路径及参数设置
    # 一些路径
    pathGrib1h = 'F:\\work\\2020Correct\\data\\TEM_ob_1h_CLDAS_GRID\\'
    pathStation1h = 'F:\\work\\2020Correct\\data\\TEM_ob_1h_648\\'
    pathGrib24h = 'F:\\work\\2020Correct\\data\\TM_ob_24h_Grid\\'
    pathStation24h = 'F:\\work\\2020Correct\\data\\TM_ob_24h_648\\'
    logPath = 'F:\\work\\2020Correct\\data\\log\\'
    # 获取时间参数
    getTimeOb = GetNowTime()
    #getTimeOb.print_all_attribute_of_object()  # 此对象所有属性的print
    nowTimeStr = getTimeOb.nowTimeStr
    nowTimeStrUTC = getTimeOb.nowTimeStrUTC
    previousTimeS = getTimeOb.previousTimeS
    previousTimeSUTC = getTimeOb.previousTimeSUTC
    listTimeBJT, listTimeUTC = get_listTime()
    ##########################筛选程序
    # 筛选格点最高最低实况
    try:
        finalGridData = get_Tmost_Grid(listTimeBJT, pathGrib1h)
        np.savetxt(pathGrib24h + previousTimeS + '_TMAX.txt', finalGridData[0], fmt='%.2f')
        np.savetxt(pathGrib24h + previousTimeS + '_TMIN.txt', finalGridData[1], fmt='%.2f')
    except Exception as e1:
        print('  【实况格点最值未能筛选，原因为:】')
        print(e1)
        with open(logPath + '实况格点最值获取报错_' + getTimeOb.nowBJTStr + '.log','w+') as logfo1:
            logfo1.writelines(str(e1))
    # 筛选站点最高最低实况
    try:
        finalStationData = get_Tmost_Station(listTimeUTC, pathStation1h)
        finalStationData[0].to_csv(pathStation24h + previousTimeS + '_TMAX.txt', float_format='%.2f')
        finalStationData[1].to_csv(pathStation24h + previousTimeS + '_TMIN.txt', float_format='%.2f')
    except Exception as e2:
        print('  【实况站点最值未能筛选，原因为:】')
        print(e2)
        with open(logPath + '实况站点最值获取报错_' + getTimeOb.nowBJTStr + '.log','w+') as logfo2:
            logfo2.writelines(str(e2))
    timeEnd = time.time() - timeStart
    print('【最高气温最低气温筛选运行结束，运行时间%.2f秒】' % timeEnd)


