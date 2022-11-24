from flask import Flask, render_template, redirect, url_for, flash, session, request
import sqlite3
from wtforms import Form, StringField, DateField, SearchField, TextAreaField, PasswordField, validators, SelectField, BooleanField
from passlib.hash import sha256_crypt
from functools import wraps
import random
import verification

#login control decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ('isLoggedIn' in session) == True and session['isLoggedIn'] == True:
            return f(*args, **kwargs)
        else:
            flash('Bu sayfayi goruntulemek icin lutfen giris yapin','danger')
            return redirect(url_for('giris_yap'))
    return decorated_function

#logout control decorator
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (('isLoggedIn' in session) and session['isLoggedIn'] == False) or ('isLoggedIn' not in session):
            return f(*args, **kwargs)
        else:
            flash('Bu sayfayi goruntulemek icin lutfen cikis yapin','danger')
            return redirect(url_for('index'))
    return decorated_function

#isAdmin control decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ('isLoggedIn' in session) == True and session['isLoggedIn'] == True:
            if session['isLoggedIn'] == True and session['isAdmin'] == 'True':
                return f(*args, **kwargs)
            else:
                flash('Bu sayfayi goruntulemek icin admin yetkisine ihtiyaciniz var.','danger')
                return redirect(url_for('index'))
        else:
            flash('Bu sayfayi goruntulemek icin lutfen giris yapin','danger')
            return redirect(url_for('giris_yap'))
    return decorated_function

app = Flask(__name__)
app.secret_key = 'oh_so_secret'

class RegisterForm(Form):
    ad = StringField(
        'Isim Soyisim',
        validators=[
            validators.Length(
                min=3,
                max=35
            )
        ]
    )
    
    mail = StringField(
        'Nara Mail Adresi',
        validators=[
            validators.Email(
                message='Lutfen gecerli bir mail adresi girin.',
                allow_empty_local=False
            )
        ]
    )
    
    sifre = PasswordField(
        'Parola:',
        validators=[
            validators.DataRequired(
                message='Lutfen bir parola belirleyin.'
            ),
            validators.EqualTo(
                fieldname='confirm',
                message='Parolaniz uyusmuyor.'
            )
        ]
    )
    
    confirm = PasswordField('Parola Dogrula')
    
    isAdmin = BooleanField('Admin Yetkisi',false_values=(False,'False','false','0',0))
    
    isVerified = BooleanField('Dogrulandi',false_values=(False,'False','false','0',0))
    
    resetPw = 0
    
class LoginForm(Form):
    mail = StringField('Mail adresinizi giriniz')
    sifre = PasswordField('Sifrenizi giriniz')

class UrunForm(Form):
    ad = StringField('Urun Adi',validators=[validators.Length(min=2,max=50)])
    ozellik = TextAreaField('Urun Ozellikleri',validators=[validators.Length(min=5)])
    kullanan = SelectField('Kim kullaniyor',choices=[])

class SearchForm(Form):
    ad = SearchField('Urun Adi')

class LogForm(Form):
    basla = DateField('Baslangic Tarihi')
    bitis = DateField('Bitis Tarihi')

@app.route('/giris-yap',methods=['GET','POST'])
@logout_required
def giris_yap():
    con = sqlite3.connect('inv.db')
    form = LoginForm(request.form)
    if request.method == 'POST':
        mail = form.mail.data
        sifre = form.sifre.data
        
        cursor = con.cursor()
        sorgu = f"select * from users where Mail = '{mail}'"
        cursor.execute(sorgu)
        data = cursor.fetchone()
        if data:
            sifre_db = data[3]
            if sha256_crypt.verify(sifre,sifre_db):
                if data[5] == 'True':
                    flash('Basariyla giris yaptiniz.','success')
                    session['isLoggedIn'] = True
                    session['name'] = data[1]
                    session['isAdmin'] = data[4]
                    session['id'] = data[0]
                    return redirect(url_for('index'))
                else:
                    flash('Hesabinizi dogrulamadan giris yapamazsiniz.','danger')
            else:
                flash('Yanlis sifre veya mail adresi girdiniz.','danger')
                return redirect(url_for('giris_yap'))
        else:
            flash('Yanlis sifre veya mail adresi girdiniz.','danger')
            return redirect(url_for('giris_yap'))
    return render_template('giris-yap.html',form=form)

