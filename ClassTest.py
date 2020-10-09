import pandas as pd
import numpy as np
import datetime
import time
import os


class FindNearestPoint(object):
    '''
    选取离站点最近的格点
    '''

    def __init__(self, sPLat, sPLon, mRLat, mRLon):
        '''
        获取模式基本属性参数，包括分辨率和起始格点经纬度
        :param sPLat:模式起始纬度
        :param sPLon:模式起始经度
        :param mRLat:模式纬向分辨率
        :param mRLon:模式经向分辨率
        '''
        self.sPLat = sPLat
        self.sPLon = sPLon
        self.mRLat = mRLat
        self.mRLon = mRLon
        print('模式纬向分辨率为：', self.mRLat, ',模式经向分辨率为：', self.mRLon)
        print('模式纬向起始点为：', self.sPLat, ',模式经向起始点为：', self.sPLon)

    def nearestP_solo(self,startMPoint, modelResl, stationCoordinates):
        '''
        获取单纬度或单经度数据，转化为在模式分辨率（modelResl）下所在的格点坐标位置
        :param startMPoint: 模式起始经度或纬度
        :param modelResl: 模式分辨率
        :param stationCoordinates: 站点的经度或纬度信息
        :return:
        '''
        # 获取站点经度或纬度信息的整数部分
        sPIntPart = int(str(stationCoordinates).split('.')[0])
        # 获取站点经度或纬度小数部分，并除以分辨率。目的是得到经纬度小数部分所占用格点数
        numOfGPoint = format(float('0.' + str(stationCoordinates).split('.')[1]) / abs(modelResl), '.3f')
        # 获取站点经纬度小数部分所占格点数的整数部分，之后对小数部分进行判断，如果大于0.5，则多占一个格点，否则以整数部分为准
        numOfGPointIntPart = int(str(numOfGPoint).split('.')[0])
        numOfGPointFloatPart = float('0.' + str(numOfGPoint).split('.')[1])
        if numOfGPointFloatPart <= 0.5:
            numOfGPointIntPart = numOfGPointIntPart
        else:
            numOfGPointIntPart = numOfGPointIntPart + 1
        # 最终该经度或纬度所占格点数是该经纬度整数部分，加小数部分求格点数并乘以分辨率之和，最终除以分辨率得到
        # 事实上这一步是求出了距离该经度或纬度最近的格点经纬度
        finallonNum = sPIntPart + numOfGPointIntPart * abs(modelResl)
        finallonGrid = int((finallonNum - startMPoint) / modelResl + 1)
        return finallonGrid

if __name__ == '__main__':
    sPLat = 40.0
    mRLat = -0.125
    sPLon = 88.0
    mRLon = 0.125
    ob1 = FindNearestPoint(sPLat, sPLon, mRLat, mRLon)
    aa = ob1.nearestP_solo(0.0,0.05,10.026)
    print(aa)



# def findNearstPoint(startPoint,mdResl,positionStation):
#     '''
#     #查找最近点函数
#     #startPoint为模式起始经纬度，mdResl为模式分辨率，分经向和纬向，positionStation为站点经纬度
#     '''
#     intPartLon = int(str(format(positionStation,'.2f'))[:-3])
#     a = format(float('0.'+str(format(positionStation,'.2f'))[-2:])/abs(mdResl),'.2f')
#     b = int(str(a)[0])
#     c = float('0.'+str(a)[-2:])
#     if c <= 0.5:
#         b = b
#     else:
#         b = b+1
#     if mdResl < 0:
#         finallonNum = intPartLon+b*abs(mdResl)
#     else:
#         finallonNum = intPartLon+b*mdResl
#     finallonGrid = int((finallonNum - startPoint)/mdResl + 1)
#     return finallonNum,finallonGrid
#
# def outputGridNum(listLat,listLon,sPLat,sPLon,mRLat,mRlon):
#     '''
#     # 输出站点对应格点元组列表
#     #listLat：纬度坐标，listLon：经度坐标，sPLat：模式起始纬度，sPLon：模式起始经度，mRLat：纬向分辨率，mRlon：经向分辨率
#     '''
#     lista = []
#     listb = []
#     for i in listLat:
#         a = findNearstPoint(sPLat, mRLat, i)
#         lista.append(a[1])
#     for j in listLon:
#         b = findNearstPoint(sPLon, mRlon, j)
#         listb.append(b[1])
#     c = list(zip(lista, listb))
#     return c
#
#
#
# stationInfoFilePath = 'F:\\U盘备份\\data\\StationInfo\\StationInfo.txt'
# stDf = pd.read_csv(stationInfoFilePath,encoding='utf-8',sep=',',engine='python')
# listLat = list(stDf['lat'])
# listLon = list(stDf['lon'])
# sPLat = 40.0
# mRLat = -0.125
# sPLon = 88.0
# mRLon = 0.125
# listPoint = outputGridNum(listLat,listLon,sPLat,sPLon,mRLat,mRLon)
# print(listPoint)