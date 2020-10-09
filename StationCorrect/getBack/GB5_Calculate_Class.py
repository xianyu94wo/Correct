import os
import pandas as pd
import numpy as np
import time
import datetime

np.set_printoptions(suppress=True)


class CalculateAdjust(object):

    def __init__(self, element, SlidingStep, qiBaoShiJian):
        self.element = element
        self.SlidingStep = SlidingStep
        self.qiBaoShiJian = qiBaoShiJian
        self.listOfData = self.get_step_time()

    def get_now_time(self):
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

    def get_step_time(self):
        listDaysTemp = []
        for day in range(2, self.SlidingStep + 2):
            startTime = datetime.datetime.strptime(self.qiBaoShiJian[:-2], '%Y%m%d%H')
            getTime = startTime - datetime.timedelta(days=day)
            getTimeStr = getTime.strftime('%Y%m%d%H')
            listDaysTemp.append(getTimeStr)
        return sorted(listDaysTemp)

    def get_diff_dataframe(self, pathM, pathO, baseDf):
        '''
        输出偏差df，输出列以滑动步长为准
        :param pathM: 模式基本路径
        :param pathO: 实况基本路径
        :param listOfData: 滑动步长范围内的资料名称列表
        :param baseDf: 打底DF
        :return: 返回包含滑动步长范围内的实况与预报偏差
        '''
        for i in self.listOfData:
            # 分别读取列表listOfData内的模式和实况资料
            path1 = pathM + i + '_' + self.element + '.txt'
            path2 = pathO + i + '_' + self.element + '.txt'
            # 之前的模式格点对应站点资料输出后无index和col，这里用np读取为array
            ar1 = np.loadtxt(path1)
            # 用pd读取实况资料
            dfO = pd.read_csv(path2, encoding='utf-8', engine='python', index_col=0)
            # 添加实况资料到模式资料的df中
            dfO[self.element + 'm'] = ar1
            # 求偏差，并将偏差列名设置为列表index对应的名称，偏差用O-M
            dfO[self.element + 'diff' + str(self.listOfData.index(i) + 1)] = dfO[self.element] - dfO[self.element + 'm']
            # 删除不需要的列
            dfO = dfO.drop([self.element + 'm', self.element], axis=1)
            # 合并各偏差
            baseDf = pd.concat([baseDf, dfO], axis=1)
        diffDf = baseDf.drop(['Station_Name'], axis=1)
        return diffDf

    def calculate_median(self, diffDf, baseDf,SlidingStep):
        '''
        求中位数和D中位数
        :param diffDf: diffDf
        :param baseDf: baseDf
        :return: 返回diffDf（因为原来diff可能因为全局变量或者局部变量被更改）、中位数array、Darray
        '''
        diffDfT = diffDf.T
        medianArray = diffDfT.median()
        for i in range(1, SlidingStep + 1):
            diffDf['DMedian' + str(i)] = abs(diffDf[self.element + 'diff' + str(i)] - medianArray)
            DMedianDf = pd.concat([baseDf, diffDf['DMedian' + str(i)]], axis=1)
            diffDf = diffDf.drop(['DMedian' + str(i)], axis=1)
            baseDf = DMedianDf
        DMedianDf = DMedianDf.drop(['Station_Name'], axis=1)

        DMedianDfT = DMedianDf.T
        DMedianArray = DMedianDfT.median()
        # diffDf['medianArray'] = medianArray
        # diffDf['DMedianArray'] = DMedianArray
        return diffDf, medianArray, DMedianArray

    def calculate_omiga(self, diffDf, medianArray, DMedianArray, SlidingStep):
        '''
        计算Ω
        :param diffDf: diffDf
        :param medianArray: 中位数array
        :param DMedianArray: Darray
        :return: 返回diffDf（因为原来diff可能因为全局变量或者局部变量被更改）
        '''
        for i in range(1, SlidingStep + 1):
            diffDf['omiga' + str(i)] = (diffDf[self.element + 'diff' + str(i)] - medianArray) / (7.5 * DMedianArray)
            diffDf.loc[diffDf['omiga' + str(i)] > 1, 'omiga' + str(i)] = 1
            diffDf.loc[diffDf['omiga' + str(i)] < -1, 'omiga' + str(i)] = -1
        return diffDf

    def calculate_adjustDeno(self, diffDf, baseDf, SlidingStep):
        '''
        计算adjust第二项的分母
        :param diffDf: diffDf
        :param baseDf: baseDf
        :return: 返回西格玛后的分母
        '''
        for i in range(1, SlidingStep + 1):
            diffDf['adjustDeno' + str(i)] = (1 - diffDf['omiga' + str(i)] ** 2) ** 2
            adjustDenoDf = pd.concat([baseDf, diffDf['adjustDeno' + str(i)]], axis=1)
            diffDf = diffDf.drop(['adjustDeno' + str(i)], axis=1)
            baseDf = adjustDenoDf
        adjustDenoDf = adjustDenoDf.drop(['Station_Name'], axis=1)
        adjustDenoResult = adjustDenoDf.sum(axis=1)
        # print(adjustDenoResult)
        return adjustDenoResult

    def calculate_adjustNumer(self, diffDf, baseDf, medianArray,SlidingStep):
        '''
        计算adjust第二项的分子
        :param diffDf: diffDf
        :param baseDf: baseDf
        :return: 返回西格玛后的分子
        '''
        for i in range(1, SlidingStep + 1):
            diffDf['adjustNumer' + str(i)] = (diffDf[self.element + 'diff' + str(i)] - medianArray) * (
                        1 - diffDf['omiga' + str(i)] ** 2) ** 2
            adjustNumerDf = pd.concat([baseDf, diffDf['adjustNumer' + str(i)]], axis=1)
            diffDf = diffDf.drop(['adjustNumer' + str(i)], axis=1)
            baseDf = adjustNumerDf
        adjustNumerDf = adjustNumerDf.drop(['Station_Name'], axis=1)
        adjustNumerResult = adjustNumerDf.sum(axis=1)
        # print(adjustNumerResult)
        return adjustNumerResult

    def output_result(self, adjustNumer, adjustDeno, medianArray):
        adjust = adjustNumer / adjustDeno
        adjustResult = medianArray + adjust
        modelResult = np.loadtxt(pathM + self.qiBaoShiJian[:-2] + '_' + self.element + '.txt')
        CorrectResult = modelResult + adjustResult
        baseDfResult = pd.read_csv(stationInfoFilePath, encoding='utf-8', sep=',', engine='python').set_index(
            'Station_Num')  # 读取站点信息文件
        baseDfResult[self.element + 'modelResult'] = modelResult
        baseDfResult[self.element + 'adjustResult'] = adjustResult
        baseDfResult[self.element + 'Correct'] = CorrectResult
        baseDfResult = baseDfResult.drop(['Station_Name', 'City', 'County', 'lat', 'lon', 'Altitude'], axis=1)
        # print(baseDfResult)
        return baseDfResult
        # return baseDfResult[self.element + 'Correct']