@app.route('/kayit-ol',methods=['GET','POST'])
@logout_required
def kayit_ol():
    con = sqlite3.connect('inv.db')
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        ad = form.ad.data
        mail = form.mail.data
        sifre = sha256_crypt.encrypt(form.sifre.data)
        isAdmin = False
        isVerified = False
        
        cursor2 = con.cursor()
        sorgu2 = f"select * from users where Mail = '{mail}'"
        cursor2.execute(sorgu2)
        result2 = cursor2.fetchall()
        if len(result2) > 0:
            flash('Bu Mail adresi zaten kayitli.','warning')
            return redirect(url_for('kayit_ol'))
        else:            
        
            if mail.endswith('@gmail.com'):
                rnd = random.randint(1000000000,2147483647) #verify code

                if verification.dogrulama(verifycode=rnd,usermail=mail,ad=ad):
                    cursor = con.cursor()
                    sorgu = f"insert into users(Ad,Mail,Sifre,isAdmin,isVerified,verifyCode) VALUES('{ad}','{mail}','{sifre}','{isAdmin}','{isVerified}','{rnd}')"
                    cursor.execute(sorgu)
                    con.commit()
                    cursor.close()
                
                    flash('Basariyla kayit oldunuz. Mail hesabiniza gelen link ile hesabinizi dogruladiktan sonra isleminize devam edebilirsiniz.','success')
                    return redirect(url_for('giris_yap'))
                else:
                    flash('Bir hata meydana geldi.','warning')
                    return redirect(url_for('kayit_ol'))
            else:
                flash('@nara.com.tr ile biten hesabiniz ile uye olmaniz gerek.','danger')
                return redirect(url_for('kayit_ol'))
    else:
        return render_template('kayit-ol.html',form = form)

@app.route('/cikis-yap')
@login_required
def cikisYap():
    session['isLoggedIn'] = False
    return redirect(url_for('giris_yap'))

@app.route('/')
@login_required
def index():
    con = sqlite3.connect('inv.db')
    cursor = con.cursor()
    sorgu = "select * from urunler where Kullanan = '{}'".format(session['name'])
    cursor.execute(sorgu)
    urunler = cursor.fetchall()
    return render_template('index.html',urunler=urunler)
    
@app.route('/hakkinda')
def hakkinda():
    return render_template('hakkinda.html')

@app.route('/tum-urunler')
@login_required
def tum_urunler():
    con = sqlite3.connect('inv.db')
    cursor = con.cursor()
    sorgu = 'select * from urunler'
    cursor.execute(sorgu)
    urunler = cursor.fetchall()
    return render_template('tum-urunler.html',urunler=urunler)

@app.route('/urun-ekle',methods=['GET','POST'])
@admin_required
def urun_ekle():
    con = sqlite3.connect('inv.db')
    form = UrunForm(request.form)
    if request.method == 'POST':
        ad = form.ad.data
        ozellik = form.ozellik.data
        kullanan = form.kullanan.data
        ekleyen = session['name']
        
        cursor = con.cursor()
        kayit = f"insert into urunler(urunAdi,urunOzellikleri,Kullanan,Ekleyen) VALUES('{ad}','{ozellik}','{kullanan}','{ekleyen}')"
        cursor.execute(kayit)
        con.commit()
        cursor.close()
        
        log = con.cursor()
        logsor = "insert into logs(log) VALUES('{}')".format(f'<b>{ekleyen}</b> adli kullanici <b>{ad}</b> isimli <b>{ozellik}</b> ozelliklerindeki urunu ekledi. <b>{kullanan}</b> adli kullaniciya atadi.')
        log.execute(logsor)
        con.commit()
        log.close()
        
        flash('Urun basariyla eklendi.','success')
        return redirect(url_for('urun_ekle'))
    else:
        cursor = con.cursor()
        sorgu = 'select ad from users'
        cursor.execute(sorgu)

        data = cursor.fetchall()
        liste = ['Depoda','Etkinlikte']
        for i in data:
            liste.append(i[0])

        form.kullanan.choices = liste
        return render_template('urun-ekle.html',form=form)

