import pandas as pd
import numpy as np
import os
import datetime
import time
from collections import Counter

np.set_printoptions(suppress=True)


def get_now_time(duringDays, nowBJTStr=datetime.datetime.today().strftime('%Y%m%d%H')):
    # nowBJT = datetime.datetime.today()
    # nowBJTStr = nowBJT.strftime('%Y%m%d%H')
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    listTimeTemp = []
    for eDay in range(1, duringDays + 1):
        if nowHour >= 8 and nowHour < 20:
            nowTimeStr = nowBJTStr[:-2] + '08'
            timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
            previousTime = timeTemp - datetime.timedelta(days=eDay)
            previousTimeS = previousTime.strftime('%Y%m%d%H')
            listTimeTemp.append(previousTimeS)
        elif nowHour >= 20:
            nowTimeStr = nowBJTStr[:-2] + '20'
            timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
            previousTime = timeTemp - datetime.timedelta(days=eDay)
            previousTimeS = previousTime.strftime('%Y%m%d%H')
            listTimeTemp.append(previousTimeS)
    return sorted(listTimeTemp), nowTimeStr


def get_correct_verification(pathO, pathM, element, listOfForcastDate):
    '''
    用预报结果和实况计算各站多日平均绝对误差和每日全站平均绝对误差
    :param pathO: 实况资料基本路径
    :param pathM: 预报结果基本路径
    :param element: 检验要素
    :param listOfForcastDate: get_file_list获取的所需检验文件名列表
    :param stDf: 打底DF
    :return:各站多日平均绝对误差和每日全站平均绝对误差
    '''
    arZero = np.zeros((161, 274), dtype=float)
    arOne = np.ones((161, 274), dtype=float)
    arBase0 = np.array([arZero, arOne])
    listEeM = []
    for i in listOfForcastDate:
        pathOb = pathO + i + '_' + element + '.txt'
        pathFc = pathM + element + '\\' + i[2:] + '.024'
        arFc = np.loadtxt(pathFc, skiprows=3)
        arOb = np.loadtxt(pathOb)
        arOb[arOb == 0] = 0.01
        arEe = abs((arOb - arFc) / arOb)
        arEeM = np.nanmean(arEe.reshape(44114))
        listEeM.append(arEeM)
        eEAry = np.append(arBase0, arEe)
        dim0 = arBase0.shape
        dataeEAry = eEAry.reshape(dim0[0] + 1, dim0[1], dim0[2])
        arBase0 = dataeEAry.copy()
    arBase0 = np.delete(arBase0, [0, 1], axis=0)
    arEeAPSum = np.nansum(arBase0, axis=0)
    arEeMSum = np.nansum(listEeM)
    return arEeMSum, arEeAPSum


def get_omiga(listModel):
    listOmiga = []
    arTemp = np.array(listModel)
    arTempSum = np.nansum(arTemp, axis=0)
    for i in range(len(listModel)):
        omiga = (arTempSum - listModel[i]) / ((len(listModel) - 1) * arTempSum)
        listOmiga.append(omiga)
    return listOmiga


def correct(FCtime, listOmiga):
    global pathM1, pathM2, eEle, pathS
    pathM1today = pathM1 + eEle + '\\' + FCtime[2:] + '.024'
    pathM2today = pathM2 + eEle + '\\' + FCtime[2:] + '.024'
    ar1 = np.loadtxt(pathM1today, skiprows=3)
    ar2 = np.loadtxt(pathM2today, skiprows=3)
    arRes = ar1 * listOmiga[0] + ar2 * listOmiga[1]
    gridFileSaveName = FCtime[2:] + '.024'
    np.savetxt(pathS + eEle + '\\' + gridFileSaveName + '.temp', arRes, fmt='%.2f')
    with open(pathS + eEle + '\\' + gridFileSaveName + '.temp') as f1:
        tempStr = f1.readlines()
    with open(pathS + eEle + '\\' + gridFileSaveName, 'w') as f2:
        f2.write('diamond 4 CB3ysj_20%s_%s %s' % (gridFileSaveName[:-4], eEle, '\n'))
        f2.write('20%s %s %s %s 24 0 %s' % (
            gridFileSaveName[:-10], gridFileSaveName[2:4], gridFileSaveName[4:6], gridFileSaveName[6:8], '\n'))
        thirdLine = '0.05000 0.05000 89.3 102.95 31.4 39.4 274 161 10.000000 -40.000000 40.000000 5.000000 0.000000 '
        f2.write('%s %s' % (thirdLine, '\n'))

        f2.writelines(tempStr)
    os.remove(pathS + eEle + '\\' + gridFileSaveName + '.temp')

    return arRes


if __name__ == '__main__':
    element = ['TMAX', 'TMIN']  # ,'TMIN'
    listDuring = [1]
    pathO = 'F:\\work\\2020Correct\\data\\TM_ob_24h_Grid\\'
    pathM1 = 'F:\\work\\2020Correct\\data\\TM_Result_DA\\'
    pathM2 = 'F:\\work\\2020Correct\\data\\TM_Result_Grid_20\\'

    pathZ = 'F:\\work\\2020Correct\\data\\TM_md_24h_Grid\\'
    #duringDay = 20
    dataStart = '2020032209'
    duringDayS = 400
    for duringDay in listDuring:
        pathS = 'F:\\work\\2020Correct\\data\\TM_Result_Combine_3_'+str(duringDay) + '\\'
        for eDay in range(duringDayS):
            timeStart1 = time.time()
            getTime1 = datetime.datetime.strptime(dataStart, '%Y%m%d%H')
            getTime1 = getTime1 + datetime.timedelta(hours=12 * eDay)
            getTimeStrF = getTime1.strftime('%Y%m%d%H')
            listTime = get_now_time(duringDay, getTimeStrF)
            print(listTime)
            ###############################################################
            for eEle in element:
                aa = get_correct_verification(pathO, pathM1, eEle, listTime[0])
                bb = get_correct_verification(pathO, pathM2, eEle, listTime[0])
                # listEeMSum, listEeAPSum = [aa[0], bb[0], cc[0]], [aa[1], bb[1], cc[1]]
                listEeMSum, listEeAPSum = [aa[0], bb[0]], [aa[1], bb[1]]
                listOmiga = get_omiga(listEeAPSum)
                final = correct(listTime[1], listOmiga)

    print('DONE')
