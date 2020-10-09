import os
import pandas as pd
import numpy as np
import time
import datetime


def get_now_time(nowBJTStr=datetime.datetime.today().strftime('%Y%m%d%H')):
    '''
    按当天日期和时间判断指导报起报时间
    获取当前时间，判断当前时间是否超过中午12点，如果超过则返回当天日期+'2000'，如果未超过则返回当天日期+'0800'
    :return: 起报时间
    '''
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    # 若当前时间在下午13时之前，则设置起报时间为0800，否则设置为2000
    if nowHour < 13:
        qiBaoShiJian = nowBJTStr[:-2] + '08'
    else:
        qiBaoShiJian = nowBJTStr[:-2] + '20'
    return qiBaoShiJian


def get_step_time(SlidingStep, qiBaoShiJian):
    listDaysTemp = []
    for day in range(2, SlidingStep + 2):
        startTime = datetime.datetime.strptime(qiBaoShiJian, '%Y%m%d%H')
        getTime = startTime - datetime.timedelta(days=day)
        getTimeStr = getTime.strftime('%Y%m%d%H')
        listDaysTemp.append(getTimeStr)
    return sorted(listDaysTemp)


def get_diff_dataframe(pathM, pathO, listTempM, listTempO, eStep, nowTime, jStep):
    '''
    输出偏差df，输出列以滑动步长为准
    :param pathM: 模式基本路径
    :param pathO: 实况基本路径
    :param listOfData: 滑动步长范围内的资料名称列表
    :param baseDf: 打底DF
    :return: 返回包含滑动步长范围内的实况与预报偏差
    '''
    omiga = 0.05
    path1 = '{}{}\\{}\\TMP_{}'.format(pathM, listTempM[0][:4], listTempM[0][:8], listTempM[0])
    path2 = '{}{}\\{}\\TMP_{}.txt'.format(pathO, listTempO[0][:4], listTempO[0][:-2], listTempO[0])
    arM1 = np.loadtxt(path1)
    arO1 = np.loadtxt(path2)
    arDiff = arM1 - arO1
    B1 = omiga * arDiff

    for i in range(1, eStep):
        path1 = '{}{}\\{}\\TMP_{}'.format(pathM, listTempM[i][:4], listTempM[i][:8], listTempM[i])
        path2 = '{}{}\\{}\\TMP_{}.txt'.format(pathO, listTempO[i][:4], listTempO[i][:-2], listTempO[i])
        arM = np.loadtxt(path1)
        arO = np.loadtxt(path2)
        bi = arM - arO
        Bt = (1 - omiga) * B1 + omiga * bi
        B1 = Bt
        print('*' * 50)
    print(Bt)


if __name__ == '__main__':
    timeStart = time.time()
    pathM = 'F:\\work\\2020Correct\\data\\TM_md_3h_Grid\\'
    pathO = 'F:\\work\\2020Correct\\data\\TEM_ob_1h_CLDAS_GRID\\'
    # listStep = ['003', '006', '009', '012', '015', '018', '021', '024']
    listStep = ['003']  # 预报时效
    # slidingStep = [3, 5, 7, 10, 15, 20]
    slidingStep = [60]
    for eStep in slidingStep:
        nowTime = get_now_time()
        print(nowTime)
        listFile = get_step_time(eStep, nowTime)
        ######################获取不同起报时次下不同预报时间的文件名
        #########################################################################
        for j in listStep:
            listTempO = []
            listTempM = []
            for i in listFile:
                listTempM.append(i + '.' + j)  ######获取相应列表的模式资料名
                timeTemp = datetime.datetime.strptime(i, '%Y%m%d%H') + datetime.timedelta(hours=int(j))
                timeTempStr = timeTemp.strftime('%Y%m%d%H')
                listTempO.append(timeTempStr)  ######获取相应列表的实况资料名
            #########################################################################
            listTempO = sorted(listTempO)
            listTempM = sorted(listTempM)

            aa = get_diff_dataframe(pathM, pathO, listTempM, listTempO, eStep, nowTime, j)
            # print(aa)

    timeEnd = time.time() - timeStart
    print('【共耗时%.4f秒】' % timeEnd)