@app.route('/urun/<string:id>')
@login_required
def urun_ozellikleri(id):
    con = sqlite3.connect('inv.db')
    cursor = con.cursor()
    sorgu = "select * from urunler where id = '{}'".format(id)
    cursor.execute(sorgu)
    urun = cursor.fetchone()
    return render_template('urun-ozellikleri.html',urun=urun)

@app.route('/urun/duzenle/<string:id>',methods=['GET','POST'])
@admin_required
def urun_duzenle(id):
    con = sqlite3.connect('inv.db')
    if request.method == 'GET':
        cursor = con.cursor()
        sorgu = "select * from urunler where id = '{}'".format(id)
        cursor.execute(sorgu)
        urun = cursor.fetchone()
        if urun:
            form = UrunForm()
            form.ad.data = urun[1]
            form.ozellik.data = urun[2]
            form.kullanan.data = urun[3]
            
            cursor2 = con.cursor()
            sorgu2 = 'select ad from users'
            cursor2.execute(sorgu2)
            
            data = cursor2.fetchall()
            liste = ['Depoda','Etkinlikte']
            for i in data:
                liste.append(i[0])
            form.kullanan.choices = liste
            
            return render_template('urun-duzenle.html',form=form,urun=urun)
        else:
            flash("Bu id'ye sahip bir urun bulunmamaktadir.",'danger')
            return redirect(url_for('index'))
    else:
        form = UrunForm(request.form)
        ad = form.ad.data
        ozellik = form.ozellik.data
        kullanan = form.kullanan.data
        duzenleyen = session['name']
        cursor3 = con.cursor()
        sorgu3 = "update urunler set urunAdi = '{}', urunOzellikleri = '{}', Kullanan = '{}', Duzenleyen = '{}' where id = '{}'".format(ad,ozellik,kullanan,duzenleyen,id)
        cursor3.execute(sorgu3)
        con.commit()
        
        log = con.cursor()
        logsor = "insert into logs(log) VALUES('{}')".format(f'<b>{session["name"]}</b> adli kullanici <b>{ad}</b> isimli <b>{ozellik}</b> ozelliklerindeki urunu <b>{kullanan}</b> adli kullaniciya duzenledi.')
        log.execute(logsor)
        con.commit()
        log.close()

        
        flash('Urun basariyla guncellendi.','success')
        return redirect(f'/urun/duzenle/{id}')

@app.route('/urun/sil/<string:id>')
@admin_required
def urunSil(id):
    con = sqlite3.connect('inv.db')
    cursor = con.cursor()
    sorgu = "select * from urunler where id = '{}'".format(id)
    cursor.execute(sorgu)
    
    urun = cursor.fetchone()
    ad = urun[0]
    ozellik = urun[1]
    kullanan = urun[2]
    
    if len(urun) > 0:
        sorgu2 = "delete from urunler where id = '{}'".format(id)
        cursor.execute(sorgu2)
        con.commit()
        
        log = con.cursor()
        logsor = "insert into logs(log) VALUES('{}')".format(f'<b>{session["name"]}</b> adli kullanici <b>{ad}</b> isimli <b>{ozellik}</b> ozelliklerindeki urunu sildi. <b>{kullanan}</b> adli kullanici kullaniyordu.')
        log.execute(logsor)
        con.commit()
        log.close()

        
        flash('Urun basariyla silindi.','success')
        return redirect(url_for('tum_urunler'))
    else:
        flash('Boyle bir urun bulunmamaktadir.','danger')
        return redirect(url_for('tum_urunler')) #bu sayfayi olustur

@app.route('/user/<string:ad>')
@login_required
def kullaniciProfili(ad):
    con = sqlite3.connect('inv.db')
    cursor = con.cursor()
    sorgu = "select * from urunler where Kullanan = '{}'".format(ad)
    cursor.execute(sorgu)
    urunler = cursor.fetchall()
    return render_template('kullanici-profili.html',urunler=urunler,ad=ad)

