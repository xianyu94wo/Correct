import xarray as xr
import numpy as np
import pandas as pd
import datetime
import time

np.set_printoptions(suppress=True)


def get_now_time(nowBJTStr=datetime.datetime.today().strftime('%Y%m%d%H')):
    '''
    按当天日期和时间判断指导报起报时间
    获取当前时间，判断当前时间是否超过中午12点，如果超过则返回当天日期+'2000'，如果未超过则返回当天日期+'0800'
    :return: 起报时间
    '''
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    # 若当前时间在下午13时之前，则设置起报时间为0800，否则设置为2000
    if nowHour < 13:
        qiBaoShiJian = nowBJTStr[:-2] + '0800'
        nowTimeStr = nowBJTStr[:-2] + '08'
        timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
        previousTime = timeTemp - datetime.timedelta(days=1)
        previousBeforeTime = timeTemp - datetime.timedelta(days=2)
        previousTimeS = previousTime.strftime('%Y%m%d%H')
        previousBeforeTimeS = previousBeforeTime.strftime('%Y%m%d%H')
        return qiBaoShiJian, nowTimeStr, previousTimeS, previousBeforeTimeS
    else:
        qiBaoShiJian = nowBJTStr[:-2] + '2000'
        nowTimeStr = nowBJTStr[:-2] + '20'
        timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
        previousTime = timeTemp - datetime.timedelta(days=1)
        previousBeforeTime = timeTemp - datetime.timedelta(days=2)
        previousTimeS = previousTime.strftime('%Y%m%d%H')
        previousBeforeTimeS = previousBeforeTime.strftime('%Y%m%d%H')
        return qiBaoShiJian, nowTimeStr, previousTimeS, previousBeforeTimeS


def combineData():
    global arDataofDA, arDataofMB, arDataofZD, eEle
    arDataofDA = np.loadtxt(pathMDA + eEle + '\\' + timeList[1][2:] + '.024', skiprows=3).reshape(44114)
    arDataofMB = np.loadtxt(pahtMMB + eEle + '\\' + timeList[1][2:] + '.024', skiprows=3).reshape(44114)

    arDataCombineR = np.array([arDataofMB, arDataofDA])
    return arDataCombineR


def combineVR():
    global eEle, listMode, pathVeriRes, str1, timeList
    listFileName = []
    for eMode in listMode:
        fileName = '{}{}_10days_{}_{}.txt'.format(str1, timeList[-1], eEle, eMode)
        listFileName.append(fileName)
    listFileName = sorted(listFileName)
    arVRofDA, arVRofMB = np.loadtxt(pathVeriRes + listFileName[0]), np.loadtxt(pathVeriRes + listFileName[1])
    arVRCombineR = np.array([arVRofMB, arVRofDA])
    return arVRCombineR


if __name__ == '__main__':
    pathVeriRes = 'F:\\work\\2020Correct\\data\\verificationResultCheck\\'
    #pathMZD = 'F:\\work\\2020Correct\\data\\TM_md_24h_Grid\\'
    pathMDA = 'F:\\work\\2020Correct\\data\\TM_Result_DA\\'
    pahtMMB = 'F:\\work\\2020Correct\\data\\TM_Result_Grid_20\\'
    pathRes = 'F:\\work\\2020Correct\\data\\TM_Result_Combine_2\\'
    listElement = ['TMAX', 'TMIN']
    listMode = ['DA', 'MB']
    str1 = 'skilleDayforePoint_'

    dataStart = '2020033109'
    duringDayS = 350
    for eDay in range(duringDayS):
        getTime1 = datetime.datetime.strptime(dataStart, '%Y%m%d%H')
        getTime1 = getTime1 + datetime.timedelta(hours=12 * eDay)
        getTimeStrF = getTime1.strftime('%Y%m%d%H')
        timeList = get_now_time(getTimeStrF)
        for eEle in listElement:
            print('【正在执行%s集成运算】' % eEle)
            arDataCombineR = combineData()
            print(arDataCombineR.shape)
            arVRCombineR = combineVR()
            #############################
            listCoordinate, listResult = [], []
            for i in range(161):
                for j in range(274):
                    listCoordinate.append(np.argmax(arVRCombineR[:, i, j]))
            for ki, kv in enumerate(listCoordinate):
                listResult.append(arDataCombineR[kv][ki])
            arrResult = np.array(listResult).reshape(161, 274)
            np.savetxt(pathRes + eEle + '\\' + timeList[1][2:] + '.024', arrResult, fmt='%.2f')
            print('【%s已完成】'%timeList[0])

#
#
# print(arDataCombineR)
# print('************')
# arVRofDA = pathVeriRes


# path1 = 'C:\\Users\\ybtd2\\Desktop\\新建文件夹\\'
# path2 = 'F:\\work\\2020Correct\\data\\TM_Result_DA\\TMIN\\'
# f1 = 'skilleDayforePoint_2020091508_10days_TMIN_DA.txt'
# f2 = 'skilleDayforePoint_2020091508_10days_TMIN_MB.txt'
# arDA = path1 + f1, skiprows=3)
# arMB = np.loadtxt(path1 + f2, skiprows=3)
# arDA1 = arDA.copy()
# ar3 = arDA - arMB
# arZero = np.zeros((161, 274))
# arBase0 = np.array([arZero, arDA])
#
# ar1  = np.append(arBase0, arMB)
# dim0 = arBase0.shape
# ar2 = ar1.reshape(dim0[0] + 1, dim0[1], dim0[2])
#
# for k in range(3):
#     for i in range(161):
#         for j in range(274):
#             print(np.nanmax(ar2[:, i, j]))
#             print(np.argmax(ar2[:, i, j]))
