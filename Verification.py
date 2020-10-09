import pandas as pd
import numpy as np
import os
np.set_printoptions(suppress=True)

def get_file_list(pathM,qiBaoShiJian):
    '''
    按预报结果文件夹中的文件确定所需检验的文件名
    :param pathM: 预报结果文件夹
    :return:
    '''
    listOfForcastDate = []
    listOfForcastFile = sorted(os.listdir(pathM))
    for i in listOfForcastFile:
        listOfForcastDate.append(i.split('_')[0][:-4] + qiBaoShiJian)#由于输出的预报文件后多了00，此处去掉
    return sorted(set(listOfForcastDate))#预报文件文件夹中后缀分TMAX和TMIN，因此用set进行去重

def get_correct_verification(pathO,pathM,element,listOfForcastDate,stDf):
    '''
    用预报结果和实况计算各站多日平均绝对误差和每日全站平均绝对误差
    :param pathO: 实况资料基本路径
    :param pathM: 预报结果基本路径
    :param element: 检验要素
    :param listOfForcastDate: get_file_list获取的所需检验文件名列表
    :param stDf: 打底DF
    :return:各站多日平均绝对误差和每日全站平均绝对误差
    '''
    for i in listOfForcastDate:
        pathOb = pathO + i + '_' + element + '.txt'
        pathFc = pathM + i + '00_' + element + '.txt'
        dfOb = pd.read_csv(pathOb, encoding='utf-8', engine='python',index_col=0)
        dfOb = dfOb[~dfOb.index.duplicated(keep='first')]
        dfFc = pd.read_csv(pathFc, encoding='utf-8', engine='python',sep=' ').set_index('Station_Num')
        dfV = pd.concat([dfFc, dfOb], axis=1)
        dfV['corV'] = abs(dfV[element + 'Correct'] - dfV[element])
        dfCorV = pd.concat([stDf, dfV['corV']], axis=1)
        stDf = dfCorV
    dfCorV = dfCorV.drop(['Station_Name', 'City', 'County', 'lat', 'lon', 'Altitude'], axis=1)
    dfCorV = dfCorV.dropna()
    dfCorVT = dfCorV.T
    dfCorVA = dfCorV.mean()#每日全站平均绝对误差
    dfCorVAT = dfCorVT.mean()#各站多日平均绝对误差

    # dfCorV.to_csv(pathS +  'test1.txt', sep=' ', float_format='%.3f')
    # dfCorVT.to_csv(pathS + 'test2.txt', sep=' ', float_format='%.3f')
    # dfCorVA.to_csv(pathS + 'CorVA' + '_' + element + '.txt', sep=' ', float_format='%.3f')
    # dfCorVAT.to_csv(pathS + 'CorVA_S' + '_' + element + '.txt', sep=' ', float_format='%.3f')
    # dfCorVT.to_csv(pathS + 'test' + '_' + element + '.txt', sep=' ', float_format='%.3f')

    return dfCorVA,dfCorVAT

def get_model_verification(pathO,pathM,element,listOfForcastDate,stDf):
    '''
    与上个函数基本一致，只不过求的是模式（SCMOC）预报结果
    :param pathO: 实况资料基本路径
    :param pathM: 预报结果基本路径
    :param element: 检验要素
    :param listOfForcastDate: get_file_list获取的所需检验文件名列表
    :param stDf: 打底DF
    :return:各站多日平均绝对误差和每日全站平均绝对误差
    '''
    for i in listOfForcastDate:
        pathOb = pathO + i + '_' + element + '.txt'
        pathFc = pathM + i + '00_' + element + '.txt'

        dfOb = pd.read_csv(pathOb, encoding='utf-8', engine='python',index_col=0)
        dfOb = dfOb[~dfOb.index.duplicated(keep='first')]
        dfFc = pd.read_csv(pathFc, encoding='utf-8', engine='python',sep=' ').set_index('Station_Num')
        dfV = pd.concat([dfFc, dfOb], axis=1)
        dfV['modelV'] = abs(dfV[element + 'modelResult'] - dfV[element])
        dfModelV = pd.concat([stDf, dfV['modelV']], axis=1)
        stDf = dfModelV
    dfModelV = dfModelV.drop(['Station_Name', 'City', 'County', 'lat', 'lon', 'Altitude'], axis=1)
    dfModelV = dfModelV.dropna()
    dfModelVA = dfModelV.mean()
    dfModelVAT = dfModelV.T.mean()

    # dfModelVA.to_csv(pathS + 'ModelVA' + '_' + element + '.txt', sep=' ', float_format='%.3f')
    # dfModelVAT.to_csv(pathS + 'ModelVA_S' + '_' + element + '.txt', sep=' ', float_format='%.3f')
    return dfModelVA,dfModelVAT