@app.route('/ekleyen/<string:ad>')
@login_required
def ekleyen(ad):
    con = sqlite3.connect('inv.db')
    cursor = con.cursor()
    sorgu = "select * from urunler where Ekleyen = '{}'".format(ad)
    cursor.execute(sorgu)
    urunler = cursor.fetchall()
    return render_template('ekleyen.html',urunler=urunler,ad=ad)

@app.route('/urun/kullanbirak/<string:id>')
@login_required
def kullan_birak(id):
    con = sqlite3.connect('inv.db')
    cursor = con.cursor()
    sorgu = "select * from urunler where id = '{}'".format(id)
    cursor.execute(sorgu)
    urun = cursor.fetchone()
    if urun:
        if (urun[3] == 'Depoda') or (urun[3] == session['name']):
            return render_template('kullan-birak.html',urun=urun)
        else:
            flash('Bu sayfayi gormeye yetkiniz bulunmamaktadir.','danger')
            return redirect(url_for('index'))
    else:
        flash('Boyle bir urun bulunmamaktadir.','danger')
        return redirect(url_for('index'))
    
@app.route('/urun/kullanmayabasla/<string:id>')
@login_required
def kullanmayaBasla(id):
    con = sqlite3.connect('inv.db')
    cursor = con.cursor()
    sorgu = "select * from urunler where id = '{}'".format(id)
    cursor.execute(sorgu)
    urun = cursor.fetchone()
    ad = urun[1]
    ozellik = urun[2]
    
    if urun:
        if urun[3] == 'Depoda':
            cursor2 = con.cursor()
            sorgu2 = "update urunler set Kullanan = '{}' where id = '{}'".format(session['name'],id)
            cursor2.execute(sorgu2)
            con.commit()
            
            log = con.cursor()
            logsor = "insert into logs(log) VALUES('{}')".format(f'<b>{session["name"]}</b> adli kullanici <b>{ad}</b> isimli <b>{ozellik}</b> ozelliklerindeki urunu kullanmaya basladi.')
            log.execute(logsor)
            con.commit()
            log.close()
                
            flash('Urunu kullanmaya baslayabilirsiniz.','success')
            return redirect(url_for('index'))
        else:
            flash('Bu urunu su anda baskasi kullaniyor.','warning')
            return redirect(url_for('index'))
    else:
        flash('Boyle bir urun bulunmamaktadir.','danger')
        return redirect(url_for('index'))
    
@app.route('/urun/kullanmayibirak/<string:id>')
@login_required
def kullanmayiBirak(id):
    con = sqlite3.connect('inv.db')
    cursor = con.cursor()
    sorgu = "select * from urunler where id = '{}'".format(id)
    cursor.execute(sorgu)
    urun = cursor.fetchone()
    if urun:
        if urun[3] == session['name']:
            cursor2 = con.cursor()
            sorgu2 = "update urunler set Kullanan = '{}' where id = '{}'".format('Depoda',id)
            cursor2.execute(sorgu2)
            con.commit()
            
            ad = urun[1]
            ozellik = urun[2]
            
            log = con.cursor()
            logsor = "insert into logs(log) VALUES('{}')".format(f'<b>{session["name"]}</b> adli kullanici <b>{ad}</b> isimli <b>{ozellik}</b> ozelliklerindeki urunu depoya birakti.')
            log.execute(logsor)
            con.commit()
            log.close()

            flash('Urunu basariyla depoya biraktiniz..','success')
            return redirect(url_for('index'))
        else:
            flash('Bu urunu su anda baskasi kullaniyor.','warning')
            return redirect(url_for('index'))
    else:
        flash('Boyle bir urun bulunmamaktadir.','danger')
        return redirect(url_for('index'))

