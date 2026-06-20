import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import time

API_URL = "http://127.0.0.1:8000/api/v1/veri-gonder/"

def duygu_hesapla(metin):
    skor = TextBlob(str(metin)).sentiment.polarity
    if skor > 0.1: return "Pozitif 🟢", round(skor, 2)
    elif skor < -0.1: return "Negatif 🔴", round(skor, 2)
    return "Nötr ⚪", round(skor, 2)

def telegram_kanali_kazi(kanal_adi):
    print(f"🚀 Telegram Kamu İşçisi Devrede: @{kanal_adi} kanalı dinleniyor...")
    # Kanalın halka açık web akış adresi
    url = f"https://t.me/s/{kanal_adi}"
    
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Telegram mesaj metinlerinin saklandığı div sınıfı
            mesajlar = soup.find_all('div', class_='tgme_widget_message_text')
            
            basarili = 0
            for m in mesajlar[:15]: # Son 15 güncel mesajı al
                metin = m.get_text(strip=True)
                if len(metin) > 20:
                    durum, skor = duygu_hesapla(metin)
                    
                    paket = {
                        "platform": f"Telegram (@{kanal_adi})",
                        "kategori": "Siyaset/Gündem",
                        "icerik": metin,
                        "duygu_durumu": durum,
                        "duygu_skoru": skor
                    }
                    
                    res = requests.post(API_URL, json=paket)
                    if res.status_code == 201:
                        basarili += 1
                        print(f"✅ TG'den aktarıldı: {metin[:40]}...")
            
            print(f"🎉 Telegram görevi tamamlandı. API'ye {basarili} yeni mesaj işlendi.")
    except Exception as e:
        print(f"Telegram hatası: {e}")

if __name__ == "__main__":
    # Örnek olarak büyük bir gündem/haber kanalı üzerinden test ediyoruz
    telegram_kanali_kazi("solcugazete")
