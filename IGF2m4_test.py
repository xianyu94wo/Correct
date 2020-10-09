import os
import numpy as np
import datetime
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
#定义昨天日期函数
def getYesterday():
	today = datetime.date.today()
	oneday = datetime.timedelta(days=1)
	yesterday = today - oneday
	return yesterday
#判断是否过12点，如果没有则日期为前一天，如果有，则为本日
hour_now = datetime.datetime.now().hour
if hour_now >= 12:
	date_today1 = datetime.datetime.strftime(datetime.date.today(),'%Y%m%d')
else:
	date_today1 = datetime.datetime.strftime(getYesterday(),'%Y%m%d')
if hour_now >= 12:
	date_today2 = datetime.datetime.strftime(datetime.date.today(),'%y%m%d')
else:
	date_today2 = datetime.datetime.strftime(getYesterday(),'%y%m%d')
#打开当日文件夹
rootdir = "I:\\data\\IGF\\IGFdata\\"
filename1 = date_today1
filename2 = rootdir + filename1
filename3 = "I:\\data\\IGF\\temp\\"
filename4 = "I:\\data\\IGF\\IGF2M4\\"
#列出文件夹下所有的目录与文件并筛选出08或20
list_dir = os.listdir(filename2)
name_of_data_list = []
for i in range(0,len(list_dir)):
	list_of_data = str(list_dir[i])
	time_step = list_of_data.split("_")[8][-4:-2]
#判断08或20点资料
	if hour_now <= 12:
		if time_step == '20':
			name_of_data_list.append(list_of_data)
	else:
		if time_step == '08':
			name_of_data_list.append(list_of_data)
for i in range(0,len(name_of_data_list)):
	name_of_data = name_of_data_list[i]
	element_name = name_of_data.split("_")[7].split("-")[1]#获取要素名称
	m4_data_dirname = filename3+str(element_name)+"\\"
	os.chdir("D:\\Program Files (x86)\\opengrads\\Contents\\Cygwin\\Versions\\2.1.a2.oga.1\\i686\\")
	data_path = "wgrib2 "+filename2+"\\"+name_of_data+" -v"#os.system中wgrib需要的资料路径
	os.system(str(data_path))
#获取文件时效及预报步长
	step_of_data = name_of_data[-7:-5]
	period_of_data = name_of_data[-10:-7]
	step_number = int(int(period_of_data)/int(step_of_data))

#转grib2至txt文件
	for step in range(1,step_number+1):
		n_step_number = step
		n_step_of_data = int(step_of_data)*step
		if hour_now >= 16:
			execute_data_name = date_today2+"20."+str(n_step_of_data).zfill(3)
		else:
			execute_data_name = date_today2+"08."+str(n_step_of_data).zfill(3)
		execute_path = "wgrib2 "+filename2+"\\"+name_of_data+" -d "+"1."+str(n_step_number)+" -no_header -text "+m4_data_dirname+str(execute_data_name)
		print('*'*50)
		print(execute_path)
		print('*' * 50)
		os.system(execute_path)

#将转成功后的txt文件转为矩阵
list_dir_of_elements = os.listdir(filename3)
for i in range(0,len(list_dir_of_elements)):
	file_of_elements_temp = str(list_dir_of_elements[i])
	list_dir_of_elements_temp = os.listdir(filename3+file_of_elements_temp+"\\")
	for j in range(0,len(list_dir_of_elements_temp)):
		name_of_elements_temp = str(list_dir_of_elements_temp[j])
		file_array_temp = open(filename3+file_of_elements_temp+"\\"+name_of_elements_temp,"r")
		grids = file_array_temp.read().strip()
		grids = grids.split("\n")
		element_array = np.array(grids)
		element_array.resize(161,274)
		element_array =element_array.astype(float)
		if file_of_elements_temp == "ER03":			
			np.savetxt(filename4+file_of_elements_temp+"\\"+name_of_elements_temp, element_array, fmt = '%.1f')
		else:
			np.savetxt(filename4+file_of_elements_temp+"\\"+name_of_elements_temp, element_array-273.15, fmt = '%.1f')
		file_array_temp.close()
