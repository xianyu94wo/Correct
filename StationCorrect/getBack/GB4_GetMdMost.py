import pandas as pd
import numpy as np
import datetime
import os
from FindNearestlyPoint.FNP import FindNearestPoint


class OutPutGridResultForEveryStaion(object):
    '''
    读取格点数据输出对应站点位置的格点预报结果
    '''
    def __init__(self,sPLat, sPLon, mRLat, mRLon, element, gridBasePath):
        '''

        :param sPLat: 老一套
        :param sPLon: 老一套
        :param mRLat: 老一套
        :param mRLon: 老一套
        :param element: 要素名称
        :param gridBasePath: 格点资料路径
        '''
        self.sPLat = sPLat
        self.mRLat = mRLat
        self.sPLon = sPLon
        self.mRLon = mRLon
        self.element = element
        self.gridBasePath = gridBasePath
        self.nowTime = self.get_now_time() # 获取当前时间
        self.previousTime = self.get_time_previous() # 获取前一天时间
        self.previousBeforeTime = self.get_time_previous_before() #获取前两天时间
        self.gridDataPath = self.check_data()[0]
        self.dataYear = self.nowTime[:4]
        self.dataDate = self.nowTime[:-4]
        self.dataTime = self.nowTime[:-2]


    def get_now_time(self):
        '''
        按当天日期和时间判断指导报起报时间
        获取当前时间，判断当前时间是否超过中午12点，如果超过则返回当天日期+'2000'，如果未超过则返回当天日期+'0800'
        :return: 起报时间
        '''
        nowBJT = datetime.datetime.today()#获取当前时间（北京时）
        nowBJTStr = nowBJT.strftime('%Y%m%d%H')#时间格式转化为字符串格式
        nowHour = int(nowBJTStr[-2:])#字符串中获取小时并转为整数
        # 若当前时间在下午13时之前，则设置起报时间为0800，否则设置为2000
        if nowHour < 13:
            qiBaoShiJian = nowBJTStr[:-2] + '0800'
        else:
            qiBaoShiJian = nowBJTStr[:-2] + '2000'
        return qiBaoShiJian

    def get_time_previous(self):
        '''
        获取当前时间起报点的前12h时间
        :param nowTime: 当前时间对应的起报点
        :return: 前12h时间
        '''
        startTime = datetime.datetime.strptime(self.nowTime[:-2], '%Y%m%d%H')
        getTime = startTime - datetime.timedelta(hours=24)
        getTimeStr = getTime.strftime('%Y%m%d%H')
        return  getTimeStr + '00'

    def get_time_previous_before(self):
        '''
        获取当前时间起报点的前24h时间
        :param nowTime: 当前时间对应的起报点
        :return: 前24h时间
        '''
        startTime = datetime.datetime.strptime(self.nowTime[:-2], '%Y%m%d%H')
        getTime = startTime - datetime.timedelta(hours=48)
        getTimeStr = getTime.strftime('%Y%m%d%H')
        return  getTimeStr + '00'

    def check_data(self):
        '''

        :param gridBasePath: grid资料存放路径（grid资料为解码SCMOC后的指导报）
        :param nowTime: 当前时间对应的起报时间
        :param previousTime: 当前时间前一天对应的起报时间
        :param previousBeforeTime: 当前时间前两天对应的起报时间
        :return: 返回可读取的资料路径
        '''
        if os.path.exists(self.gridBasePath + self.nowTime[:4] + '\\' +  self.nowTime[:-4] + '\\' + self.element + '_' + self.nowTime[:-2] +'.024'):
            gridDataPath = self.gridBasePath + self.nowTime[:4] + '\\' +  self.nowTime[:-4] + '\\' + self.element + '_' + self.nowTime[:-2] +'.024'
            # 下列几个要素暂时无用
            dataYear = gridDataPath.split('\\')[5]
            dataDate = gridDataPath.split('\\')[6]
            dataTime = gridDataPath.split('\\')[7][5:-4]
            #print(gridDataPath)
            return gridDataPath, dataYear, dataDate, dataTime
        elif os.path.exists(self.gridBasePath + self.previousTime[:4] + '\\' + self.previousTime[:-4] + '\\' + self.element + '_' + self.previousTime[:-2] + '.048'):
            gridDataPath = self.gridBasePath + self.previousTime[:4] + '\\' + self.previousTime[:-4] + '\\' + self.element + '_' + self.previousTime[:-2] + '.048'
            dataYear = gridDataPath.split('\\')[5]
            dataDate = gridDataPath.split('\\')[6]
            dataTime = gridDataPath.split('\\')[7][5:-4]
            #print(gridDataPath)
            return gridDataPath, dataYear, dataDate, dataTime
        elif os.path.exists(self.gridBasePath + self.previousBeforeTime[:4] + '\\' + self.previousBeforeTime[:-4] + '\\' + self.element + '_' + self.previousBeforeTime[:-2] + '.072'):
            gridDataPath = self.gridBasePath + self.previousBeforeTime[:4] + '\\' + self.previousBeforeTime[:-4] + '\\' + self.element + '_' + self.previousBeforeTime[:-2] + '.072'
            dataYear = gridDataPath.split('\\')[5]
            dataDate = gridDataPath.split('\\')[6]
            dataTime = gridDataPath.split('\\')[7][5:-4]
            #print(gridDataPath)
            return gridDataPath, dataYear, dataDate, dataTime
        else:
            print('近三个时次资料均未入库！请联系信息中心！')

    def output_grid_result(self,gridResultPath):
        '''
        将对应站点位置的格点预报结果输出为txt
        :param gridResultPath: 输出路径
        :return: 返回各站预报结果的一维数组
        '''
        global stationInfoFilePath
        gridData = np.loadtxt(self.gridDataPath)
        gridNumList = FindNearestPoint(sPLat, sPLon, mRLat, mRLon)
        gridNum = gridNumList.output_grid_num(stationInfoFilePath)
        listTemp = []
        for eNum in gridNum:
            singleData = gridData[eNum[0]-1,eNum[1]-1]
            listTemp.append(singleData)
        ar1 = np.array(listTemp)
        np.savetxt(gridResultPath + self.dataTime + '_' + self.element + '.txt' ,ar1,fmt='%.2f')
        return ar1

