#!/bin/python3
# Note, Jan = 00, Feb = 01, ...
#

import pandas as pd 
import so2daily as cv
import os
import smtplib
from email.message import EmailMessage
import datetime as dt
import re
import dateutil.relativedelta
from io import StringIO
class so2(object):
	def checker(self):
		ste = pd.read_csv("Site20201105114345683.txt", sep = "\t", usecols = ['AQS Code','Site Name','County'])
		ste.rename(columns = {'AQS Code':'airs', 'Site Name':'name', 'County':'county'}, inplace=True)
		today = (dt.date.today().strftime("%m-%d-%Y"))
		preDay = (dt.date.today()-dt.timedelta(days=1)).strftime("%m-%d-%Y")
		months ={"01":"00","02":"01","03":"02","04":"03","05":"04","06":"05",
		"07":"06","08":"07","09":"08","10":"09","11":"10","12":"11"}
		today = today.replace(today[0:2], months[today[0:2]],1)
		preDay = preDay.replace(preDay[0:2], months[preDay[0:2]],1)
		print(preDay,today)
		reg = [["AMARILLO","1"],["BEAUMONT","10"],["DFW", "4"], ["SAN", "13"], ["MID","7"], ["TYLER", "5"], ["WACO", "9"]]
#		reg = [["AMARILLO","1"]]
		dat = pd.DataFrame()
		for r in reg:
			ref = cv.Scrape(preDay, today, r[1], r[0])
			df = ref.loopMain()
			paramCode = re.compile(r'\s\d\d\d\d\d')
			for i in df:
				do = (i[0])
				do1 = str(do.string)
				try:
					parm = (paramCode.search(do1)).group()
				except AttributeError:
					os.system('echo "There is an error with pulling the data" |mail -s "SO2 High Days" robert.ramirez@tceq.texas.gov')
				else:
					do2 = pd.read_csv(StringIO(do), sep=',',skiprows=9,skip_blank_lines=True, na_filter=True)
					do2.dropna(how="any", inplace=True)
					do2["pol"]=parm.lstrip()
					do3 = pd.melt(do2,id_vars=['Date','pol'], var_name = 'airs')
					dat = pd.concat([dat,do3])
		dat.value = dat.value.apply(pd.to_numeric,errors='coerce')
		dat.airs = dat.airs.str.replace("_","").str[:9]
		wid = pd.pivot(dat,index=['airs','Date'], columns ='pol', values='value').reset_index()
#		 wid = dat.pivot(index=['airs','Date'], columns ='pol', values='value').reset_index()
		wid.rename(columns={"42401":'so2', "61103":"wspeed", "61104":"wdir"},inplace= True)
		wid.dropna(how="any", inplace=True)
		std=wid.loc[wid['so2'] > 75.4]
		if len(std) != 0:
			ste.airs = ste.airs.astype('str')
			tot = pd.merge(std,ste, how='left', on='airs')
			tot.Date = tot.Date.apply(lambda x: dt.datetime.strptime(x,'%Y%m%d%H%M%S'))
			contacts = ['Timothy.Janke@tceq.texas.gov','robert.ramirez@tceq.texas.gov','zhaohua.fang@tceq.texas.gov']
			x = tot.to_html(index=False)
			msg = EmailMessage()
			msg['Subject'] = 'These SO2 monitors had a high event'
			msg['From'] = 'roramire@storm.localdomain'
			msg['To'] = contacts
#			msg['To'] = 'robert.ramirez@tceq.texas.gov'
			
			msg.set_content(tot.to_string(header=True, col_space = 30, index=False))
			
			msg.add_alternative("""\
			{}
			""".format(x), subtype='html')
			s = smtplib.SMTP('localhost')
			s.send_message(msg)
		else:
			return None
if __name__ == "__main__":
	q = so2()
	q.checker()