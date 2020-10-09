import os
import pandas as pd
import numpy as np
import time
import datetime
np.set_printoptions(suppress=True)


def get_now_time():
    '''
    按当天日期和时间判断指导报起报时间
    获取当前时间，判断当前时间是否超过中午12点，如果超过则返回当天日期+'2000'，如果未超过则返回当天日期+'0800'
    :return: 起报时间
    '''
    nowBJT = datetime.datetime.today()  # 获取当前时间（北京时）
    nowBJTStr = nowBJT.strftime('%Y%m%d%H')  # 时间格式转化为字符串格式
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    # 若当前时间在下午13时之前，则设置起报时间为0800，否则设置为2000
    if nowHour < 13:
        qiBaoShiJian = nowBJTStr[:-2] + '0800'
    else:
        qiBaoShiJian = nowBJTStr[:-2] + '2000'
    return qiBaoShiJian

def get_step_time(qiBaoShiJian, SlidingStep):
    listDaysTemp = []
    for day in range(2,SlidingStep + 2):
        startTime = datetime.datetime.strptime(qiBaoShiJian[:-2], '%Y%m%d%H')
        getTime = startTime - datetime.timedelta(days=day)
        getTimeStr = getTime.strftime('%Y%m%d%H')
        listDaysTemp.append(getTimeStr)
    return sorted(listDaysTemp)

def get_time_ob(duringDays):
    '''
    按当天日期和时间判断指导报起报时间
    获取当前时间，判断当前时间是否超过中午12点，如果超过则返回当天日期+'2000'，如果未超过则返回当天日期+'0800'
    :return: 起报时间
    '''

    startTimeStr = '2020080107'
    startTime = datetime.datetime.strptime(startTimeStr, '%Y%m%d%H')
    getTime = startTime + datetime.timedelta(hours=12 * duringDays)
    getTimeStr = getTime.strftime('%Y%m%d%H')  # 时间格式转化为字符串格式
    nowHour = int(getTimeStr[-2:])  # 字符串中获取小时并转为整数
    # 若当前时间在下午13时之前，则设置起报时间为0800，否则设置为2000
    if nowHour < 13:
        qiBaoShiJian = getTimeStr[:-2] + '0800'
    else:
        qiBaoShiJian = getTimeStr[:-2] + '2000'
    return qiBaoShiJian

def get_diff_dataframe(pathM, pathO, listOfData, baseDf, element):
    '''
    输出偏差df，输出列以滑动步长为准
    :param pathM: 模式基本路径
    :param pathO: 实况基本路径
    :param listOfData: 滑动步长范围内的资料名称列表
    :param baseDf: 打底DF
    :return: 返回包含滑动步长范围内的实况与预报偏差
    '''
    for i in listOfData:
        # 分别读取列表listOfData内的模式和实况资料
        path1 = pathM + i + '_' + element + '.txt'
        path2 = pathO + i + '_' + element + '.txt'
        # 之前的模式格点对应站点资料输出后无index和col，这里用np读取为array
        ar1 = np.loadtxt(path1)
        # 用pd读取实况资料
        dfO = pd.read_csv(path2, encoding='utf-8', engine='python',index_col=0)
        # 添加实况资料到模式资料的df中
        dfO[element + 'm'] = ar1
        # 求偏差，并将偏差列名设置为列表index对应的名称，偏差用O-M
        dfO[element + 'diff' + str(listOfData.index(i) + 1)] = dfO[element] - dfO[element + 'm']
        # 删除不需要的列
        dfO = dfO.drop([element + 'm',element], axis=1)
        # 合并各偏差
        baseDf = pd.concat([baseDf,dfO],axis=1)
    diffDf = baseDf.drop(['Station_Name'], axis=1)
    return diffDf

def calculate_median(diffDf,baseDf, element):
    '''
    求中位数和D中位数
    :param diffDf: diffDf
    :param baseDf: baseDf
    :return: 返回diffDf（因为原来diff可能因为全局变量或者局部变量被更改）、中位数array、Darray
    '''
    diffDfT = diffDf.T
    medianArray = diffDfT.median()
    for i in range(1,SlidingStep + 1):
        diffDf['DMedian' + str(i) ] = abs(diffDf[element + 'diff' + str(i)] - medianArray)
        DMedianDf = pd.concat([baseDf,diffDf['DMedian' + str(i)]],axis=1)
        diffDf = diffDf.drop(['DMedian' + str(i)],axis = 1)
        baseDf = DMedianDf
    DMedianDf = DMedianDf.drop(['Station_Name'], axis = 1)
    DMedianDfT = DMedianDf.T
    DMedianArray = DMedianDfT.median()
    # diffDf['medianArray'] = medianArray
    # diffDf['DMedianArray'] = DMedianArray
    return diffDf,medianArray,DMedianArray

