import numpy as np
import pandas as pd
import time
import os
import sys

sys.path.append('E:\\workspace\\work\\Correct\\CorrectClass\\')
from get_now_time import GetNowTime
from FNP import FindNearestPoint


if __name__ == '__main__':
    sPLat = 31.40
    mRLat = 0.05
    sPLon = 89.3
    mRLon = 0.05
    # eEle = 'TMIN'
    element = ['TMIN', 'TMAX']
    # 站点信息文件，此文件中只有站点信息，为了DF索引而设
    corBasePath = 'F:\\work\\2020Correct\\data\\'
    baseDfoFilePath = corBasePath + 'stationInfo\\StationInfo_648.txt'
    path648 = corBasePath + 'TM_Result_648\\'
    pathDA = corBasePath + 'TM_Result_DA\\'
    pathMB = corBasePath + 'TM_Result_Grid_20\\'
    pathSA = corBasePath + 'TM_Result_StaionAdd\\'
    pathCombine = [pathDA, pathMB]
    # pathGrid = 'E:\\work\\2020Correct\\data\\GRID\\'
    # tempPath = 'E:\\work\\2020Correct\\data\\temp.txt'
    # pathGridS = 'E:\\work\\2020Correct\\data\\TM_Result_648_Grid\\'

    # 读取站点信息文件
    timeStart = time.time()
    print('【开始运行站点融入格点程序】')
    getTimeOb = GetNowTime()
    #getTimeOb.print_all_attribute_of_object()
    baseDf = pd.read_csv(baseDfoFilePath, encoding='utf-8', sep=',', engine='python').set_index('Station_Num')
    qiBaoShiJian = getTimeOb.qiBaoShiJian
    baoWenMing = qiBaoShiJian[2:-2] + '.024'
    for eEle in element:
        aa = qiBaoShiJian + '_' + eEle + '.txt'
        path1 = path648 + aa
        df1 = pd.read_csv(path1, encoding='utf-8', sep=' ', engine='python').set_index('Station_Num')
        df2 = pd.concat([baseDf, df1[eEle + 'Correct']], axis=1)
        df2.dropna(inplace=True)
        df2 = df2.drop(['Station_Name', 'City', 'County', 'Altitude'], axis=1)
        FNPob = FindNearestPoint(sPLat, sPLon, mRLat, mRLon)
        listLat1 = df2['lat']
        listLon1 = df2['lon']
        FNPob.listLon = listLon1
        FNPob.listLat = listLat1
        gridNumList = FNPob.output_grid_num()
        listStationCorrcet = list(df2[eEle + 'Correct'])
        # for i, v in enumerate(gridNumList):
        #     print(i,v,listStationCorrcet[i])
        #
        # print(listStationCorrcet)
        for eMethod in pathCombine:
            arTemp = np.loadtxt(eMethod + eEle + '\\' + baoWenMing, skiprows=3)
            for i, v in enumerate(gridNumList):
                arTemp[v[0], v[1]]  = listStationCorrcet[i]
                if eMethod == pathDA:
                    pathS = pathSA + 'DA\\'
                elif eMethod == pathMB:
                    pathS = pathSA + 'MB\\'

            np.savetxt(pathS + eEle + '\\' + baoWenMing + '.temp', arTemp, fmt='%.2f')
            with open(pathS + eEle + '\\' + baoWenMing + '.temp') as f1:
                tempStr = f1.readlines()
            with open(pathS + eEle + '\\' + baoWenMing, 'w') as f2:
                f2.write('diamond 4 ' + eMethod[25:-2]  + 'addS_20%s_%s %s' % (baoWenMing[:-4], eEle, '\n'))
                f2.write('20%s %s %s %s 24 0 %s' % (
                    baoWenMing[:-10], baoWenMing[2:4], baoWenMing[4:6], baoWenMing[6:8], '\n'))
                thirdLine = '0.05000 0.05000 89.3 102.95 31.4 39.4 274 161 10.000000 -40.000000 40.000000 5.000000 0.000000 '
                f2.write('%s %s' % (thirdLine, '\n'))

                f2.writelines(tempStr)
            os.remove(pathS + eEle + '\\' + baoWenMing + '.temp')
    costTime = time.time() - timeStart
    print("运行时间：【%.4f】秒" % costTime)


