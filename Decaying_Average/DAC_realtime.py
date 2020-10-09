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


def get_diff_dataframe(pathM1, pathO1, eStep, omiga):
    '''
    输出偏差df，输出列以滑动步长为准
    :param pathM: 模式基本路径
    :param pathO: 实况基本路径
    :param listOfData: 滑动步长范围内的资料名称列表
    :param baseDf: 打底DF
    :return: 返回包含滑动步长范围内的实况与预报偏差
    '''
    arM1 = np.loadtxt(pathM1[0])
    arO1 = np.loadtxt(pathO1[0])
    arDiff = arM1 - arO1
    B1 = omiga * arDiff
    for i in range(1, eStep):
        try:
            arMi = np.loadtxt(pathM1[i])
            arOi = np.loadtxt(pathO1[i])
            bi = arMi - arOi
            Bi = (1 - omiga) * B1 + omiga * bi
            B1 = Bi
        except Exception as e:
            continue
    return B1


def correct(pathF, bias, pathS, eEle):
    arZD = np.loadtxt(pathF)
    arFC = arZD - bias
    np.savetxt(pathS + '24hTemp2.txt', arFC, format('%.2f'))

    with open(pathS + '24hTemp2.txt') as f1:
        tempStr = f1.readlines()
    with open('{}\\{}\\{}.024'.format(pathS, eEle,nowTime[2:]), 'w') as f2:
        f2.write('diamond 4 DAysj_%s_%s\n' % (nowTime, eEle))
        f2.write('%s %s %s %s 24 0 \n' % (nowTime[:4], nowTime[4:6], nowTime[6:8], nowTime[-2:]))
        thirdLine = '0.05000 0.05000 89.3 102.95 31.4 39.4 274 161 10.000000 -40.000000 40.000000 2.000000 0.000000 '
        f2.write('%s %s' % (thirdLine, '\n'))
        f2.writelines(tempStr)
    os.remove(pathS + '24hTemp2.txt')

def mkdir_dir_and_ormiga():
    path1 = 'F:\\work\\2020Correct\\data\\DA\\'
    listOmiga = ['{:.3f}'.format(0.005 * x) for x in range(75, 100)]
    list2 = [path1 + x for x in listOmiga]
    # for i in list2:
    #     os.makedirs(i)
    return listOmiga

if __name__ == '__main__':
    pathM = 'F:\\work\\2020Correct\\data\\TM_md_24h_Grid\\'
    pathO = 'F:\\work\\2020Correct\\data\\TM_ob_24h_Grid\\'
    pathS = 'F:\\work\\2020Correct\\data\\TM_Result_DA\\'
    listEle = ['TMIN', 'TMAX']  #
    #omiga = 0.05
    slidingStep = [60]

    dataStart = '2020032006'
    duringDay = 350


    ###################################################################
    for eStep in slidingStep:
        nowTime = get_now_time()
        listFile = get_step_time(eStep, nowTime)
        # ######################获取不同起报时次下不同预报时间的文件名
        # #########################################################################
        for eEle in listEle:
            timeStart = time.time()
            if eEle == 'TMAX':
                omiga = 0.085
            if eEle == 'TMIN':
                omiga = 0.115
            print('【正在处理以{}为权重的{}起报的{}】'.format(omiga, nowTime, eEle))
            listTemp = sorted(list(map(lambda x: x + '_' + eEle + '.txt', listFile)))
            listPathM, listPathO = [pathM + i for i in listTemp], [pathO + i for i in listTemp]
            bias = get_diff_dataframe(listPathM, listPathO, eStep, omiga)
            pathF = pathM + nowTime + '_' + eEle + '.txt'
            result = correct(pathF, bias, pathS, eEle)
            timeEnd = time.time() - timeStart
            print('【处理完成，共耗时%.4f秒】' % timeEnd)
