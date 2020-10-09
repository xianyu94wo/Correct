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
    return sorted(listTimeTemp)


def get_correct_verification(pathO, pathM, pathZ, element, listOfForcastDate):
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
    print(listOfForcastDate)
    arZero = np.zeros((161, 274), dtype=float)
    arOne = np.ones((161, 274), dtype=float)
    arBase0 = np.array([arZero, arOne])
    arBase1 = np.array([arZero, arOne])
    arBase2 = np.array([arZero, arOne])
    arBase3 = np.array([arZero, arOne])
    arBase4 = np.array([arZero, arOne])
    listSkilleDayforALL = []
    listRate = []
    for i in listOfForcastDate:
        pathOb = pathO + i + '_' + element + '.txt'
        pathZd = pathZ + i + '_' + element + '.txt'
        pathFc = pathM + element + '\\' + i[2:] + '.024'

        # arFc = np.loadtxt(pathFc, skiprows=3)
        if pathM == pathM3 or pathM == pathM4:
            arFc = np.loadtxt(pathFc)
        else:
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
        # print('客观预报准确率为{:.3f}'.format(FcNum / 44114))
        listRate.append(FcNum / 44114)
        for j in ZdAbsTemp:
            if j <= 2:
                ZdNum += 1
        # print('指导预报准确率为{:.3f}'.format(ZdNum / 44114))
        listRate.append(ZdNum / 44114)

        diffAryFc = arFc - arOb
        diffAryZd = arZd - arOb
        diffAryZdAbs[diffAryZdAbs == 0] = np.nan

        diffAryFcAllPointAVE = np.nanmean(diffAryFcAbs)
        diffAryZdAllPointAVE = np.nanmean(diffAryZdAbs)
        skillAllPointAVE = (diffAryZdAllPointAVE - diffAryFcAllPointAVE) / diffAryZdAllPointAVE
        listSkilleDayforALL.append(skillAllPointAVE)

        skillPoint = (diffAryZdAbs - diffAryFcAbs) / diffAryZdAbs
        SPAVE = np.nanmean(skillPoint)

        skillPointAry = np.append(arBase0, skillPoint)
        dim0 = arBase0.shape
        dataCombSkill = skillPointAry.reshape(dim0[0] + 1, dim0[1], dim0[2])
        arBase0 = dataCombSkill.copy()

        FcdiffAryAbs = np.append(arBase1, diffAryFcAbs)
        dim1 = arBase1.shape
        dataCombFcAbs = FcdiffAryAbs.reshape(dim1[0] + 1, dim1[1], dim1[2])
        arBase1 = dataCombFcAbs.copy()

        ZddiffAryAbs = np.append(arBase2, diffAryZdAbs)
        dim2 = arBase2.shape
        dataCombZdAbs = ZddiffAryAbs.reshape(dim2[0] + 1, dim2[1], dim2[2])
        arBase2 = dataCombZdAbs.copy()

        FcdiffAry = np.append(arBase3, diffAryFc)
        dim3 = arBase3.shape
        dataCombFc = FcdiffAry.reshape(dim3[0] + 1, dim3[1], dim3[2])
        arBase3 = dataCombFc.copy()

        ZddiffAry = np.append(arBase4, diffAryZd)
        dim4 = arBase4.shape
        dataCombZd = ZddiffAry.reshape(dim4[0] + 1, dim4[1], dim4[2])
        arBase4 = dataCombZd.copy()

    dataCombSkill = np.delete(dataCombSkill, [0, 1], axis=0)
    dataCombFcAbs = np.delete(dataCombFcAbs, [0, 1], axis=0)
    dataCombZdAbs = np.delete(dataCombZdAbs, [0, 1], axis=0)
    dataCombFc = np.delete(dataCombFc, [0, 1], axis=0)
    dataCombZd = np.delete(dataCombZd, [0, 1], axis=0)
    skilleDayforePoint = np.nanmean(dataCombSkill, axis=0)
    diffFceDayforePointAbs = np.nanmean(dataCombFcAbs, axis=0)
    diffZdeDayforePointAbs = np.nanmean(dataCombZdAbs, axis=0)
    diffFceDayforePoint = np.nanmean(dataCombFc, axis=0)
    diffZdeDayforePoint = np.nanmean(dataCombZd, axis=0)
    listRate = np.array(listRate)
    listRate = listRate.reshape(len(listOfForcastDate), 2)
    dfRate = pd.DataFrame(listRate, index=listOfForcastDate, columns=['FC', 'ZD'])

    listSkilleDayforALL = np.array(listSkilleDayforALL)
    dfSkilleDayforALL = pd.DataFrame(listSkilleDayforALL, index=listOfForcastDate, columns=['Skill'])
    return skilleDayforePoint, diffFceDayforePointAbs, diffZdeDayforePointAbs, diffFceDayforePoint, diffZdeDayforePoint, dfSkilleDayforALL, dfRate