def get_skill_point_EVERYDAY(CorVA,ModelVA,element,listOfForcastDate,qiBaoShiJian):

    ar1 = np.array(CorVA)
    ar2 = np.array(ModelVA)
    ar3 = np.stack((ar1,ar2))

    df1 = pd.DataFrame(ar3,columns=listOfForcastDate,index=('订正MAE','指导MAE'))
    df1 = df1.T
    df1['订正技巧'] = (df1['指导MAE'] - df1['订正MAE']) / df1['指导MAE']
    df2 = df1.mean()
    print(df2)
    df1.to_csv(pathS + 'SkillofEveryDay' + '_' + element + '_' +qiBaoShiJian + '.txt', sep=' ', float_format='%.3f')
    df2.to_csv(pathS + 'SkillofEveryDayA' + '_' + element + '_' +qiBaoShiJian + '.txt', sep=' ', float_format='%.3f')

def get_skill_point_EVERYSTATION(CorVAT,ModelVAT,element,qiBaoShiJian):
    df1 = pd.concat([CorVAT,ModelVAT],axis=1)
    df1.columns = ['订正MAE','指导MAE']
    df1['订正技巧'] = (df1['指导MAE'] - df1['订正MAE']) / df1['指导MAE']
    df2 = df1.mean()
    df1.to_csv(pathS + 'SkillofEveryStation' + '_' + element + '_' +qiBaoShiJian + '.txt', sep=' ', float_format='%.3f')
    df2.to_csv(pathS + 'SkillofEveryStationA' + '_' + element + '_' + qiBaoShiJian + '.txt', sep=' ', float_format='%.3f')
    # ar1 = np.array(CorVAT)
    # ar2 = np.array(ModelVAT)
    # ar3 = (ar2 - ar1) / ar2
    # np.savetxt(pathS+ 'SkillofEveryStation' + '_' + element + '.txt',ar3,fmt='%.3f')



if __name__ == '__main__':
    #'2020081708_TMAX.txt'
    #eEle = 'TMAX'
    #qiBaoShiJian = '08'
    qiBaoShiJian = ['08','20']#,'20'
    element = ['TMAX','TMIN']#,'TMIN'
    # pathO = 'E:\\work\\2020Correct\\data\\testO\\'
    # pathM = 'E:\\work\\2020Correct\\data\\testM\\'
    # pathS = 'E:\\work\\2020Correct\\data\\testS\\'
    pathO = 'E:\\work\\2020Correct\\data\\TM_ob_24h_648\\'
    pathM = 'E:\\work\\2020Correct\\data\\testM\\'
    pathS = 'E:\\work\\2020Correct\\data\\verificationResult_20\\'
    stationInfoFilePath = 'E:\\work\\2020Correct\\data\\StationInfo_648.txt'
    stDf = pd.read_csv(stationInfoFilePath,encoding='utf-8',sep=',',engine='python').set_index('Station_Num') #读取站点信息文件
###############################################################
    for eEle in element:
        for eQiBaoShiJian in qiBaoShiJian:
            listOfForcastDate = get_file_list(pathM,eQiBaoShiJian)
            correctVerification = get_correct_verification(pathO, pathM, eEle, listOfForcastDate,stDf)
            modelVerification = get_model_verification(pathO, pathM, eEle, listOfForcastDate, stDf)
            skillPointEVERYDAY = get_skill_point_EVERYDAY(correctVerification[0],modelVerification[0],eEle,listOfForcastDate,eQiBaoShiJian)
            skillPointEVERYSTATION = get_skill_point_EVERYSTATION(correctVerification[1], modelVerification[1],eEle,eQiBaoShiJian)
#########################################################
    print('DONE')



