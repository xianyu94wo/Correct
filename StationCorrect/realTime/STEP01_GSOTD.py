from urllib import request
from urllib.request import urlopen
import datetime
import sys
sys.path.append('E:\\workspace\\work\\Correct\\CorrectClass\\')
from get_now_time import GetNowTime
#GSOTD是GetStationOb1hTemData的缩写

if __name__ == '__main__':




    getTimeOb = GetNowTime()
    nowBJT = datetime.datetime.strptime(getTimeOb.nowBJTStr,'%Y%m%d%H')
    nowUTC = nowBJT - datetime.timedelta(hours=8)
    nowUTCStr = nowUTC.strftime('%Y%m%d%H')
    print('【当前世界时为%s】'%nowUTCStr)
    saveStationDataPath = 'E:\\work\\2020Correct\\data\\TEM_ob_1h_648\\'
    stationIDFilePath = 'E:\\data\\station\\ALL223_Num_648.txt'
    with open(stationIDFilePath,encoding='utf-8') as f1:
        listSta = f1.readlines()
    with open(saveStationDataPath + nowUTCStr + '.txt', 'w') as f2:
        baseUrl = 'http://10.181.89.55/cimiss-web/api?userId=BEXN_QXT_Yousangjie&pwd=Ysj8894315&' \
                   'interfaceId=getSurfEleByTimeAndStaID&dataCode=SURF_CHN_MUL_HOR&' \
                   'elements=Station_Id_C,Lat,Lon,Year,Mon,Day,Hour,TEM&' \
                   'times=' + nowUTCStr + '0000&staIds=' + listSta[0].strip('\n') + '&dataFormat=text'
        req = request.Request(baseUrl)
        print(baseUrl)
        response = urlopen(req).read().decode("utf-8")
        f2.write(response.strip('\n'))
    # print('Done!')



