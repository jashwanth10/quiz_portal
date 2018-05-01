import smtplib
def fun(mail,otp):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("viveknannaka945@gmail.com", "Vivek$945&$nannaka")
    message = str(otp)+" "+"is your quiz portal verification code"
    s.sendmail("viveknannaka945@gmail.com", mail, message)
    s.quit()
