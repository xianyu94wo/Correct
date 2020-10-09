import os
import pandas as pd
import numpy as np
import time
import datetime
import shutil

np.set_printoptions(suppress=True)


class CalculateAdjust(object):

    def __init__(self, element, SlidingStep, nowBJTStr=datetime.datetime.today().strftime('%Y%m%d%H')):
        self.element = element
        self.SlidingStep = SlidingStep
        self.nowHour = int(nowBJTStr[-2:])
        self.nowBJTStr = nowBJTStr
        self.qiBaoShiJian = self.get_now_time()
        self.listOfData = self.get_step_time()

    def get_now_time(self):
        '''
        按当天日期和时间判断指导报起报时间
        获取当前时间，判断当前时间是否超过中午12点，如果超过则返回当天日期+'2000'，如果未超过则返回当天日期+'0800'
        :return: 起报时间
        '''
        # nowBJT = datetime.datetime.today()  # 获取当前时间（北京时）
        # nowBJTStr = nowBJT.strftime('%Y%m%d%H')  # 时间格式转化为字符串格式
        # 若当前时间在下午13时之前，则设置起报时间为0800，否则设置为2000
        if self.nowHour < 13:
            qiBaoShiJian = self.nowBJTStr[:-2] + '0800'
        else:
            qiBaoShiJian = self.nowBJTStr[:-2] + '2000'
        return qiBaoShiJian

    def get_step_time(self):
        listDaysTemp = []
        for day in range(2, self.SlidingStep + 2):
            startTime = datetime.datetime.strptime(self.qiBaoShiJian[:-2], '%Y%m%d%H')
            getTime = startTime - datetime.timedelta(days=day)
            getTimeStr = getTime.strftime('%Y%m%d%H')
            listDaysTemp.append(getTimeStr)
        return sorted(listDaysTemp)

    def get_diff_dataframe(self, pathM, pathO):
        '''
        输出偏差df，输出列以滑动步长为准
        :param pathM: 模式基本路径
        :param pathO: 实况基本路径
        :param listOfData: 滑动步长范围内的资料名称列表
        :param baseDf: 打底DF
        :return: 返回包含滑动步长范围内的实况与预报偏差
        '''
        arZero = np.zeros((161, 274))
        arOne = np.ones((161, 274))
        arZero = arZero.reshape(arZero.shape[0] * arZero.shape[1])
        arOne = arOne.reshape(arOne.shape[0] * arOne.shape[1])
        dfBase = pd.DataFrame([arZero, arOne])

        for i, v in enumerate(self.listOfData):
            # 分别读取列表listOfData内的模式和实况资料
            path1 = pathM + v + '_' + self.element + '.txt'
            path2 = pathO + v + '_' + self.element + '.txt'
            # 之前的模式格点对应站点资料输出后无index和col，这里用np读取为array
            arM = np.loadtxt(path1)
            arO = np.loadtxt(path2)
            arO[arO >= 99] = np.nan
            arO[arO <= -99] = np.nan
            arM[arM >= 99] = np.nan
            arM[arM <= -99] = np.nan
            arDiff = arO - arM
            arDiff = arDiff.reshape(arDiff.shape[0] * arDiff.shape[1])
            dfBase.loc[str(i + 1)] = arDiff
            dfBase = dfBase
        dfBase.drop([0, 1], axis=0, inplace=True)
        return dfBase

    def calculate_median(self, diffDf, SlidingStep):
        '''
        求中位数和D中位数
        :param diffDf: diffDf
        :param baseDf: baseDf
        :return: 返回diffDf（因为原来diff可能因为全局变量或者局部变量被更改）、中位数array、Darray
        '''
        # diffDfT = diffDf.T
        medianArray = diffDf.median()
        diffDfDMedian = diffDf.T
        for i in range(1, SlidingStep + 1):
            diffDfDMedian['DMedian' + str(i)] = abs(diffDfDMedian[str(i)] - medianArray)

        diffDfDMedian.drop([str(xx + 1) for xx in range(SlidingStep)], axis=1, inplace=True)
        diffDfDMedian = diffDfDMedian.T
        DMedianArray = diffDfDMedian.median()
        return diffDf, medianArray, DMedianArray

    def calculate_omiga(self, diffDf, medianArray, DMedianArray, SlidingStep):
        '''
        计算Ω
        :param diffDf: diffDf
        :param medianArray: 中位数array
        :param DMedianArray: Darray
        :return: 返回diffDf（因为原来diff可能因为全局变量或者局部变量被更改）
        '''
        diffDfOmiga = diffDf.T
        for i in range(1, SlidingStep + 1):
            diffDfOmiga['omiga' + str(i)] = (diffDfOmiga[str(i)] - medianArray) / (7.5 * DMedianArray)

            diffDfOmiga.loc[diffDfOmiga['omiga' + str(i)] > 1, 'omiga' + str(i)] = 1
            diffDfOmiga.loc[diffDfOmiga['omiga' + str(i)] < -1, 'omiga' + str(i)] = -1
        diffDfOmiga.drop([str(xx + 1) for xx in range(SlidingStep)], axis=1, inplace=True)
        return diffDfOmiga

    def calculate_adjustDeno(self, diffDfOmiga, SlidingStep):
        '''
        计算adjust第二项的分母
        :param diffDf: diffDf
        :param baseDf: baseDf
        :return: 返回西格玛后的分母
        '''
        diffDfadjustDeno = diffDfOmiga
        for i in range(1, SlidingStep + 1):
            diffDfadjustDeno['adjustDeno' + str(i)] = (1 - diffDfadjustDeno['omiga' + str(i)] ** 2) ** 2
        diffDfadjustDeno.drop(['omiga' + str(xx + 1) for xx in range(SlidingStep)], axis=1, inplace=True)
        adjustDenoResult = diffDfadjustDeno.sum(axis=1)
        return diffDfadjustDeno, adjustDenoResult

    def calculate_adjustNumer(self, diffDf2, diffDfadjustDeno, medianArray, eSlidingStep):
        '''
        计算adjust第二项的分子
        :param diffDf: diffDf
        :param baseDf: baseDf
        :return: 返回西格玛后的分子
        '''
        print('******************************')
        diffDfadjustDenoTemp1 = pd.concat([diffDf2.T, diffDfadjustDeno], axis=1)
        for i in range(1, eSlidingStep + 1):
            diffDfadjustDenoTemp1['adjustNumer' + str(i)] = (diffDfadjustDenoTemp1[str(i)] - medianArray) * \
                                                            diffDfadjustDenoTemp1['adjustDeno' + str(i)]

        diffDfadjustDenoTemp1.drop(['adjustDeno' + str(xx + 1) for xx in range(eSlidingStep)], axis=1, inplace=True)
        diffDfadjustDenoTemp1.drop([str(xx + 1) for xx in range(eSlidingStep)], axis=1, inplace=True)
        adjustNumerResult = diffDfadjustDenoTemp1.sum(axis=1)
        return adjustNumerResult

    def output_result(self, adjustNumer, adjustDeno, medianArray):
        adjust = adjustNumer / adjustDeno
        adjustResult = medianArray + adjust
        adjustResult[adjustResult <= -40] = 0
        adjustResult[adjustResult >= 40] = 0
        modelResult = np.loadtxt(pathM + self.qiBaoShiJian[:-2] + '_' + self.element + '.txt')
        modelResult = modelResult.reshape(modelResult.shape[0] * modelResult.shape[1])
        CorrectResult = modelResult + adjustResult
        CorrectResultAr = CorrectResult.values
        CorrectResultAr = CorrectResultAr.reshape(161, 274)
        adjustResultTemp = np.array(adjustResult)
        adjustResultTemp = adjustResultTemp.reshape(161, 274)
        np.savetxt('F:\\work\\2020Correct\\data\\abc' + eEle + '.txt', adjustResultTemp, fmt='%.2f')
        return CorrectResultAr

    def check_file(self, FinalResult):
        checkTime = datetime.datetime.today()
        checkTimeStr = checkTime.strftime('%Y%m%d%H%M')  # 时间格式转化为字符串格式
        if self.qiBaoShiJian[-4:-2] == '08':
            if int(checkTimeStr[-4:]) > 555 and int(checkTimeStr[-4:]) < 640:
                if self.qiBaoShiJian[:-2] + '_' + eEle + '.txt' not in os.listdir(pathO):
                    CorrectResultAr = np.loadtxt(pathM + self.qiBaoShiJian[:-2] + '_' + eEle + '.txt')
                    return CorrectResultAr
            else:
                CorrectResultAr = FinalResult
                return CorrectResultAr
        elif self.qiBaoShiJian[-4:-2] == '20':
            if int(checkTimeStr[-4:]) > 1530 and int(checkTimeStr[-4:]) < 1620:
                if self.qiBaoShiJian[:-2] + '_' + eEle + '.txt' not in os.listdir(pathO):
                    CorrectResultAr = np.loadtxt(pathM + self.qiBaoShiJian[:-2] + '_' + eEle + '.txt')
                    return CorrectResultAr
            else:
                CorrectResultAr = FinalResult
                return CorrectResultAr


