import smtplib
def fun(mail,otp):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("your mail", "your mail password")
    message = str(otp)+" "+"is your quiz portal verification code"
    s.sendmail("your mail", mail, message)
    s.quit()
