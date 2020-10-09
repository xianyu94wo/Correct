import numpy as np
import pandas as pd
import datetime
import os
from FindNearestlyPoint.FNP import FindNearestPoint


# TTG为txttogrid的缩写
class ABC(object):
    '''
    读取格点数据输出对应站点位置的格点预报结果
    '''

    def __init__(self, element, gridBasePath, timeStr):
        '''

        :param sPLat: 老一套
        :param sPLon: 老一套
        :param mRLat: 老一套
        :param mRLon: 老一套
        :param element: 要素名称
        :param gridBasePath: 格点资料路径
        '''
        # self.sPLat = sPLat
        # self.mRLat = mRLat
        # self.sPLon = sPLon
        # self.mRLon = mRLon
        # self.element = element
        # self.gridBasePath = gridBasePath
        self.timeStr = timeStr
        self.element = element
        self.gridBasePath = gridBasePath
        self.nowTime = self.get_now_time()  # 获取当前时间
        self.previousTime = self.get_time_previous()  # 获取前一天时间
        self.previousBeforeTime = self.get_time_previous_before()  # 获取前两天时间
        # self.gridDataPath = self.check_data()[0]
        self.dataYear = self.nowTime[:4]
        self.dataDate = self.nowTime[:-4]
        self.dataTime = self.nowTime[:-2]
        self.gridDataPath = self.check_data()[0]

    def get_now_time(self):
        '''
        按当天日期和时间判断指导报起报时间
        获取当前时间，判断当前时间是否超过中午12点，如果超过则返回当天日期+'2000'，如果未超过则返回当天日期+'0800'
        :return: 起报时间
        '''
        #nowBJT =   # 获取当前时间（北京时）
        nowBJTStr = self.timeStr  # 时间格式转化为字符串格式
        nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
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
        if os.path.exists(self.gridBasePath + self.nowTime[:4] + '\\' + self.nowTime[
                                                                        :-4] + '\\' + self.element + '_' + self.nowTime[
                                                                                                           :-2] + '.024'):
            gridDataPath = self.gridBasePath + self.nowTime[:4] + '\\' + self.nowTime[
                                                                         :-4] + '\\' + self.element + '_' + self.nowTime[
                                                                                                            :-2] + '.024'
            # 下列几个要素暂时无用
            dataYear = gridDataPath.split('\\')[5]
            dataDate = gridDataPath.split('\\')[6]
            dataTime = gridDataPath.split('\\')[7][5:-4]
            # print(gridDataPath)
            return gridDataPath, dataYear, dataDate, dataTime
        elif os.path.exists(self.gridBasePath + self.previousTime[:4] + '\\' + self.previousTime[
                                                                               :-4] + '\\' + self.element + '_' + self.previousTime[
                                                                                                                  :-2] + '.048'):
            gridDataPath = self.gridBasePath + self.previousTime[:4] + '\\' + self.previousTime[
                                                                              :-4] + '\\' + self.element + '_' + self.previousTime[
                                                                                                                 :-2] + '.048'
            dataYear = gridDataPath.split('\\')[5]
            dataDate = gridDataPath.split('\\')[6]
            dataTime = gridDataPath.split('\\')[7][5:-4]
            # print(gridDataPath)
            return gridDataPath, dataYear, dataDate, dataTime
        elif os.path.exists(self.gridBasePath + self.previousBeforeTime[:4] + '\\' + self.previousBeforeTime[
                                                                                     :-4] + '\\' + self.element + '_' + self.previousBeforeTime[
                                                                                                                        :-2] + '.072'):
            gridDataPath = self.gridBasePath + self.previousBeforeTime[:4] + '\\' + self.previousBeforeTime[
                                                                                    :-4] + '\\' + self.element + '_' + self.previousBeforeTime[
                                                                                                                       :-2] + '.072'
            dataYear = gridDataPath.split('\\')[5]
            dataDate = gridDataPath.split('\\')[6]
            dataTime = gridDataPath.split('\\')[7][5:-4]
            # print(gridDataPath)
            return gridDataPath, dataYear, dataDate, dataTime
        else:
            print('近三个时次资料均未入库！请联系信息中心！')


def all_attribute_of_object(obj):
    '''
    输出对象所有属性
    :param obj:对象名
    :return: 无返回值
    '''
    print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))