def all_attribute_of_object(obj):
    '''
    输出对象所有属性
    :param obj:对象名
    :return: 无返回值
    '''
    print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))


if __name__ == '__main__':
    timeStart = time.time()
    print('【开始运行获取订正程序】')
    # stationInfoFilePath = 'F:\\work\\2020Correct\\data\\StationInfo_648.txt'  # 站点信息文件，此文件中只有站点信息，为了DF索引而设
    # SlidingStep = 20
    # SlidingStep = [3, 5, 7, 10, 15, 20]
    SlidingStep = [20, ]
    element = ['TMIN', 'TMAX']
    # element = ['TMAX']
    pathM = 'F:\\work\\2020Correct\\data\\TM_md_24h_Grid\\'
    pathO = 'F:\\work\\2020Correct\\data\\TM_ob_24h_Grid\\'
    # element = ['TMIN']
    # baseDf = pd.read_csv(stationInfoFilePath, encoding='utf-8', sep=',', engine='python').set_index(
    #     'Station_Num')  # 读取站点信息文件
    # baseDf = baseDf['Station_Name']  # 只留一列
    startTimeStr = '2020020413'

    for eSlidingStep in SlidingStep:
        pathS = 'F:\\work\\2020Correct\\data\\TM_Result_Grid_' + str(eSlidingStep) + '\\'
        for eEle in element:
            try:
                ob1 = CalculateAdjust(eEle, eSlidingStep)
                all_attribute_of_object(ob1)
                diffDfData = ob1.get_diff_dataframe(pathM, pathO)
                diffDfBase = ob1.calculate_median(diffDfData, eSlidingStep)
                diffDf2, medianArray, DMedianArray = diffDfBase[0], diffDfBase[1], diffDfBase[2]
                diffDf3 = ob1.calculate_omiga(diffDf2, medianArray, DMedianArray, eSlidingStep)
                adjustDenoAll = ob1.calculate_adjustDeno(diffDf3, eSlidingStep)
                adjustNumer = ob1.calculate_adjustNumer(diffDf2, adjustDenoAll[0], medianArray, eSlidingStep)
                FinalResult = ob1.output_result(adjustNumer, adjustDenoAll[1], medianArray)

            except Exception as e:
                print(e)
                continue

            CorrectResultAr = ob1.check_file(FinalResult)
            gridFileSaveName = ob1.qiBaoShiJian[2:-2] + '.024'
            np.savetxt(pathS + eEle + '\\' + gridFileSaveName + '.temp', CorrectResultAr, fmt='%.2f')
            with open(pathS + eEle + '\\' + gridFileSaveName + '.temp') as f1:
                tempStr = f1.readlines()
            with open(pathS + eEle + '\\' + gridFileSaveName, 'w') as f2:
                f2.write('diamond 4 MBysj_20%s_%s %s' % (gridFileSaveName[:-4], eEle, '\n'))
                f2.write('20%s %s %s %s 24 0 %s' % (
                    gridFileSaveName[:-10], gridFileSaveName[2:4], gridFileSaveName[4:6], gridFileSaveName[6:8], '\n'))
                thirdLine = '0.05000 0.05000 89.3 102.95 31.4 39.4 274 161 10.000000 -40.000000 40.000000 5.000000 0.000000 '
                f2.write('%s %s' % (thirdLine, '\n'))

                f2.writelines(tempStr)
            os.remove(pathS + eEle + '\\' + gridFileSaveName + '.temp')

    costTime = time.time() - timeStart
    print("运行时间：【%.4f】秒" % costTime)
