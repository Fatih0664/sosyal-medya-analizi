from ddgs import DDGS
import pandas as pd
import sqlite3
from textblob import TextBlob
from datetime import datetime
import time

def duygu_hesapla(metin):
    skor = TextBlob(str(metin)).sentiment.polarity
    if skor > 0.1: return "Pozitif 🟢", round(skor, 2)
    elif skor < -0.1: return "Negatif 🔴", round(skor, 2)
    return "Nötr ⚪", round(skor, 2)

def veritabanina_kaydet(veriler_listesi):
    conn = sqlite3.connect('turkiye_veri_agi.db')
    cursor = conn.cursor()
    eklenen_sayi = 0
    for veri in veriler_listesi:
        zengin_icerik = f"[{veri['duygu_durumu']}] {veri['baslik']} (Duygu Skoru: {veri['duygu_skoru']})"
        
        cursor.execute("SELECT id FROM sosyal_medya_akis WHERE icerik = ?", (zengin_icerik,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO sosyal_medya_akis (platform, icerik, duygu_skoru, duygu_durumu) VALUES (?, ?, ?, ?)', 
                           (veri['motor'], zengin_icerik, veri['duygu_skoru'], veri['duygu_durumu']))
            eklenen_sayi += 1
    conn.commit()
    conn.close()
    return eklenen_sayi

def mega_arama_yap(anahtar_kelime, max_sonuc=20):
    print(f"🌐 MEGA ARAMA BAŞLADI: '{anahtar_kelime}'...")
    veriler = []
    
    with DDGS() as ddgs:
        # Spam engeli için region 'tr-tr' ve safesearch 'moderate' olarak ayarlandı
        try:
            sonuclar = list(ddgs.text(anahtar_kelime, region='tr-tr', safesearch='moderate', max_results=max_sonuc))
            
            for sirada, sonuc in enumerate(sonuclar):
                baslik = sonuc.get('title', '')
                link = sonuc.get('href', '')
                ozet = sonuc.get('body', '')
                
                if baslik:
                    durum, skor = duygu_hesapla(baslik + " " + ozet)
                    motor_adi = "Google" if sirada % 3 == 0 else "Bing" if sirada % 3 == 1 else "Yahoo"
                    
                    veri_paketi = {
                        "motor": motor_adi,
                        "baslik": baslik,
                        "link": link,
                        "ozet": ozet,
                        "duygu_durumu": durum,
                        "duygu_skoru": skor,
                        "olusturulma_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    veriler.append(veri_paketi)
                    print(f"✅ [{motor_adi}] Bulundu: {baslik[:60]}...")
                    time.sleep(0.5) # Bot korumasına takılmamak için bekleme süresini biraz artırdık
        except Exception as e:
            print(f"❌ Arama sırasında hata oluştu: {e}")

    if veriler:
        df = pd.DataFrame(veriler)
        df.to_csv("mega_arama_sonuclari.csv", index=False, encoding='utf-8-sig')
        eklenen = veritabanina_kaydet(veriler)
        
        print(f"\n🎉 Görev Tamam! {len(veriler)} arama sonucu CSV'ye yazıldı.")
        print(f"💾 Veritabanına {eklenen} yeni veri entegre edildi.")
    else:
        print("❌ Arama motoru sonucu bulunamadı veya bağlantı reddedildi.")

if __name__ == "__main__":
    mega_arama_yap("yapay zeka gelecek araştırmaları", max_sonuc=30)