class OutPutGridResultForEveryStaionGB(object):
    '''
    回补历史数据
    读取格点数据输出对应站点位置的格点预报结果
    '''

    def __init__(self, sPLat, sPLon, mRLat, mRLon, element, gridBasePath, duringDays):
        '''

        :param sPLat: 老一套
        :param sPLon: 老一套
        :param mRLat: 老一套
        :param mRLon: 老一套
        :param element: 要素名称
        :param gridBasePath: 格点资料路径
        '''
        self.sPLat = sPLat
        self.mRLat = mRLat
        self.sPLon = sPLon
        self.mRLon = mRLon
        self.element = element
        self.gridBasePath = gridBasePath
        self.duringDays = duringDays
        self.nowTime = self.get_time_gb()  # 获取当前时间
        self.previousTime = self.get_time_previous()  # 获取前一天时间
        self.previousBeforeTime = self.get_time_previous_before()  # 获取前两天时间
        self.gridDataPath = self.check_data()[0]
        self.dataYear = self.nowTime[:4]
        self.dataDate = self.nowTime[:-4]
        self.dataTime = self.nowTime[:-2]

    def get_time_gb(self):
        '''
        按当天日期和时间判断指导报起报时间
        获取当前时间，判断当前时间是否超过中午12点，如果超过则返回当天日期+'2000'，如果未超过则返回当天日期+'0800'
        :return: 起报时间
        '''

        startTimeStr = '2020082107'
        startTime = datetime.datetime.strptime(startTimeStr, '%Y%m%d%H')
        getTime = startTime + datetime.timedelta(hours=12 * self.duringDays)
        getTimeStr = getTime.strftime('%Y%m%d%H')  # 时间格式转化为字符串格式
        nowHour = int(getTimeStr[-2:])  # 字符串中获取小时并转为整数
        # 若当前时间在下午13时之前，则设置起报时间为0800，否则设置为2000
        if nowHour < 13:
            qiBaoShiJian = getTimeStr[:-2] + '0800'
        else:
            qiBaoShiJian = getTimeStr[:-2] + '2000'
        return qiBaoShiJian

    def get_time_previous(self):
        '''
        获取当前时间起报点的前12h时间
        :param nowTime: 当前时间对应的起报点
        :return: 前12h时间
        '''
        startTime = datetime.datetime.strptime(self.nowTime[:-2], '%Y%m%d%H')
        getTime = startTime - datetime.timedelta(hours=24)
        getTimeStr = getTime.strftime('%Y%m%d%H')
        return getTimeStr + '00'

    def get_time_previous_before(self):
        '''
        获取当前时间起报点的前24h时间
        :param nowTime: 当前时间对应的起报点
        :return: 前24h时间
        '''
        startTime = datetime.datetime.strptime(self.nowTime[:-2], '%Y%m%d%H')
        getTime = startTime - datetime.timedelta(hours=48)
        getTimeStr = getTime.strftime('%Y%m%d%H')
        return getTimeStr + '00'

    def check_data(self):
        '''

        :param gridBasePath: grid资料存放路径（grid资料为解码SCMOC后的指导报）
        :param nowTime: 当前时间对应的起报时间
        :param previousTime: 当前时间前一天对应的起报时间
        :param previousBeforeTime: 当前时间前两天对应的起报时间
        :return: 返回可读取的资料路径
        '''

        if os.path.exists(self.gridBasePath + self.nowTime[:4] + '\\' + self.nowTime[:-4] + '\\' + self.element + '_' + self.nowTime[:-2] + '.024'):
            gridDataPath = self.gridBasePath + self.nowTime[:4] + '\\' + self.nowTime[:-4] + '\\' + self.element + '_' + self.nowTime[:-2] + '.024'
            # 下列几个要素暂时无用
            dataYear = gridDataPath.split('\\')[5]
            dataDate = gridDataPath.split('\\')[6]
            dataTime = gridDataPath.split('\\')[7][5:-4]
            # print(gridDataPath)
            return gridDataPath, dataYear, dataDate, dataTime
        elif os.path.exists(self.gridBasePath + self.previousTime[:4] + '\\' + self.previousTime[:-4] + '\\' + self.element + '_' + self.previousTime[:-2] + '.048'):
            gridDataPath = self.gridBasePath + self.previousTime[:4] + '\\' + self.previousTime[:-4] + '\\' + self.element + '_' + self.previousTime[:-2] + '.048'
            dataYear = gridDataPath.split('\\')[5]
            dataDate = gridDataPath.split('\\')[6]
            dataTime = gridDataPath.split('\\')[7][5:-4]
            # print(gridDataPath)
            return gridDataPath, dataYear, dataDate, dataTime
        elif os.path.exists(self.gridBasePath + self.previousBeforeTime[:4] + '\\' + self.previousBeforeTime[:-4] + '\\' + self.element + '_' + self.previousBeforeTime[:-2] + '.072'):
            gridDataPath = self.gridBasePath + self.previousBeforeTime[:4] + '\\' + self.previousBeforeTime[:-4] + '\\' + self.element + '_' + self.previousBeforeTime[:-2] + '.072'
            dataYear = gridDataPath.split('\\')[5]
            dataDate = gridDataPath.split('\\')[6]
            dataTime = gridDataPath.split('\\')[7][5:-4]
            # print(gridDataPath)
            return gridDataPath, dataYear, dataDate, dataTime
        else:
            print('近三个时次资料均未入库！请联系信息中心！')

    def output_grid_result(self, gridResultPath):
        '''
        将对应站点位置的格点预报结果输出为txt
        :param gridResultPath: 输出路径
        :return: 返回各站预报结果的一维数组
        '''
        global stationInfoFilePath
        gridData = np.loadtxt(self.gridDataPath)
        gridNumList = FindNearestPoint(sPLat, sPLon, mRLat, mRLon)
        gridNum = gridNumList.output_grid_num(stationInfoFilePath)
        listTemp = []
        for eNum in gridNum:
            singleData = gridData[eNum[0] - 1, eNum[1] - 1]
            listTemp.append(singleData)
        ar1 = np.array(listTemp)
        np.savetxt(gridResultPath + self.dataTime + '_' + self.element + '.txt', ar1, fmt='%.2f')
        return ar1

if __name__ == '__main__':
    sPLat = 31.40
    mRLat = 0.05
    sPLon = 89.3
    mRLon = 0.05
    element = ['TMIN','TMAX']
    stationInfoFilePath = 'E:\\work\\2020Correct\\data\\StationInfo_648.txt'
    gridBasePath = 'F:\\work\\2020Correct\\data\\GRID\\'
    gridResultPath ='F:\\work\\2020Correct\\data\\TM_md_24h_648\\'

    ####################### 获取实时数据 ####################
    # for eEle in element:
    #     ob1 = OutPutGridResultForEveryStaion(sPLat,sPLon,mRLat,mRLon,eEle,gridBasePath)
    #     checkData = ob1.check_data()
    #     ar1 = ob1.output_grid_result(gridResultPath)

    #######################回补历史数据###################
    for i in range(1000):
        for eEle in element:
            ob2 = OutPutGridResultForEveryStaionGB(sPLat,sPLon,mRLat,mRLon,eEle,gridBasePath,i)
            checkData2 = ob2.check_data()
            print(checkData2)
            ar2 = ob2.output_grid_result(gridResultPath)

    print('DONE')