import requests
import os
# Önceki yazdığımız modülden yapay zeka fonksiyonunu doğrudan içe aktarıyoruz
from yapay_zeka_merkezi import yapay_zeka_ozeti_cikar

# DİKKAT: Kendi bilgilerini buraya gir
TELEGRAM_TOKEN = "8972120519:AAHMrT3J9gblClKQSLvvX_ZUOAaSQGTOLo0"
CHAT_ID = "7082795768"

def telegram_mesaj_gonder(metin):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": metin
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Metin raporu Telegram'a başarıyla fırlatıldı!")
        else:
            print(f"❌ Telegram mesaj hatası: {response.text}")
    except Exception as e:
        print(f"❌ Mesaj gönderiminde hata: {e}")

def telegram_belge_gonder(dosya_yolu):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    if os.path.exists(dosya_yolu):
        try:
            with open(dosya_yolu, 'rb') as dosya:
                files = {'document': dosya}
                data = {'chat_id': CHAT_ID}
                response = requests.post(url, data=data, files=files)
                if response.status_code == 200:
                    print(f"✅ Excel dosyası ({dosya_yolu}) Telegram'a eklendi!")
                else:
                    print(f"❌ Telegram belge hatası: {response.text}")
        except Exception as e:
            print(f"❌ Belge gönderiminde hata: {e}")
    else:
        print(f"⚠️ Gönderilecek belge bulunamadı: {dosya_yolu}")

if __name__ == "__main__":
    print("🚀 Telegram Kuryesi motorları ısıtıyor...")
    
    # 1. Groq (Llama-3) modelini çalıştırıp güncel raporu alıyoruz
    ozet_metni = yapay_zeka_ozeti_cikar()
    
    if ozet_metni:
        print("📱 Veriler Telegram'a aktarılıyor...")
        # 2. Metni Telegram'dan yolla
        telegram_mesaj_gonder(ozet_metni)
        
        # 3. Excel dosyasını Telegram'dan yolla
        excel_dosyasi = "Gunluk_Istihbarat_Raporu.xlsx"
        telegram_belge_gonder(excel_dosyasi)
        
        print("🎉 Tüm istihbarat verileri başarıyla cebine iletildi!")
    else:
        print("❌ Özet çıkarılamadığı için Telegram'a gönderim yapılamadı.")
