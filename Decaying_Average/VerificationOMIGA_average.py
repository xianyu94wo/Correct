import pandas as pd
import numpy as np
import os
import datetime
import time
from collections import Counter

np.set_printoptions(suppress=True)


def mkdir_dir_and_ormiga():
    path1 = 'F:\\work\\2020Correct\\data\\DA\\'
    listOmiga = ['{:.3f}'.format(0.005 * x) for x in range(1, 200)]
    list2 = [path1 + x for x in listOmiga]
    # for i in list2:
    #     os.makedirs(i)
    return listOmiga


if __name__ == '__main__':
    pathResult = 'F:\\work\\2020Correct\\data\\verificationDA\\'
    pathResultSave = 'F:\\work\\2020Correct\\data\\'
    listElement = ['TMAX', 'TMIN']
    # listElement = ['TMIN']
    rateStr = 'listRateForALL'
    skillStr = 'listSkilleDayforALL'
    # print(SlidingStep)

    ####################################
    listAllStep = mkdir_dir_and_ormiga()
    print(listAllStep)
    #
    for eEle in listElement:
        listRateResult, listSkillResult = [], []
        for eStep in listAllStep:
            pathTemp = pathResult + eStep + '\\'
            listFile = os.listdir(pathTemp)
            for eFile in listFile:
                aa = eFile.split('_')
                if aa[0] == rateStr and aa[-1][:-4] == eEle and aa[1][-2:] == '20':
                    print(eStep, eFile)
                    dfTemp = pd.read_csv(pathResult + eStep + '\\' + eFile, index_col=0)['FC']

                    aveRateResult = dfTemp.mean(axis=0)
                    listRateResult.append(aveRateResult)
                if aa[0] == skillStr and aa[-1][:-4] == eEle and aa[1][-2:] == '20':
                    dfTemp2 = pd.read_csv(pathResult + eStep + '\\' + eFile, index_col=0)['Skill']
                    # print(dfTemp2)
                    aveSkillResult = dfTemp2.mean(axis=0)
                    listSkillResult.append(aveSkillResult)
        dfRateResult = pd.DataFrame(listRateResult, index=listAllStep)
        dfRateResult.to_csv(pathResultSave + 'FinalRateResult_' + eEle + '_20.txt', sep=',', float_format='%.4f')
        dfSkillResult = pd.DataFrame(listSkillResult, index=listAllStep)
        dfSkillResult.to_csv(pathResultSave + 'FinalSkillResult_' + eEle + '_20.txt', sep=',', float_format='%.4f')

    print('DONE')