if __name__ == '__main__':
    sPLat = 31.40
    mRLat = 0.05
    sPLon = 89.3
    mRLon = 0.05
    # eEle = 'TMIN'
    element = ['TMIN', 'TMAX']
    # 站点信息文件，此文件中只有站点信息，为了DF索引而设
    baseDfoFilePath = 'E:\\work\\2020Correct\\data\\StationInfo_648.txt'
    stationInfoFilePath = 'E:\\work\\2020Correct\\data\\StationInfo_648.txt'
    pathS = 'E:\\work\\2020Correct\\data\\TM_Result_648\\'
    pathGrid = 'E:\\work\\2020Correct\\data\\GRID\\'
    tempPath = 'E:\\work\\2020Correct\\data\\temp.txt'
    pathGridS = 'E:\\work\\2020Correct\\data\\TM_Result_648_Grid\\'

    # 读取站点信息文件
    baseDf = pd.read_csv(baseDfoFilePath, encoding='utf-8', sep=',', engine='python').set_index('Station_Num')

    firstDay = '2020012204'
    listTime = []
    for eday in range(230):
        startTime = datetime.datetime.strptime(firstDay, '%Y%m%d%H')
        getTime = startTime + datetime.timedelta(hours=12 * eday)
        getTimeStr = getTime.strftime('%Y%m%d%H')
        listTime.append(getTimeStr)
    print(listTime)



    for every12h in listTime:
        for eEle in element:
                obb = ABC(eEle, pathGrid,every12h)
                all_attribute_of_object(obb)
                aa = obb.nowTime + '_' + eEle + '.txt'
                path1 = pathS + aa

                df1 = pd.read_csv(path1, encoding='utf-8', sep=' ', engine='python').set_index('Station_Num')
                df2 = pd.concat([baseDf, df1[eEle + 'Correct']], axis=1)
                df2 = df2.drop(['Station_Name', 'City', 'County'], axis=1)
                dfTemp = df2['lon']
                df2.drop(labels=['lon'], axis=1, inplace=True)
                df2.insert(0, 'lon', dfTemp)
                df2.dropna(inplace=True)

                df2.to_csv(tempPath, sep=',', float_format='%.3f')
                df3 = pd.read_csv(tempPath, encoding='utf-8', sep=',', engine='python').set_index('Station_Num')

                ob1 = FindNearestPoint(sPLat, sPLon, mRLat, mRLon)
                gridNum = ob1.output_grid_num(tempPath)
                lista = list(df3[eEle + 'Correct'])

                ar1 = np.loadtxt(obb.gridDataPath, dtype=float)
                for index, value in enumerate(gridNum):
                    # print(i,v,list1[i])
                    list1 = []
                    list2 = []
                    list1.append(value[0] - 1)
                    list1.append(value[0])
                    list1.append(value[0] + 1)
                    list2.append(value[1] - 1)
                    list2.append(value[1])
                    list2.append(value[1] + 1)
                    for i in list1:
                        for j in list2:
                            bb = (i, j)
                            try:
                                ar1[i][j] = lista[index]
                            except IndexError:
                                print('无该点')
                if obb.dataTime[-2:] == '08':
                    faBaoTime = '040000'
                else:
                    faBaoTime = '160000'
                gridFileSaveName = obb.nowTime[2:-2] + '.024'
                np.savetxt(pathGridS + eEle + '\\' + gridFileSaveName + '.temp', ar1, fmt='%.2f')
                with open(pathGridS + eEle + '\\' + gridFileSaveName + '.temp') as f1:
                    tempStr = f1.readlines()
                with open(pathGridS + eEle + '\\' + gridFileSaveName, 'w') as f2:
                    f2.write('diamond 4 MBysj_20%s_%s %s' % (gridFileSaveName[:-4], eEle, '\n'))
                    f2.write('20%s %s %s %s 24 0 %s' % (
                    gridFileSaveName[:-10], gridFileSaveName[2:4], gridFileSaveName[4:6], gridFileSaveName[6:8], '\n'))
                    thirdLine = '0.05000 0.05000 89.3 102.95 31.4 39.4 274 161 10.000000 -100.000000 88.000000 10.000000 0.000000 '
                    f2.write('%s %s' % (thirdLine, '\n'))

                    f2.writelines(tempStr)
                os.remove(pathGridS + eEle + '\\' + gridFileSaveName + '.temp')
