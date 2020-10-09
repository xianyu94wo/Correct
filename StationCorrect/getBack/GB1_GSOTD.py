from urllib import request
from urllib.request import urlopen
import datetime

#GSOTD是GetStationOb1hTemData的缩写,GB为回补
def get_back_time(duringHours):
    startTimeStr = '2020092600'
    startTime = datetime.datetime.strptime(startTimeStr, '%Y%m%d%H')
    deltaHours = int(duringHours)
    deltaTime = datetime.timedelta(hours=deltaHours)
    nowUTC = startTime + deltaTime
    nowUTCStr = nowUTC.strftime('%Y%m%d%H')
    return nowUTCStr

if __name__ == '__main__':
    savePath = 'F:\\work\\2020Correct\\data\\TEM_ob_1h_648\\'
    stationIDFilePath = 'E:\\data\\station\\ALL223_Num_648.txt'
    for eHours in range(3 * 24):# 此处为小时
        nowUTCstr = get_back_time(eHours)
        print(nowUTCstr)
        with open(stationIDFilePath,encoding='utf-8') as f1:
            listSta = f1.readlines()
        with open(savePath + nowUTCstr + '.txt', 'w') as f2:
            baseUrl = 'http://10.181.89.55/cimiss-web/api?userId=BEXN_QXT_Yousangjie&pwd=Ysj8894315&' \
                       'interfaceId=getSurfEleByTimeAndStaID&dataCode=SURF_CHN_MUL_HOR&' \
                       'elements=Station_Id_C,Lat,Lon,Year,Mon,Day,Hour,TEM&' \
                       'times=' + nowUTCstr + '0000&staIds=' + listSta[0].strip('\n') + '&dataFormat=text'
            req = request.Request(baseUrl)
            print(baseUrl)
            response = urlopen(req).read().decode("utf-8")
            f2.write(response.strip('\n'))
    print('Done!')