if __name__ == '__main__':
    # '2020081708_TMAX.txt'
    # eEle = 'TMAX'
    # qiBaoShiJian = '08'
    # qiBaoShiJian = ['08', '20']  # ,'20'
    # element = ['TMAX', 'TMIN']  # ,'TMIN'
    element = ['TMAX', 'TMIN']  # ,'TMIN'
    # pathO = 'E:\\work\\2020Correct\\data\\testO\\'
    # pathM = 'E:\\work\\2020Correct\\data\\testM\\'
    # pathS = 'E:\\work\\2020Correct\\data\\testS\\'
    pathO = 'F:\\work\\2020Correct\\data\\TM_ob_24h_Grid\\'
    pathM1 = 'F:\\work\\2020Correct\\data\\TM_Result_Grid_20\\'
    pathM2 = 'F:\\work\\2020Correct\\data\\TM_Result_DA\\'
    pathM3 = 'F:\\work\\2020Correct\\data\\TM_Result_Combine\\'
    pathM4 = 'F:\\work\\2020Correct\\data\\TM_Result_Combine_2\\'
    pathM5 = 'F:\\work\\2020Correct\\data\\TM_Result_Combine_3\\'
    pathM6 = 'F:\\work\\2020Correct\\data\\TM_Result_Combine_3m\\'
    # pathM = 'F:\\work\\2020Correct\\data\\TM_Result_648_Grid\\'
    pathS = 'F:\\work\\2020Correct\\data\\verificationResultALL\\'
    pathZ = 'F:\\work\\2020Correct\\data\\TM_md_24h_Grid\\'
    duringDay = 169
    # listTime = get_now_time(duringDay,'2020081509')
    listTime = get_now_time(duringDay)
    listPath = [pathM1, pathM2, pathM3, pathM4, pathM5, pathM6]
    listMName = ['MB', 'DA', 'CB1', 'CB2', 'CB3', 'CB4']

    ###############################################################
    for eEle in element:

        for i, ePath in enumerate(listPath):
            print(eEle, listMName[i])
            aa = get_correct_verification(pathO, ePath, pathZ, eEle, listTime)
            skilleDayforePoint, diffFceDayforePointAbs, diffZdeDayforePointAbs, diffFceDayforePoint, diffZdeDayforePoint, dfSkilleDayforALL, dfRate = aa
            np.savetxt('{}skilleDayforePoint_{}_{}days_{}_{}.txt'.format(pathS, listTime[-1], duringDay, eEle, listMName[i]),
                       skilleDayforePoint, fmt='%.4f')
            np.savetxt('{}diffFceDayforePointABS_{}_{}days_{}_{}.txt'.format(pathS, listTime[-1], duringDay, eEle, listMName[i]),
                       diffFceDayforePoint, fmt='%.4f')
            np.savetxt('{}diffZdeDayforePointABS_{}_{}days_{}_{}.txt'.format(pathS, listTime[-1], duringDay, eEle, listMName[i]),
                       diffZdeDayforePoint, fmt='%.4f')
            np.savetxt('{}diffFceDayforePoint_{}_{}days_{}_{}.txt'.format(pathS, listTime[-1], duringDay, eEle, listMName[i]),
                       diffFceDayforePoint, fmt='%.4f')
            np.savetxt('{}diffZdeDayforePoint_{}_{}days_{}_{}.txt'.format(pathS, listTime[-1], duringDay, eEle, listMName[i]),
                       diffZdeDayforePoint, fmt='%.4f')
            dfSkilleDayforALL.to_csv('{}listSkilleDayforALL_{}_{}days_{}_{}.txt'.format(pathS, listTime[-1], duringDay, eEle, listMName[i]),
                                     float_format='%.4f')
            dfRate.to_csv('{}listRateForALL_{}_{}days_{}_{}.txt'.format(pathS, listTime[-1], duringDay, eEle, listMName[i]),
                          float_format='%.4f')

    #########################################################
    print('DONE')
