import pandas as pd
import requests
import time
from textblob import TextBlob
import os

API_URL = "http://127.0.0.1:8000/api/v1/veri-gonder/"

def skor_hesapla(metin):
    analiz = TextBlob(str(metin))
    skor = analiz.sentiment.polarity
    if skor > 0.1:
        return "Pozitif 🟢", round(skor, 2)
    elif skor < -0.1:
        return "Negatif 🔴", round(skor, 2)
    else:
        return "Nötr ⚪", round(skor, 2)

basarili_kayit = 0

# 1. BÖLÜM: MEGA ARAMA VERİLERİNİ AKTAR (Google, Bing, Yahoo)
print("🌐 Web Arama Verileri Aktarılıyor...")
try:
    df_web = pd.read_csv("mega_arama_sonuclari.csv").dropna(subset=['baslik'])
    for index, row in df_web.iterrows():
        duygu_durumu, duygu_skoru = skor_hesapla(row['baslik'])
        # Platformu doğrudan CSV'deki 'motor' sütunundan alıyoruz (Google, Bing, Yahoo)
        veri_paketi = {
            "platform": row['motor'], 
            "kategori": "Teknoloji",
            "icerik": row['baslik'],
            "duygu_durumu": duygu_durumu,
            "duygu_skoru": duygu_skoru
        }
        response = requests.post(API_URL, json=veri_paketi)
        if response.status_code == 201: basarili_kayit += 1
except Exception as e:
    print(f"Web verisi hatası: {e}")

# 2. BÖLÜM: WHATSAPP VERİLERİNİ AKTAR
print("💬 WhatsApp Verileri Aktarılıyor...")
wp_dosya = "whatsapp_mesajlar.csv"
if os.path.exists(wp_dosya):
    try:
        df_wp = pd.read_csv(wp_dosya, header=None, names=["Tarih/Kim", "Mesaj"], encoding="utf-8-sig").dropna()
        for index, row in df_wp.iterrows():
            duygu_durumu, duygu_skoru = skor_hesapla(row['Mesaj'])
            veri_paketi = {
                "platform": "WhatsApp", 
                "kategori": "Teknoloji",
                "icerik": row['Mesaj'],
                "duygu_durumu": duygu_durumu,
                "duygu_skoru": duygu_skoru
            }
            response = requests.post(API_URL, json=veri_paketi)
            if response.status_code == 201: basarili_kayit += 1
    except Exception as e:
        print(f"WhatsApp verisi hatası: {e}")

print(f"\n🎉 İşlem Tamamlandı! Toplam {basarili_kayit} yeni veri API'ye (ve oradan Flutter'a) gönderildi!")
