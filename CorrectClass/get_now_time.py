import datetime


class GetNowTime(object):

    def __init__(self, nowBJTStr=datetime.datetime.today().strftime('%Y%m%d%H')):
        self.nowBJTStr = nowBJTStr
        self.nowBJT = datetime.datetime.strptime(self.nowBJTStr, '%Y%m%d%H')
        self.nowUTC = self.nowBJT - datetime.timedelta(hours=8)
        self.nowUTCStr = self.nowUTC.strftime('%Y%m%d%H')
        self.nowHour = int(nowBJTStr[-2:])
        self.qiBaoShiJian = self.get_now_time()[0]
        self.nowTimeStr = self.get_now_time()[1]
        self.nowTimeStrUTC = (datetime.datetime.strptime(self.nowTimeStr, '%Y%m%d%H') - datetime.timedelta(hours=8)).strftime('%Y%m%d%H')
        self.previousTimeS = self.get_now_time()[2]
        self.previousTimeSUTC = (datetime.datetime.strptime(self.previousTimeS, '%Y%m%d%H') - datetime.timedelta(hours=8)).strftime('%Y%m%d%H')
        self.previousBeforeTimeS = self.get_now_time()[3]

    def get_now_time(self):
        if self.nowHour < 13:
            qiBaoShiJian = self.nowBJTStr[:-2] + '0800'
            nowTimeStr = self.nowBJTStr[:-2] + '08'
            timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
            previousTime = timeTemp - datetime.timedelta(days=1)
            previousBeforeTime = timeTemp - datetime.timedelta(days=2)
            previousTimeS = previousTime.strftime('%Y%m%d%H')
            previousBeforeTimeS = previousBeforeTime.strftime('%Y%m%d%H')
            return qiBaoShiJian, nowTimeStr, previousTimeS, previousBeforeTimeS
        else:
            qiBaoShiJian = self.nowBJTStr[:-2] + '2000'
            nowTimeStr = self.nowBJTStr[:-2] + '20'
            timeTemp = datetime.datetime.strptime(nowTimeStr, '%Y%m%d%H')
            previousTime = timeTemp - datetime.timedelta(days=1)
            previousBeforeTime = timeTemp - datetime.timedelta(days=2)
            previousTimeS = previousTime.strftime('%Y%m%d%H')
            previousBeforeTimeS = previousBeforeTime.strftime('%Y%m%d%H')
            return qiBaoShiJian, nowTimeStr, previousTimeS, previousBeforeTimeS

    def print_all_attribute_of_object(self):
        print('\n'.join(['%s:%s' % item for item in self.__dict__.items()]))


if __name__ == '__main__':
    ob1 = GetNowTime()
    print(type(ob1.qiBaoShiJian))
    ob1.all_attribute_of_object()
