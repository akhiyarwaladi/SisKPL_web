import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
def kirimEmail(pesan):
	
	fromaddr = "sistem.otomatisasi8@gmail.com"
	#toaddr = ["akiyar18@gmail.com", "akiyar@apps.ipb.ac.id", "imas.sitanggang@apps.ipb.ac.id"]
	toaddr = ["syarif.budhiman@lapan.go.id","rokhis.khomarudin@lapan.go.id","ayom.widipaminto@lapan.go.id","rahmadi@lapan.go.id","bowo_lpn@yahoo.com","mpriyatna@yahoo.com","iskef55@gmail.com"]

	
	print("Mengirim email ke " + str(toaddr))
	msg = MIMEMultipart()
	# msg['From'] = fromaddr
	# msg['To'] = toaddr
	msg['Subject'] = "Notifikasi SisKPL (Sistem Otomatisasi Klasifikasi Tutupan Lahan)"
	
	body = pesan
	msg.attach(MIMEText(body, 'plain'))

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "8Pusfatj@")
	text = msg.as_string()
	#text = pesan
	server.sendmail(fromaddr, toaddr, text)
	print("Email telah dikirim ke " + str(toaddr))
	server.quit()