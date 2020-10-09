import pandas as pd
import numpy as np
import datetime
import os


def get_time(path1,dfSt):
    '''
    分08和20时，获取过去24h最高最低气温，并通过站号、最高、最低输出到日文件中
    '''
    nowBJT = datetime.datetime.today()  # 获取当前时间（北京时）
    nowBJTStr = nowBJT.strftime('%Y%m%d%H')  # 时间格式转化为字符串格式
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    # 下段是获取时间字符串，判断当前时间是几点，白天获取前一日08至当日08资料，20点亦然
    if nowHour >= 8 and nowHour < 20: # 当日8点后20点前
        timeTemp = nowBJTStr[:-2] + '00' # 将时间归位至当日00时（UTC），对应当日BJT08时，下面20时同理
        # 下段时换算日期为前一天，即存储文件名为前一天日期加‘08’字符串，意为前一天08点到当日08时的24h，这么做是为了与模式文件名同一
        startTime = datetime.datetime.strptime(nowBJTStr[:-2], '%Y%m%d')
        getTime = startTime - datetime.timedelta(days=1)
        getTimeStr = getTime.strftime('%Y%m%d')
        saveName = getTimeStr + '08'
    elif nowHour >= 20 or nowHour < 8:
        timeTemp = nowBJTStr[:-2] + '12'
        startTime = datetime.datetime.strptime(nowBJTStr[:-2], '%Y%m%d')
        getTime = startTime - datetime.timedelta(days=1)
        getTimeStr = getTime.strftime('%Y%m%d')
        saveName = getTimeStr + '20'

    for i in range(24):
        # 用上面获取的归位时间，逐小时向前推24个时次，获取前24h各站气温，并拼接为一个df
        startTimeC = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
        getTimeC = startTimeC - datetime.timedelta(hours=i)
        getTimeStrC = getTimeC.strftime('%Y%m%d%H')
        dfO = pd.read_csv(path1 + getTimeStrC + '.txt', sep=' ', engine='python', header=1).set_index('Station_Id_C')# 读取各时次的逐小时文件
        dfO[dfO['TEM'] > 100] = np.nan # 过滤较大值
        dfO = dfO['TEM']
        dfMandO = pd.concat([dfSt, dfO], axis=1) # 将24个文件拼接在一起
        dfSt = dfMandO
    #dfSt.to_csv('E:\\workspace\\tiaoshi\\data\\' + saveName + '.txt', float_format='%.2f')
    # 求最大最小值
    dfSt['TMAX'] = dfMandO.max(axis=1)
    dfSt['TMIN'] = dfMandO.min(axis=1)

    dfTMAXFinal = dfSt[['TMAX']]
    dfTMINFinal = dfSt[['TMIN']]
    # 将结果输出为存储时间为名的txt中，第一列为站号，第二列为最高温，第三列为最低气温
    dfTMAXFinal.to_csv('E:\\work\\2020Correct\\data\\TM_ob_24h\\' + saveName + '_TMAX.txt', float_format='%.2f')
    dfTMINFinal.to_csv('E:\\work\\2020Correct\\data\\TM_ob_24h\\' + saveName + '_TMIN.txt', float_format='%.2f')

def get_time_gb(path1,dfSt,nowBJTStr):
    # 此函数与上述基本一致，是回补数据时用的
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    print(nowHour)
    if nowHour >= 8 and nowHour < 20:
        timeTemp = nowBJTStr[:-2] + '00'
        startTime = datetime.datetime.strptime(nowBJTStr[:-2], '%Y%m%d')
        getTime = startTime - datetime.timedelta(days=1)
        getTimeStr = getTime.strftime('%Y%m%d')
        saveName = getTimeStr + '08'
    elif nowHour >= 20:
        timeTemp = nowBJTStr[:-2] + '12'
        startTime = datetime.datetime.strptime(nowBJTStr[:-2], '%Y%m%d')
        getTime = startTime - datetime.timedelta(days=1)
        getTimeStr = getTime.strftime('%Y%m%d')
        saveName = getTimeStr + '20'
    for i in range(24):
        startTime = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
        getTime1 = startTime - datetime.timedelta(hours=i)
        getTimeStr1 = getTime1.strftime('%Y%m%d%H')
        print(path1 + getTimeStr1 + '.txt')
        dfO = pd.read_csv(path1 + getTimeStr1 + '.txt', sep=' ', engine='python', header=1).set_index('Station_Id_C')
        dfO = dfO[~dfO.index.duplicated(keep='first')]
        dfO[dfO['TEM'] > 100] = np.nan
        dfO = dfO['TEM']
        dfMandO = pd.concat([dfSt, dfO], axis=1)
        print(dfMandO.shape)
        dfSt = dfMandO

    #dfSt.to_csv('E:\\workspace\\tiaoshi\\data\\' + saveName + '.txt', float_format='%.2f')
    dfSt['TMAX'] = dfMandO.max(axis=1)
    dfSt['TMIN'] = dfMandO.min(axis=1)

    dfTMAXFinal = dfSt[['TMAX']]
    dfTMINFinal = dfSt[['TMIN']]
    # 将结果输出为存储时间为名的txt中，第一列为站号，第二列为最高温，第三列为最低气温
    dfTMAXFinal.to_csv('F:\\work\\2020Correct\\data\\TM_ob_24h_648\\' + saveName + '_TMAX.txt', float_format='%.2f')
    dfTMINFinal.to_csv('F:\\work\\2020Correct\\data\\TM_ob_24h_648\\' + saveName + '_TMIN.txt', float_format='%.2f')

if __name__ == '__main__':
    stationInfoFilePath = 'E:\\work\\2020Correct\\data\\StationInfo_648.txt' # 站点信息文件，此文件中只有站点信息，为了DF索引而设
    stDf = pd.read_csv(stationInfoFilePath,encoding='utf-8',sep=',',engine='python').set_index('Station_Num') #读取站点信息文件
    stDf = stDf['Station_Name'] # 只留一列
    path1 = 'F:\\work\\2020Correct\\data\\TEM_ob_1h_648\\' #实况逐小时资料位置


    nowBJTStr = '2020092321' #回补资料日期
    #31为回补时次，15天为15 * 2
    for duringDays in range(10):
        nowBJT = datetime.datetime.strptime(nowBJTStr, '%Y%m%d%H')
        getTime = nowBJT + datetime.timedelta(hours=12 * duringDays)
        getTimeStr = getTime.strftime('%Y%m%d%H')
        print(getTimeStr)
        aa = get_time_gb(path1,stDf,getTimeStr)

    # print(stDf)