@app.route('/logs',methods=['GET','POST'])
@admin_required
def logs():
    con = sqlite3.connect('inv.db')
    form = LogForm(request.form)
    if request.method == 'POST':
        cursor2 = con.cursor()
        basla = form.basla.data
        bitis = form.bitis.data
        if (basla != None) and (bitis != None):
            sorgu2 = f"select * from logs where (tarih between '{basla}' and '{bitis}')"
            cursor2.execute(sorgu2)
            loglar = cursor2.fetchall()
            if loglar:
                loglar.reverse()
                flash(f'{basla} ile {bitis} tarihleri arasindaki kayitlar basariyla listelendi.','success')
                return render_template('log-kayitlari.html',loglar=loglar,form=form)
            else:
                flash('Aradiginiz kriterlerde log kaydi bulunamadi.','warning')
                return redirect(url_for('logs'))
        else:
            flash('Lutfen tarih kismini doldurunuz.','danger')
            return redirect(url_for('logs'))
    cursor = con.cursor()
    sorgu = 'select * from logs'
    cursor.execute(sorgu)
    loglar = cursor.fetchall()
    loglar.reverse()
    return render_template('log-kayitlari.html',loglar=loglar,form=form)

@app.route('/arama',methods=['GET','POST'])
@login_required
def urunArama():
    con = sqlite3.connect('inv.db')
    form = SearchForm(request.form)
    if request.method == 'POST':
        ad = form.ad.data
        
        cursor = con.cursor()
        ara = "select * from urunler where urunAdi LIKE '%{}%'".format(ad)
        cursor.execute(ara)
        urunler = cursor.fetchall()
        if len(urunler) > 0:
            return render_template('arama.html',form=form,urunler=urunler)
        else:
            flash('Bu isimde bir urun bulunamadi.','warning')
            return redirect(url_for('urunArama'))
        
    return render_template('arama.html',form=form)

@app.route('/dogrula/<string:verify>')
@logout_required
def dogrulama(verify):
    con = sqlite3.connect('inv.db')
    cursor = con.cursor()
    sorgu = "select * from users where verifyCode = '{}'".format(verify)
    cursor.execute(sorgu)
    user = cursor.fetchone()
    if user:
        cursor2 = con.cursor()
        sorgu2 = "update users set isVerified = True , verifyCode = 0 where id = '{}'".format(user[0])
        cursor2.execute(sorgu2)
        con.commit()
        flash('Hesabinizi basariyla dogruladiniz. Giris yapabilirsiniz.','success')
        return redirect(url_for('giris_yap'))
    else:
        flash('Boyle bir sayfa bulunmamaktadir.','warning')
        return redirect(url_for('giris_yap'))

@app.route('/sifremi-unuttum',methods=['GET','POST'])
@logout_required
def sifremi_unuttum():
    con = sqlite3.connect('inv.db')
    form = LoginForm(request.form)
    if request.method == 'POST':
        mail = form.mail.data
        
        cursor = con.cursor()
        sorgu = "select * from users where Mail = '{}'".format(mail)
        cursor.execute(sorgu)
        user = cursor.fetchone()
        if user:
            rnd = random.randint(1000000000,2147483647) #verify code
            if verification.sifreSifirlama(resetpw=rnd,usermail=mail,ad=user[1]):
                cursor2 = con.cursor()
                sorgu2 = "update users set resetPw = '{}' where id = '{}'".format(rnd,user[0])
                cursor2.execute(sorgu2)
                con.commit()
                cursor2.close()
                flash('Mail adresinizdeki link ile sifrenizi degistirebilirsiniz.','success')
                return redirect(url_for('giris_yap'))
            else:
                return redirect(url_for('sifremi_unuttum'))
    else:
        return render_template('sifremi-unuttum.html',form=form)

