import os
import datetime
import shutil


def get_now_time_GB(nowBJTStr):
    print(nowBJTStr)
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    if nowHour >= 8 and nowHour < 20:
        nowTimeStr = nowBJTStr[:-2] + '08'
        timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
        previousTime = timeTemp - datetime.timedelta(days=1)
        previousBeforeTime = timeTemp - datetime.timedelta(days=2)
        previousTimeS = previousTime.strftime('%Y%m%d%H')
        previousBeforeTimeS = previousBeforeTime.strftime('%Y%m%d%H')
        return nowTimeStr, previousTimeS, previousBeforeTimeS
    elif nowHour >= 20 or nowHour < 8:
        nowTimeStr = nowBJTStr[:-2] + '20'
        timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
        previousTime = timeTemp - datetime.timedelta(days=1)
        previousBeforeTime = timeTemp - datetime.timedelta(days=2)
        previousTimeS = previousTime.strftime('%Y%m%d%H')
        previousBeforeTimeS = previousBeforeTime.strftime('%Y%m%d%H')
        return nowTimeStr, previousTimeS, previousBeforeTimeS


def check_data(pathG, nowBJTStr, element, pathS):
    timeStr = get_now_time_GB(nowBJTStr)

    if os.path.exists(pathG + timeStr[0][:4] + '\\' + timeStr[0][:-2] + '\\' + element + '_' + timeStr[0] + '.024'):
        gridDataPath = pathG + timeStr[0][:4] + '\\' + timeStr[0][:-2] + '\\' + element + '_' + timeStr[0] + '.024'
        savePath = pathS + timeStr[0] + '_' + element  + '.txt'
        shutil.copyfile(gridDataPath, savePath)
        print('【当前%s指导预报存在，已完成拷贝】'%timeStr[0])
    elif os.path.exists(pathG + timeStr[1][:4] + '\\' + timeStr[1][:-2] + '\\' + element + '_' + timeStr[1] + '.048'):
        gridDataPath = pathG + timeStr[1][:4] + '\\' + timeStr[1][:-2] + '\\' + element + '_' + timeStr[1]+ '.048'
        savePath = pathS + timeStr[0] + '_' + element  + '.txt'
        shutil.copyfile(gridDataPath, savePath)
        print('【当前%s指导预报不存在，已完成拷贝前一天%s指导预报拷贝】' % (timeStr[0],timeStr[1]))

    elif os.path.exists(pathG + timeStr[2][:4] + '\\' + timeStr[2][:-2] + '\\' + element + '_' + timeStr[2]+ '.072'):
        gridDataPath = pathG + timeStr[2][:4] + '\\' + timeStr[2][:-2] + '\\' + element + '_' + timeStr[2] + '.072'
        savePath = pathS + timeStr[0] + '_' + element  + '.txt'
        shutil.copyfile(gridDataPath, savePath)
        print('【今日、昨日指导预报不存在，已完成拷贝%s指导预报拷贝】' % timeStr[2])
    else:
        print('近三个时次无资料')



def get_now_time():
    nowBJT = datetime.datetime.today()
    nowBJTStr = nowBJT.strftime('%Y%m%d%H')
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    listTime = []
    if nowHour >= 8 and nowHour < 20:
        timeTemp = nowBJTStr[:-2] + '08'
        saveTimet = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
        saveTime = saveTimet - datetime.timedelta(days=1)
        saveTimeStr = saveTime.strftime('%Y%m%d%H')
        for eHour in range(24):
            getTime = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
            getTime = getTime - datetime.timedelta(hours=eHour)
            getTimeStr = getTime.strftime('%Y%m%d%H')
            listTime.append(getTimeStr)
    elif nowHour >= 20:
        timeTemp = nowBJTStr[:-2] + '20'
        saveTimet = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
        saveTime = saveTimet - datetime.timedelta(days=1)
        saveTimeStr = saveTime.strftime('%Y%m%d%H')
        for eHour in range(24):
            getTime = datetime.datetime.strptime(timeTemp, '%Y%m%d%H')
            getTime = getTime - datetime.timedelta(hours=eHour)
            getTimeStr = getTime.strftime('%Y%m%d%H')
            listTime.append(getTimeStr)
    return saveTimeStr, listTime


if __name__ == '__main__':
    timeStr = '2020092511'
    pathG = 'E:\\work\\2020Correct\\data\\GRID\\'
    pathS = 'E:\\work\\2020Correct\\data\\TM_md_24h_Grid\\'
    element = ['TMAX','TMIN']
    for days in range(4):
        getTime1 = datetime.datetime.strptime(timeStr, '%Y%m%d%H')
        getTime1 = getTime1 + datetime.timedelta(hours=12 * days)
        getTimeStrF = getTime1.strftime('%Y%m%d%H')

        for eEle in element:
            aa = check_data(pathG,getTimeStrF, eEle, pathS)
            print(aa)
