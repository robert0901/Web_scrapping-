#
# LEADS data scraper:
#	Scrapes data from LEADS/Data Extractor.	 Queries which ever parameters are listed in the MET_O3_parameterCodes.txt file.
#	Note that not all parameter will be present.  This code will create a subfolder in the current
#	folder, named MET_O3.  There you will find one file per paramater with the format of 
#		'some-user-provide-prefix'_out_'paramater-code'.csv
#	example:
#		TEST_out_43212.csv
#
#  This can be stand alone, but for better perfomance use ZENO_looper.py
#
import cgi
import requests					# use pip install request
from bs4 import BeautifulSoup	# use pip install bs4
import os
import errno
import sys

class Scrape(object):

	def __init__(self, sdate, edate, region, prefix,out):
		'''
		USER CHANGE PARAMETERS HERE......
	   
		Remember that the month is numeric but note, Jan = 0, Feb = 1, ..., Dec = 11
		dates  are in the form of '05-09-2019'
		regions are TCEQ regions Austin=11, Houston=12, DFW=4, ELP=6, SAN=13, BPA=10, Corpus Christi=11 ...
		Any questions, ask Fernando.
		'''
		self.sdate = sdate	 #'01-01-2017'		 # start date
		self.edate = edate	 #'04-30-2020'		 # end date
		self.region = region #'10'				# tceq region
		self.prefix = prefix #"BPA"			# user provided prefix
		self.directory = out
		
		self.codesFile = 'so2daily.txt'
		
		
		self.dataSource = 'z'							# do not change - data source: autogc = g, zeno = z		 
		self.polcodes = self.readCodes(self.codesFile)	# do not change
		self.curpath = os.getcwd()						# do not change
		print("- CURRENT PATH:", self.curpath)
		


	def readCodes(self, codes):
		parameterNames = codes
		print("- USING PARAMETER FILE:", parameterNames)
		parms = []
		fh = open("../params/" + parameterNames, "r")
		# _ = fh.readline()
		while True:
			line = fh.readline().rstrip()
			if line == "": break
			parname, parcode = line.split("\t")
			# print(parname, parcode)
			parms.append(parcode)
		fh.close() 
		print("- OBS IN PARM FILE:", len(parms))
		return(parms)		 
			
	def data(self, url, ZenoParm, sdate, edate, region, DataSource = 'z'): ###
			include_type = ['CAMS','TAMS','UT','VICTORIA','DALLAS','FTWORTH','HOUSTON',\
			'HARRIS_CNTY','ELPASO','SETRPC','HRM','CPS','ASOS','CAPCOG','PRIVATE_INDUSTRY',\
			'PRIVATE_OTHER']

			smonth, sday, syear	 = sdate.split('-')
			emonth, eday, eyear = edate.split('-')
			
			# for the data extractor
			payload = {
			'select_date'			:'r', # r is for date range, m = month, q = quarter, y = year, u = months within a year range
			'start_month'			:1,
			'start_year'			:2015,
			'quarter'				:1,
			'quarter_year'			:2015,
			'single_year'			:2015,
			'start_month1'			:int(smonth), ### for r date range
			'start_day1'			:int(sday), ### for r date range
			'start_year1'			:int(syear), ### for r date range
			'end_month1'			:int(emonth), ### for r date range
			'end_day1'				:int(eday), ### for r date range
			'end_year1'				:int(eyear), ### for r date range
			'start_year2'			:2015,
			'end_year2'				:2015,
			'source'				:DataSource,	#Datalogger parameter. g = gsc parameter and datalogger = z.
			'zeno_param'			:ZenoParm,			#Parameter (pollutant, wind, etc)
			'agc_param'				:'',
			'database'				:'1h', # 1h for one hour increments, 5m for 5-min increments
			'output_device'			:'w',
			'output_file'			:'none',
			'overwrite'				:'u',
			'email_address'			:'none',
			'create_config'			:'c',
			'config_file'			:'none',
			'config_overwrite'		:'u',
			'select_format'			:'g',
			'select_location'		:'r',			#Selecting by specific site. r = region, s = site, c = city
			'cams_crit'				:12,
			'reg_crit'				:region,				# 11 = austin
			'include_type'			:include_type,
			'time'					:'l',
			'decimals'				:2,
			'truncate'				:'t',
			'date_format'			:'iso',
			'time_format'			:'iso',
			'data_flag'				:'f',			#shows as flag only (CAL, NOL, etc)
			'co_units'				:'m',			#ppm
			'agc_units'				:'c',			#ppb Carbon
			'water_interval'		:15,			#15 min raw samples only
			'delimiter'				:'c',			#c - commas. s - spaces.
			'spaces'				:8,
			'align'					:'r',
			'sort_order'			:'c',
			'site_id'				:'e',
			'param_id'				:'n'			#Do not include paramater identifier
			}
			return requests.get(url, params=payload)

	def writeOut(self, fname, ds):
			'''write final to file'''
			fh = open(fname, 'w')
			for i in ds:
				fh.write(i + "\n" )
			fh.close()

	def main(self, pol, sdate, edate, region, prefix, dataSource):			  
		url =  "http://rhone/cgi-bin/data_extract.pl"
		cont = []
		d = self.data(url, pol, sdate, edate, region, dataSource)
		# bs  below
		soup = BeautifulSoup(d.text, 'html.parser')
		pres = soup.find('pre')
		try:
			cont = pres.contents
		except:
			print("! No data")
			print(len(cont))
		# print(cont)	
		outname = "../" + self.directory + "/" + str(prefix) + "_out_" + str(pol) + ".csv" 
		self.writeOut(outname, cont)
		cont.clear()        
#		return(cont)
			
	def loopMain(self):
		count = 1
		dat=[]
		for pc in self.polcodes: 
			# print(str(count) + ".", pc)
#			print("{0:2}. {1:10}".format(count, pc))
			df = self.main(pc, self.sdate, self.edate, self.region, self.prefix, self.dataSource)
			dat.append (df)
			count += 1
		# print(df)
		return(dat)
		
		
if __name__ == '__main__':
	ref = Scrape('09-19-2020', '09-20-2020', '7', 'DGB',"so2_folder")
	ref.loopMain()
	