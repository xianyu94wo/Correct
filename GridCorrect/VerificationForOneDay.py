import pandas as pd
import numpy as np
import os
import datetime
import time
from collections import Counter

np.set_printoptions(suppress=True)


def get_now_time():
    nowBJT = datetime.datetime.today()
    nowBJTStr = nowBJT.strftime('%Y%m%d%H')
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    if nowHour >= 8 and nowHour < 20:
        nowTimeStr = nowBJTStr[:-2] + '08'
        timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
        previousTime = timeTemp - datetime.timedelta(days=1)
        previousTimeS = previousTime.strftime('%Y%m%d%H')
        return previousTimeS
    elif nowHour >= 20:
        nowTimeStr = nowBJTStr[:-2] + '20'
        timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
        previousTime = timeTemp - datetime.timedelta(days=1)
        previousTimeS = previousTime.strftime('%Y%m%d%H')
        return previousTimeS


def get_correct_verification(pathO, pathM, pathZ, element, nowTime):
    '''
    用预报结果和实况计算各站多日平均绝对误差和每日全站平均绝对误差
    :param pathO: 实况资料基本路径
    :param pathM: 预报结果基本路径
    :param element: 检验要素
    :param listOfForcastDate: get_file_list获取的所需检验文件名列表
    :param stDf: 打底DF
    :return:各站多日平均绝对误差和每日全站平均绝对误差
    '''
    # print(listOfForcastDate)
    listTemp1, listTemp2 = [], []

    pathOb = pathO + nowTime + '_' + element + '.txt'
    pathZd = pathZ + nowTime + '_' + element + '.txt'
    pathFc = pathM + element + '\\' + nowTime[2:] + '.024'

    arFc = np.loadtxt(pathFc, skiprows=3)
    arOb = np.loadtxt(pathOb)
    arZd = np.loadtxt(pathZd)
    diffAryFcAbs = abs(arFc - arOb)
    diffAryZdAbs = abs(arZd - arOb)
    FcAbsTemp = diffAryFcAbs.reshape(44114)
    ZdAbsTemp = diffAryZdAbs.reshape(44114)

    ZdNum, FcNum = 0, 0
    for i in FcAbsTemp:
        if i <= 2:
            FcNum += 1
    print('客观预报准确率为{:.3f}'.format(FcNum / 44114))
    listTemp2.append(FcNum / 44114)
    for j in ZdAbsTemp:
        if j <= 2:
            ZdNum += 1
    print('指导预报准确率为{:.3f}'.format(ZdNum / 44114))
    listTemp2.append(ZdNum / 44114)

    diffAryZdAbs[diffAryZdAbs == 0] = np.nan
    skillPoint = (diffAryZdAbs - diffAryFcAbs) / diffAryZdAbs
    diffAryFcAllPointAVE = np.nanmean(diffAryFcAbs)
    diffAryZdAllPointAVE = np.nanmean(diffAryZdAbs)
    skillAllPointAVE = (diffAryZdAllPointAVE - diffAryFcAllPointAVE) / diffAryZdAllPointAVE
    listTemp1.append(skillAllPointAVE)
    return diffAryFcAbs, diffAryZdAbs, skillPoint, listTemp1, listTemp2


if __name__ == '__main__':
    timeStart = time.time()
    element = ['TMAX', 'TMIN']  # ,'TMIN'
    pathO = 'F:\\work\\2020Correct\\data\\TM_ob_24h_Grid\\'
    pathM = 'F:\\work\\2020Correct\\data\\TM_Result_Grid_20\\'
    pathS = 'F:\\work\\2020Correct\\data\\verificationResultG_20\\'
    pathZ = 'F:\\work\\2020Correct\\data\\TM_md_24h_Grid\\'
    nowTime = get_now_time()
    print(nowTime)
    ###############################################################
    for eEle in element:
        print(eEle)
        aa = get_correct_verification(pathO, pathM, pathZ, eEle, nowTime)
        diffFceDayforePoint, diffZdeDayforePoint, skilleDayforePoint, skilleDayforePointAVE, Rate = aa

        np.savetxt(pathS + 'diffFceDayforePoint_' + nowTime + eEle + '.txt', diffFceDayforePoint, fmt='%.4f')
        np.savetxt(pathS + 'diffZdeDayforePoint_' + nowTime + eEle + '.txt', diffZdeDayforePoint, fmt='%.4f')
        np.savetxt(pathS + 'skilleDayforePoint_' + nowTime + eEle + '.txt', skilleDayforePoint, fmt='%.4f')
        np.savetxt(pathS + 'skilleDayforePointAVE_' + nowTime + eEle + '.txt', skilleDayforePointAVE, fmt='%.4f')
        # with open(pathS + 'precision_rate' + nowTime + eEle + '.txt','w') as f1:
        #     f1.writelines(str(Rate))
        np.savetxt(pathS + 'precision_rate' + nowTime + eEle + '.txt', Rate, fmt='%.4f')
    timeEnd = time.time()
    timeCost = timeEnd - timeStart
    print(timeCost)
    #########################################################
    print('DONE')