def calculate_omiga(diffDf, medianArray, DMedianArray, element):
    '''
    计算Ω
    :param diffDf: diffDf
    :param medianArray: 中位数array
    :param DMedianArray: Darray
    :return: 返回diffDf（因为原来diff可能因为全局变量或者局部变量被更改）
    '''
    for i in range(1,SlidingStep + 1):
        diffDf['omiga' + str(i)] = (diffDf[element + 'diff' + str(i)] - medianArray) / (7.5 * DMedianArray)
        diffDf.loc[diffDf['omiga' + str(i)] > 1, 'omiga' + str(i)] = 1
        diffDf.loc[diffDf['omiga' + str(i)] < -1, 'omiga' + str(i)] = -1
    return diffDf

def calculate_adjustDeno(diffDf, baseDf):
    '''
    计算adjust第二项的分母
    :param diffDf: diffDf
    :param baseDf: baseDf
    :return: 返回西格玛后的分母
    '''
    for i in range(1,SlidingStep + 1):
        diffDf['adjustDeno' + str(i)]  =  (1 - diffDf['omiga' + str(i)]**2)**2
        adjustDenoDf = pd.concat([baseDf, diffDf['adjustDeno' + str(i)]], axis=1)
        diffDf = diffDf.drop(['adjustDeno' + str(i)], axis=1)
        baseDf = adjustDenoDf
    adjustDenoDf = adjustDenoDf.drop(['Station_Name'], axis=1)
    adjustDenoResult = adjustDenoDf.sum(axis=1)
    #print(adjustDenoResult)
    return adjustDenoResult

def calculate_adjustNumer(diffDf, baseDf, element):
    '''
    计算adjust第二项的分子
    :param diffDf: diffDf
    :param baseDf: baseDf
    :return: 返回西格玛后的分子
    '''
    for i in range(1,SlidingStep + 1):
        diffDf['adjustNumer' + str(i)] = (diffDf[element + 'diff' + str(i)] - medianArray) * (1 - diffDf['omiga' + str(i)]**2)**2
        adjustNumerDf = pd.concat([baseDf, diffDf['adjustNumer' + str(i)]], axis=1)
        diffDf = diffDf.drop(['adjustNumer' + str(i)], axis=1)
        baseDf = adjustNumerDf
    adjustNumerDf = adjustNumerDf.drop(['Station_Name'], axis=1)
    adjustNumerResult = adjustNumerDf.sum(axis=1)
    #print(adjustNumerResult)
    return adjustNumerResult




if __name__ == '__main__':
    pathM = 'E:\\work\\2020Correct\\data\\TM_md_24h\\'
    pathO = 'E:\\work\\2020Correct\\data\\TM_ob_24h\\'
    stationInfoFilePath = 'E:\\work\\2020Correct\\data\\StationInfo.txt' # 站点信息文件，此文件中只有站点信息，为了DF索引而设
    SlidingStep = 3
    element = ['TMIN','TMAX']
    #element = ['TMIN']

    baseDf = pd.read_csv(stationInfoFilePath,encoding='utf-8',sep=',',engine='python').set_index('Station_Num') #读取站点信息文件
    baseDf = baseDf['Station_Name']  # 只留一列
    for eEle in element:
        getTime = get_now_time()
        listOfData = get_step_time(getTime, SlidingStep)
        diffDf = get_diff_dataframe(pathM, pathO, listOfData, baseDf, eEle)
        diffDfBase = calculate_median(diffDf,baseDf, eEle)
        diffDf, medianArray, DMedianArray = diffDfBase[0], diffDfBase[1], diffDfBase[2]
        diffDf = calculate_omiga(diffDf, medianArray, DMedianArray, eEle)
        adjustDeno = calculate_adjustDeno(diffDf, baseDf)
        adjustNumer = calculate_adjustNumer(diffDf, baseDf, eEle)
        adjust = adjustNumer / adjustDeno
        adjustResult = medianArray + adjust
        print(adjustResult)


