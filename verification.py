import smtplib as smtp
import random

def dogrulama(verifycode,usermail,ad):
    try:
        subject ='Nara Urun Takip Sistemi Mail Dogrulama'
        link = f'your.website.here/dogrula/{verifycode}'
        
        body = f'''
        
        Sayin {ad}
        Asagidaki linke tiklayarak hesabinizi dogrulayabilirsiniz.

        {link}

        '''
        content = f'{subject} {body}'
        
        myMail = 'E-Mail Adresiniz'
        pw = 'E-Mail Uygulama Sifreniz'
        
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

your.website.here/sifre-sifirla/{resetpw}

        '''
        content = f'{subject} {body}'
        
        myMail = 'E-Mail Adresiniz'
        pw = 'E-Mail Uygulama Sifreniz'
        
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
    posta = 'your_gmail_here'
    dogrulama(rnd,posta)
