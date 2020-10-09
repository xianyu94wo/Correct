import numpy as np
import os
import datetime
import shutil
import time
import meteva.base as meb
from GNT.get_now_time import GetNowTime
from FL.ftp_load import FtpLoad

np.set_printoptions(suppress=True)


def get_Tmost_array(listFileDst):
    global pathDst
    arZero = np.zeros((161, 274), dtype=float)
    arOne = np.ones((161, 274), dtype=float)
    arBase = np.array([arZero, arOne])
    for eFile in listFileDst:
        arTemp = np.loadtxt(pathDst + eFile, skiprows=3)
        print('已载入TMP_%s' % eFile)
        data1 = np.append(arBase, arTemp)
        dim1 = arBase.shape
        dataComb = data1.reshape(dim1[0] + 1, dim1[1], dim1[2])
        arBase = dataComb.copy()
    dataComb = np.delete(dataComb, [0, 1], axis=0)
    listmax = []
    listmin = []
    if dataComb.shape[0] > 21:
        print('正在处理最高/最低气温')
        for n in range(dataComb.shape[1]):
            for m in range(dataComb.shape[2]):
                aaa = np.max(dataComb[:, n, m])
                bbb = np.min(dataComb[:, n, m])
                listmax.append(aaa)
                listmin.append(bbb)
        TmaxArray = np.array(listmax).reshape(dataComb.shape[1], dataComb.shape[2])
        print('最高气温处理完毕')
        TminArray = np.array(listmin).reshape(dataComb.shape[1], dataComb.shape[2])
        print('最低气温处理完毕')
        return TmaxArray, TminArray


if __name__ == '__main__':
    pathFTPBase = '/GRAPES_3KM/TMP/2M_ABOVE_GROUND/'
    pathDstOrig = 'F:\\work\\2020Correct\\data\\TEM_md_1h_G3_Orig\\'
    pathSrc = 'K:\\GRAPES-3KM_to_5km\\GRAPES\\'
    pathDst = 'F:\\work\\2020Correct\\data\\TEM_md_1h_G3\\'
    pathRst = 'F:\\work\\2020Correct\\data\\TM_md_24h_G3\\'
    listEle = ['TMAX', 'TMIN']
    ftpHost = '10.181.27.199'
    ftpPort = 21
    ftpUsr = 'MicapsData'
    ftpPwd = 'MICAPS@#data321'
    timeStart = time.time()
    ###############历史回算#########################
    # for eday in range(21):
    #     timeStart = time.time()
    #     time1S = '2020091513'
    #     time1 = datetime.datetime.strptime(time1S, '%Y%m%d%H')
    #     time2 = time1 + datetime.timedelta(hours=12 * eday)
    #     time2S = time2.strftime('%Y%m%d%H')
    ###################获取时间对象######################
    getTimeOb = GetNowTime()
    #################如果当前时间大于12时，则拷贝早晨08起报的12-36，如果小于12时，则拷贝前一天20起报的12-36
    if int(getTimeOb.nowHour) < 12:
        qibaoshijian = getTimeOb.previousTimeS[2:-2] + '20'
    else:
        qibaoshijian = getTimeOb.qiBaoShiJian[2:-4] + '08'
    print(qibaoshijian)
    #######################确定拷贝文件夹和目标文件夹的文件名
    listFileDst = [getTimeOb.qiBaoShiJian[2:-2] + '.' + str(x).zfill(3) for x in range(1, 25)]
    listFileSrc = [qibaoshijian + '.' + str(x).zfill(3) for x in range(13, 37)]
    ################从FTP下载资料
    ftpOb = FtpLoad(ftpHost, ftpPort, ftpUsr, ftpPwd)
    ftpConnect = ftpOb.ftpConnet
    # fileList = ftpConnect.nlst('/20200915')
    # print(fileList)
    for eFile in listFileSrc:
        try:
            ftpOb.ftp_download(pathDstOrig + eFile, '/20' + qibaoshijian[:-2] + pathFTPBase + eFile)
            ########################插值切片
            grd = meb.read_griddata_from_micaps4(pathDstOrig + eFile)
            grid1 = meb.grid([89.3, 102.95, 0.05], [31.4, 39.4, 0.05])
            grd1 = meb.interp_gg_linear(grd, grid1)
            save_path = pathDstOrig + eFile
            meb.write_griddata_to_micaps4(grd1, save_path, effectiveNum=2)
        except Exception as downloadError:
            print(downloadError)
    # ##############拷贝##############
    try:
        for ee in range(len(listFileDst)):
            shutil.copy(pathDstOrig + listFileSrc[ee], pathDst + listFileDst[ee])
    except Exception as e:
        print(e)
    #######################选取最大最小值
    try:
        finalData = get_Tmost_array(listFileDst)
        ######################写成M4格式##################
        gridFileSaveName = '20' + qibaoshijian + '_'
        for ie, iv in enumerate(listEle):
            np.savetxt(pathRst + gridFileSaveName + iv + '.temp', finalData[ie], fmt='%.2f')
            with open(pathRst + gridFileSaveName + iv + '.temp') as f1:
                tempStr = f1.readlines()
            with open(pathRst + gridFileSaveName + iv + '.txt', 'w') as f2:
                f2.write('diamond 4 G3km_20%s_%s %s' % (gridFileSaveName[:-4], iv, '\n'))
                f2.write('20%s %s %s %s 24 0 %s' % (
                    gridFileSaveName[:-10], gridFileSaveName[2:4], gridFileSaveName[4:6], gridFileSaveName[6:8], '\n'))
                thirdLine = '0.05000 0.05000 89.3 102.95 31.4 39.4 274 161 10.000000 -40.000000 40.000000 5.000000 0.000000 '
                f2.write('%s %s' % (thirdLine, '\n'))

                f2.writelines(tempStr)
                os.remove(pathRst + gridFileSaveName + iv + '.temp')
    except Exception as aa:
        print(aa)
    timeCost = time.time() - timeStart
    print('【运行时间为%.2f秒】' % timeCost)
    print('DONE')