def get_time_ob(duringDays, startTimeStr):
    '''
    按当天日期和时间判断指导报起报时间
    获取当前时间，判断当前时间是否超过中午12点，如果超过则返回当天日期+'2000'，如果未超过则返回当天日期+'0800'
    :return: 起报时间
    '''

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


if __name__ == '__main__':


    stationInfoFilePath = 'E:\\work\\2020Correct\\data\\StationInfo_648.txt'  # 站点信息文件，此文件中只有站点信息，为了DF索引而设
    #SlidingStep = 20
    SlidingStep = [20]
    element = ['TMIN', 'TMAX']
    pathM = 'F:\\work\\2020Correct\\data\\TM_md_24h_648\\'
    pathO = 'F:\\work\\2020Correct\\data\\TM_ob_24h_648\\'

    # element = ['TMIN']

    baseDf = pd.read_csv(stationInfoFilePath, encoding='utf-8', sep=',', engine='python').set_index(
        'Station_Num')  # 读取站点信息文件
    baseDf = baseDf['Station_Name']  # 只留一列
    startTimeStr = '2020082107'
    for eSlidingStep in SlidingStep:
        pathS = 'F:\\work\\2020Correct\\data\\TM_Result_648_' + str(eSlidingStep) + '\\'
        for eDay in range(500):  # 所需回代的天数乘以2
            qiBaoShiJian = get_time_ob(eDay, startTimeStr)
            try :
                for eEle in element:
                    # print(eEle)
                    ob1 = CalculateAdjust(eEle, eSlidingStep, qiBaoShiJian)
                    print(ob1.listOfData)
                    diffDf1 = ob1.get_diff_dataframe(pathM, pathO, baseDf)
                    diffDfBase = ob1.calculate_median(diffDf1, baseDf,eSlidingStep)
                    diffDf2, medianArray, DMedianArray = diffDfBase[0], diffDfBase[1], diffDfBase[2]
                    diffDf3 = ob1.calculate_omiga(diffDf2, medianArray, DMedianArray,eSlidingStep)
                    adjustDeno = ob1.calculate_adjustDeno(diffDf3, baseDf,eSlidingStep)
                    adjustNumer = ob1.calculate_adjustNumer(diffDf3, baseDf, medianArray,eSlidingStep)
                    FinalResult = ob1.output_result(adjustNumer, adjustDeno, medianArray)
                    FinalResult.to_csv(pathS + ob1.qiBaoShiJian + '_' + eEle + '.txt', sep=' ', float_format='%.2f')
            except OSError:
                print('没有了')
                continue

