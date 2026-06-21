import sqlite3
import requests

# DİKKAT: Kendi bilgileri buraya gir
TELEGRAM_TOKEN = "8972120519:AAHMrT3J9gblClKQSLvvX_ZUOAaSQGTOLo0"
CHAT_ID = "7082795768"

# Takip etmek istediğin kritik, kriz potansiyeli olan anahtar kelimeler
KRITIK_KELIMELER = ["boykot", "istifa", "hata", "rezalet", "çöküş", "sahtekar", "yalan"]

def acil_durum_sinyali_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"🚨 [KIRMIZI ALARM - RADAR SİSTEMİ]\n\n{mesaj}"
    }
    requests.post(url, data=payload)

def radari_calistir(db_yolu="turkiye_veri_agi.db"):
    print("🛰️ Radar taraması başlatılıyor...")
    
    try:
        conn = sqlite3.connect(db_yolu)
        cursor = conn.cursor()
        
        # Son eklenen (en güncel) 20 veriyi ve içeriklerini kontrol ediyoruz
        sorgu = """
            SELECT platform, icerik, duygu_skoru 
            FROM sosyal_medya_akis 
            ORDER BY id DESC LIMIT 20
        """
        cursor.execute(sorgu)
        son_gonderiler = cursor.fetchall()
        conn.close()
        
        for platform, icerik, duygu_skoru in son_gonderiler:
            if icerik:
                # Kelimeleri küçük harfe çevirerek eşleşme yakalıyoruz
                icerik_alt = icerik.lower()
                for kelime in KRITIK_KELIMELER:
                    if kelime in icerik_alt and duygu_skoru < -0.5:
                        alarm_mesajı = (
                            f"⚠️ Kritik Tehdit Algılandı!\n"
                            f"🌐 Platform: {platform}\n"
                            f"📝 İçerik: \"{icerik}\"\n"
                            f"📊 Duygu Skoru: {duygu_skoru} (Yüksek Negatif)\n"
                            f"🔍 Tetikleyen Kelime: #{kelime}"
                        )
                        print(f"🔥 Radar tetiklendi: {kelime} kelimesi bulundu!")
                        acil_durum_sinyali_gonder(alarm_mesajı)
                        return # Aynı veri için tekrar tekrar alarm atmaması için kesiyoruz
                        
        print("🟢 Radar temiz. Anormal bir durum tespit edilmedi.")
        
    except Exception as e:
        print(f"❌ Radar taraması sırasında hata: {e}")

if __name__ == "__main__":
    radari_calistir()