#写入文件表头
list_dir_of_elements = os.listdir(filename4)
for i in range(0,len(list_dir_of_elements)):
	file_of_elements_temp = str(list_dir_of_elements[i])
	list_dir_of_elements_temp = os.listdir(filename4+file_of_elements_temp+"\\")
	for j in range(0,len(list_dir_of_elements_temp)):		
		time_step_end = int(str(list_dir_of_elements_temp[j][-3:]))
		if hour_now >= 12:
			if file_of_elements_temp == "TMP":
				explain = date_today2 + "20"+"("+str(time_step_end).zfill(3)+")" + "青海智能网格逐3小时气温(℃)预报"
				biaotou3 = "0.05000 0.05000 89.300000 102.95000 31.400000 39.400000 274 161 5.000000 -20.000000 40.00000 1.000000 0.000000 \n"
			elif file_of_elements_temp == "ER03":
				explain = date_today2 + "20"+"("+str(time_step_end).zfill(3)+")" + "青海智能网格逐3小时降水(mm)预报"
				biaotou3 = "0.05000 0.05000 89.300000 102.95000 31.400000 39.400000 274 161 5.000000 0.000000 200.00000 1.000000 0.000000 \n"
			elif file_of_elements_temp == "TMAX":
				explain = date_today2 + "20"+"("+str(time_step_end).zfill(3)+")" + "青海智能网格24小时最高气温(℃)预报"
				biaotou3 = "0.05000 0.05000 89.300000 102.95000 31.400000 39.400000 274 161 5.000000 -20.000000 40.00000 1.000000 0.000000 \n"
			elif file_of_elements_temp == "TMIN":
				explain = date_today2 + "20"+"("+str(time_step_end).zfill(3)+")" + "青海智能网格24小时最低气温(℃)预报"
				biaotou3 = "0.05000 0.05000 89.300000 102.95000 31.400000 39.400000 274 161 5.000000 -20.000000 40.00000 1.000000 0.000000 \n"
			biaotou1 = "diamond 4 " + explain + "\n"
			biaotou2 = date_today1[:4] + " " + date_today1[4:6] + " " + date_today1[-2:] + " 20 " + str(time_step_end) + " 0" + "\n"			
		else:
			if file_of_elements_temp == "TMP":
				explain = date_today2 + "08"+"("+str(time_step_end).zfill(3)+")" + "青海智能网格逐3小时气温(℃)预报"
				biaotou3 = "0.05000 0.05000 89.300000 102.95000 31.400000 39.400000 274 161 5.000000 -20.000000 40.00000 1.000000 0.000000 \n"
			elif file_of_elements_temp == "ER03":
				explain = date_today2 + "08"+"("+str(time_step_end).zfill(3)+")" + "青海智能网格逐3小时降水(mm)预报"
				biaotou3 = "0.05000 0.05000 89.300000 102.95000 31.400000 39.400000 274 161 5.000000 0.000000 200.00000 1.000000 0.000000 \n"
			elif file_of_elements_temp == "TMAX":
				explain = date_today2 + "08"+"("+str(time_step_end).zfill(3)+")" + "青海智能网格24小时最高气温(℃)预报"
				biaotou3 = "0.05000 0.05000 89.300000 102.95000 31.400000 39.400000 274 161 5.000000 -20.000000 40.00000 1.000000 0.000000 \n"
			elif file_of_elements_temp == "TMIN":
				explain = date_today2 + "08"+"("+str(time_step_end).zfill(3)+")" + "青海智能网格24小时最低气温(℃)预报"
				biaotou3 = "0.05000 0.05000 89.300000 102.95000 31.400000 39.400000 274 161 5.000000 -20.000000 40.00000 1.000000 0.000000 \n"
			biaotou1 = "diamond 4 " + explain + "\n"
			biaotou2 = date_today1[:4] + " " + date_today1[4:6] + " " + date_today1[-2:] + " 08 " + str(time_step_end) + " 0" + "\n"
		element_temp_file = open(filename4 + file_of_elements_temp + "\\" + list_dir_of_elements_temp[j],"r+")
		old = element_temp_file.read()
		element_temp_file.seek(0)
		element_temp_file.write(biaotou1)
		element_temp_file.write(biaotou2)
		element_temp_file.write(biaotou3)
		element_temp_file.write(old)
		element_temp_file.close()





'''
olat = np.linspace(31.4,39.4,161)
olon = np.linspace(89.3,103.0,274)
olon,olat = np.meshgrid(olon,olat)
level = np.arange(0,25,1)
m = Basemap(projection='merc',llcrnrlat=31.4,llcrnrlon=89.3,urcrnrlat=39.4,urcrnrlon=103.0)
m.readshapefile('I:\\data\\SHP\\xingzhengquhua_shp\\dijishi_2004','dijishi_2004.shp', linewidth=1, color='k')
x,y = m(olon,olat)
cf = m.contourf(x, y, element_array-273.15,levels=level)
plt.show()
'''


print('Done!')