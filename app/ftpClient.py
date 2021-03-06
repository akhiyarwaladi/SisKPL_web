from ftplib import FTP
import os
from datetime import datetime
from redis import StrictRedis
import shutil
import config
import smtpEmail as se
import time

redis = StrictRedis(host=config.REDIS_HOST)	
def downloadFile(liScene):
	boolScene = False
	msg = str(datetime.now()) + '\t' + "Downloading data ... \n"
	redis.rpush(config.MESSAGES_KEY, msg)
	redis.publish(config.CHANNEL_NAME, msg)
	boolScene = False
	# liscene adalah list yang sudah selesai diproses
	print "Sudah diproses " + str(liScene)
	# ambil informasi tanggal hari ini
	tupDate = datetime.now()
	print tupDate.year
	print tupDate.strftime('%j')
	#print now.year, now.month, now.day, now.hour, now.minute, now.second # check every datetime detail
	ftp = FTP( )
	# buka koneksi baru ke ftp
	try:
	    ftp.connect(host=config.ftpHost, port=21, timeout=123456)
	except:
	    se.kirimEmail("Terjadi kesalahan pada FTP server. Aplikasi tidak dapat terhubung ke server FTP. Mohon Perbaiki FTP server dan restart sistem otomatisasi")

	try:
		ftp.login(user=config.ftpUser, passwd=config.ftpPaswd)
		ftp.cwd('L8_REFLECTANCE_MS')
		# year = '2015'
		# ftp.cwd(year)
		folderTahun = ftp.nlst()

		month = '2017_23'
		#month = folderTahun[-1]
		ftp.cwd(month)
		folderTerbaru = ftp.nlst()

		while (len(folderTerbaru) == 0):
			print ("Belum ada data di dalam folder terbaru ("+month+")") 
			se.kirimEmail("Belum ada data di dalam folder terbaru ("+month+")")
			time.sleep(60)
			ftp = FTP( )
			# buka koneksi baru ke ftp
			ftp.connect(host=config.ftpHost, port=21, timeout=123456)
			ftp.login(user=config.ftpUser, passwd=config.ftpPaswd)
			ftp.cwd('L8_REFLECTANCE_MS')
			ftp.cwd(year)
			ftp.cwd(month)

			folderHari = ftp.nlst()

		for scene in folderTerbaru:
			print scene
			
			# jika scene termasuk kedalam list yang telah diproses
			if scene in liScene:
				print "scene " + str(scene) + " sudah diproses"
				# lanjut lihat folder scene yang lainnya
				continue;
			# jika tidak termasuk maka set boolean bahwa ada data yang akan diproses
			
			ftp.cwd(scene)
			fileScene = ftp.nlst()
			# jika data pada folder belum lengkap
			if (len(fileScene) != 16):
				print "scene" + str(scene) + " data belum lengkap"
				# lanjut lihat folder scene yang lainnya
				continue;

			boolScene = True
			fileScene = ftp.nlst()
			# ambil file status cloud masking
			mtl = [mt for mt in fileScene if '_geo_cm_stat.txt' in mt]
			# download terlebih dahulu file cloud masking
			localfile = open(mtl[0], 'wb')
			ftp.retrbinary('RETR ' + mtl[0], localfile.write, 1024)
			localfile.close()
			# baca file txt dengan format tupple, hasil akan ditampilkan perbaris (line)
			lines = tuple(open(mtl[0], 'r'))
			# ambil baris ke 16 (awan di darat), valuenya ada di belakang kedua dari list
			cloudLandCover = lines[15].split(" ")[-2]
			if (float(cloudLandCover) > 80):
				print "persentase awan " + scene + " di daratan lebih 25 %"
				#keluar dari folder scene yang sedang dicek
				ftp.cwd("../")
				os.remove(mtl[0])
				boolScene = False
				continue;
			os.remove(mtl[0])
			# jika telah pasti akan diproses periksa apakah data ada di workstation
			if(os.path.exists("C:/data/lahan/input/" + scene)):
				# jika ada hapus folder data tersebut
				shutil.rmtree("C:/data/lahan/input/" + scene)
			# buat folder baru untuk menyimpan data hasil download
			os.makedirs("C:/data/lahan/input/" + scene)

			# filter list di dalam folder buffer hanya _geo dan _geo.ers saja yang didownload
			fileScene2 = [img for img in fileScene if img.endswith("_geo") or img.endswith("_geo.ers") or img.endswith("_geo_cm") or 
			img.endswith("_geo_cm.ers")]
			# mulai looping setiap data yang akan didownload
			for file in fileScene2:
				print file
				# buka file yang akan didownload
				filename = file #replace with your file in the directory ('directory_name')
				localfile = open(filename, 'wb')

				# download file ke directory local
				ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
				# tutup pembukaan file
				localfile.close()

				# pindahkan file ke folder seharusnya yang akan diproses
				os.rename(filename, "C:/data/lahan/input/" + scene + "/" + file)

			#jika sudah download satu scene proses terlebih dahulu (keluar loop)
			break;	
			# keluar folder scene
			ftp.cwd("../")

		if(boolScene == False):
			sceneNow = ""
			filenameNow = [""]
		else:
			# ambil nama scene untuk dijadikan nama output nantinya
			sceneNow = os.listdir("C:/data/lahan/input/" + scene)
			# nama scene adalah nama file yang berekstensi ers
			filenameNow = [img for img in sceneNow if 'geo.ers' in img]
			print filenameNow
		# kembalikan informasi nama file, scene id, tahun, bulan
		msg = str(datetime.now()) + '\t' + "Finished Downloading data ... \n"
		redis.rpush(config.MESSAGES_KEY, msg)
		redis.publish(config.CHANNEL_NAME, msg)
		return filenameNow[0], scene, boolScene, month.split("_")[0], month
	except:
	    se.kirimEmail("Terjadi kesalahan pada FTP server. Username atau password FTP server salah.")
	
	#ftp.retrlines('LIST') # use to check file after connected

	