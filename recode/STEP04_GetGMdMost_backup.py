import os
import datetime
import shutil


def get_now_time():
    nowBJT = datetime.datetime.today()
    nowBJTStr = nowBJT.strftime('%Y%m%d%H')
    nowHour = int(nowBJTStr[-2:])  # 字符串中获取小时并转为整数
    if nowHour <= 13:
        nowTimeStr = nowBJTStr[:-2] + '08'
        timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
        previousTime = timeTemp - datetime.timedelta(days=1)
        previousBeforeTime = timeTemp - datetime.timedelta(days=2)
        previousTimeS = previousTime.strftime('%Y%m%d%H')
        previousBeforeTimeS = previousBeforeTime.strftime('%Y%m%d%H')
        return nowTimeStr, previousTimeS, previousBeforeTimeS
    else:
        nowTimeStr = nowBJTStr[:-2] + '20'
        timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
        previousTime = timeTemp - datetime.timedelta(days=1)
        previousBeforeTime = timeTemp - datetime.timedelta(days=2)
        previousTimeS = previousTime.strftime('%Y%m%d%H')
        previousBeforeTimeS = previousBeforeTime.strftime('%Y%m%d%H')
        return nowTimeStr, previousTimeS, previousBeforeTimeS


def check_data(pathG, element, pathS):
    timeStr = get_now_time()
    print(timeStr)

    if os.path.exists(pathG + timeStr[0][:4] + '\\' + timeStr[0][:-2] + '\\' + element + '_' + timeStr[0] + '.024'):
        gridDataPath = pathG + timeStr[0][:4] + '\\' + timeStr[0][:-2] + '\\' + element + '_' + timeStr[0] + '.024'
        savePath = pathS + timeStr[0] + '_' + element + '.txt'
        shutil.copyfile(gridDataPath, savePath)
        print('【当前%s指导预报存在，已完成拷贝】' % timeStr[0])
    elif os.path.exists(pathG + timeStr[1][:4] + '\\' + timeStr[1][:-2] + '\\' + element + '_' + timeStr[1] + '.048'):
        gridDataPath = pathG + timeStr[1][:4] + '\\' + timeStr[1][:-2] + '\\' + element + '_' + timeStr[1] + '.048'
        savePath = pathS + timeStr[0] + '_' + element + '.txt'
        shutil.copyfile(gridDataPath, savePath)
        print('【当前%s指导预报不存在，已完成拷贝前一天%s指导预报拷贝】' % (timeStr[0], timeStr[1]))

    elif os.path.exists(pathG + timeStr[2][:4] + '\\' + timeStr[2][:-2] + '\\' + element + '_' + timeStr[2] + '.072'):
        gridDataPath = pathG + timeStr[2][:4] + '\\' + timeStr[2][:-2] + '\\' + element + '_' + timeStr[2] + '.072'
        savePath = pathS + timeStr[0] + '_' + element + '.txt'
        shutil.copyfile(gridDataPath, savePath)
        print('【今日、昨日指导预报不存在，已完成拷贝%s指导预报拷贝】' % timeStr[2])
    else:
        print('近三个时次无资料')


if __name__ == '__main__':
    print('【开始运行获取实况最高最低气温筛选程序】')
    pathG = 'F:\\work\\2020Correct\\data\\GRID\\'
    pathS = 'F:\\work\\2020Correct\\data\\TM_md_24h_Grid\\'
    element = ['TMAX', 'TMIN']
    for eEle in element:
        aa = check_data(pathG, eEle, pathS)
