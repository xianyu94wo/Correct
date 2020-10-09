import ftplib


class FtpLoad(object):

    def __init__(self, host, port, username, passwd):
        self.host = host
        self.port = port
        self.username = username
        self.passwd = passwd
        self.ftpConnet = self.ftp_connect()


    def ftp_connect(self):
        '''
        连接FTP
        :param host: FTP地址
        :param port: FTP端口
        :param username: FTP用户名
        :param passwd: FTP密码
        :return: 返回ftp对象
        '''
        ftp = ftplib.FTP()
        try:
            ftp.connect(self.host, self.port)
        except:
            raise IOError("FTP服务器连接失败")
        try:
            ftp.login(self.username, self.passwd)
        except:
            raise IOError("FTP用户名或密码错误")
        else:
            print("FTP连接登录成功")
            return ftp


    def ftp_upload(self, localFilePath, ftpFilePath):
        file_handler = open(localFilePath, 'rb')
        self.ftpConnet.encoding = 'utf-8'
        self.ftpConnet.storbinary('STOR %s' % ftpFilePath, file_handler)
        file_handler.close()
        print('【本地文件{}已成功上传，上传至{}】'.format(localFilePath, ftpFilePath))


    def ftp_download(self, localFilePath, ftpFilePath):
        file_handler = open(localFilePath, 'wb').write
        self.ftpConnet.encoding = 'utf-8'
        self.ftpConnet.retrbinary('RETR %s' % ftpFilePath, file_handler)
        # file_handler.close()
        print('【%s已下载完成】' % localFilePath)

    def print_all_attribute_of_object(self):
        print('\n'.join(['%s:%s' % item for item in self.__dict__.items()]))

if __name__ == '__main__':
    ftpHost = '10.181.9.154'
    ftpPort = 21
    ftpUsr = 'ysj'
    ftpPwd = 'Ysj8894315'


    ob1 = FtpLoad(ftpHost, ftpPort, ftpUsr, ftpPwd)

    ob1.ftp_upload( 'F:\\work\\2.txt', '4.txt')
    ob1.ftp_download('F:\\work\\4.txt', '4.txt')

    #ftp_upload(ftp1, 'F:\\work\\2.txt', '3.txt')

#