@app.route('/sifre-sifirla/<string:resetpw>',methods=['GET','POST'])
@logout_required
def sifre_sifirlama(resetpw):
    con = sqlite3.connect('inv.db')
    form = LoginForm(request.form)
    if request.method == 'POST':
        pw = sha256_crypt.encrypt(form.sifre.data)
        
        cursor = con.cursor()
        sorgu = "select * from users where resetPw = '{}'".format(resetpw)
        cursor.execute(sorgu)
        user = cursor.fetchone()
        if user:
            cursor2 = con.cursor()
            sorgu2 = "update users set Sifre = '{}' , resetPw = 0 where id = '{}'".format(pw,user[0])
            cursor2.execute(sorgu2)
            con.commit()
            
            flash('Sifrenizi basariyla sifirladiniz.','success')
            return redirect(url_for('giris_yap'))
        else:
            flash('Boyle bir sayfa bulunmamaktadir.','danger')
            return render_template('layout.html')
    else:
        return render_template('sifre-sifirla.html',form=form)

@app.route('/admin')
@login_required
def adminpanel():
    con = sqlite3.connect('inv.db')
    cursor = con.cursor()
    sorgu = 'select * from users'
    cursor.execute(sorgu)
    users = cursor.fetchall()
    return render_template('adminpanel.html',users=users)

@app.route('/user/duzenle/<string:ad>',methods=['GET','POST'])
@login_required
def kullaniciduzenle(ad):
    con = sqlite3.connect('inv.db')
    if request.method == 'GET':
        cursor = con.cursor()
        sorgu = "select * from users where Ad = '{}'".format(ad)
        cursor.execute(sorgu)
        user = cursor.fetchone()
        if user:
            print(user)
            form = RegisterForm()
            form.ad.data = user[1]
            form.mail.data = user[2]
            form.isAdmin.data = user[4]
            form.isVerified.data = user[5]
            if user[4] == 'False':
                form.isAdmin.data = False
            if user[5] == 'False':
                print(type(user[5]))
                form.isVerified.data  = False

            return render_template('kullanici-duzenle.html',form=form,user=user)
        else:
            flash('Boyle bir kullanici bulunmamaktadir.','danger')
            return redirect(url_for('adminpanel'))
    else:
        cursor2 = con.cursor()
        sorgu = "select * from users where Ad = '{}'".format(ad)
        cursor2.execute(sorgu)
        user = cursor2.fetchone()
        
        id = user[0]
        form = RegisterForm(request.form)
        print(form.data)
        ad = form.ad.data
        mail = form.mail.data
        isAdmin = form.isAdmin.data
        isVerified = form.isVerified.data
        cursor2 = con.cursor()
        sorgu2 = "update users set Ad = '{}', Mail = '{}', isAdmin = '{}', isVerified = '{}' where id = '{}'".format(ad,mail,isAdmin,isVerified,id)
        cursor2.execute(sorgu2)
        con.commit()
        
        log = con.cursor()
        logsor = "insert into logs(log) VALUES('{}')".format(f'<b>{session["name"]}</b> adli kullanici <b>{ad}</b> isimli kullaniciyi duzenledi.')
        log.execute(logsor)
        con.commit()
        log.close()
        
        flash('Kullanici basariyla duzenlendi.','success')
        return redirect(f'/user/duzenle/{ad}')



if __name__ == '__main__':
    baglanti = sqlite3.connect('inv.db')
    sorgu = 'CREATE TABLE if not exists "urunler" ("id"	INTEGER,"urunAdi"	TEXT,"urunOzellikleri"	TEXT,"Kullanan"	INT,"Ekleyen"	INT,"Duzenleyen"	INT,PRIMARY KEY("id" AUTOINCREMENT))'
    baglanti.execute(sorgu)
    baglanti.commit()
    sorgu2 = 'CREATE TABLE if not exists "users" ("id"	INTEGER,"Ad"	TEXT,"Mail"	TEXT,"Sifre"	TEXT,"isAdmin"	BOOLEAN,"isVerified"	BOOLEAN,"verifyCode"	INT,"resetPw"	INT,PRIMARY KEY("id" AUTOINCREMENT))'
    baglanti.execute(sorgu2)
    baglanti.commit()
    sorgu3 = 'CREATE TABLE if not exists "logs" ("id"	INTEGER,"log"	TEXT,"tarih"	DATE DEFAULT CURRENT_DATE,PRIMARY KEY("id" AUTOINCREMENT))'
    baglanti.execute(sorgu3)
    baglanti.commit()
    app.run(debug=True)