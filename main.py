from ast import Index
import enum
import sys
from tkinter import messagebox
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from panel import *
import sqlite3
import datetime
from PyQt5.QtWidgets import QMessageBox

#arayüz
uyg=QApplication(sys.argv)
pencere = QMainWindow()
ui= Ui_MainWindow()
ui.setupUi(pencere)
pencere.show()


#vt kayit
baglanti = sqlite3.connect("kayit.db")
islem = baglanti.cursor()
baglanti.commit()
table = islem.execute("CREATE TABLE IF NOT EXISTS Kayit(İsim TEXT, Soyisim TEXT, Mail TEXT, Kullanici_Adi TEXT, Şifre TEXT)")
baglanti.commit()

ui.tbl1.setHorizontalHeaderLabels(("İsim","Soyisim","Mail","Kullanici_Adi","Şifre"))

def kayit_ekle():
   İsim = ui.line1.text()
   Soyisim= ui.line2.text()
   Mail= ui.line3.text()
   Kullanici_Adi= ui.line4.text()
   Şifre= ui.line5.text()
   
   try:
        ekle = "insert into Kayit(İsim,Soyisim,Mail,Kullanici_Adi,Şifre) values (?,?,?,?,?)"
        islem.execute(ekle,(İsim,Soyisim,Mail,Kullanici_Adi,Şifre))
        baglanti.commit()
        ui.statusbar.showMessage("Kayıt Eklendi !",10000)
        kayit_listele()
   except:
        ui.statusbar.showMessage("Kayıt Eklenemedi",10000)
 

def kayit_listele():
    ui.tbl1.clear()
    ui.tbl1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    ui.tbl1.setHorizontalHeaderLabels(("İsim","Soyisim","Mail","Kullanici_Adi","Şifre"))
    sorgu = "select * from Kayit"
    islem.execute(sorgu)

    for indexSatir,kayitNumarasi in enumerate(islem):
        for IndexSutun, kayitSutun in enumerate(kayitNumarasi):
            ui.tbl1.setItem(indexSatir,IndexSutun,QTableWidgetItem(str(kayitSutun)))

def kayit_sil():
    sil_mesaj = QMessageBox.question(pencere,"Silme Onayi","Silmek İstediğine Emin Misin ?")
    QMessageBox.Yes | QMessageBox.No

    if sil_mesaj == QMessageBox.Yes:
        secilen_kayit = ui.tbl1.selectedItems()
        silinecek_kayit = secilen_kayit[0].text()

        sorgu = "delete from Kayit where İsim = ?"

        try:
            islem.execute(sorgu,(silinecek_kayit))
            baglanti.commit()
            ui.statusbar.showMessage("Kayit Silindi")
            kayit_listele()
        except:
             ui.statusbar.showMessage("Kayit Silinemedi")

    else:
        ui.statusbar.showMessage("Silme İşlemi İptal Edildi")



#Buton

ui.buton1.clicked.connect(kayit_ekle)
ui.buton2.clicked.connect(kayit_sil)

kayit_listele()

sys.exit(uyg.exec_())





