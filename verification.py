import smtplib as smtp
import random

def dogrulama(verifycode,usermail,ad):
    try:
        subject ='Nara Urun Takip Sistemi Mail Dogrulama'
        link = f'berkehanyavas.pythonanywhere.com/dogrula/{verifycode}'
        
        body = f'''
        
        Sayin {ad}
        Asagidaki linke tiklayarak hesabinizi dogrulayabilirsiniz.

        {link}

        '''
        content = f'{subject} {body}'
        
        myMail = 'berkeyavas.9999@gmail.com'
        pw = 'dagugwfiqofmawew'
        
        sendTo = usermail
        
        connection = smtp.SMTP_SSL('smtp.gmail.com',465)
        connection.login(myMail,pw)
        connection.sendmail(myMail,sendTo,content.encode('utf-8'))
        connection.close()
        
        return True
    except Exception as e:
        print(e)
        return False
    
def sifreSifirlama(resetpw,usermail,ad):
    try:
        subject ='Nara Urun Takip Sistemi Mail Dogrulama'
        
        body = f'''
        
Sayin {ad}
Asagidaki linke tiklayarak sifrenizi sifirlayabilirsiniz.

berkehanyavas.pythonanywhere.com/sifre-sifirla/{resetpw}

        '''
        content = f'{subject} {body}'
        
        myMail = 'berkeyavas.9999@gmail.com'
        pw = 'dagugwfiqofmawew'
        
        sendTo = usermail
        
        connection = smtp.SMTP_SSL('smtp.gmail.com',465)
        connection.login(myMail,pw)
        connection.sendmail(myMail,sendTo,content.encode('utf-8'))
        connection.close()
        
        return True
    except Exception as e:
        print(e)
        return False

    
    
    
if __name__ == '__main__':
    rnd = random.randint(100000000000000,999999999999999) #verify code
    posta = 'berkehanyavas@gmail.com'
    dogrulama(rnd,posta)