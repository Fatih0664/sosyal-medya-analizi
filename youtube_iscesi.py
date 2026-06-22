from playwright.sync_api import sync_playwright
import sqlite3
from textblob import TextBlob

# Veritabanına bağlanıp verileri kaydeden fonksiyon
def veritabanina_kaydet(veriler_listesi):
    conn = sqlite3.connect('turkiye_veri_agi.db')
    cursor = conn.cursor()
    eklenen_sayi = 0
    for veri in veriler_listesi:
        # İstatistiksel duygu durumunu da içeriğe ekleyerek zenginleştiriyoruz
        zengin_icerik = f"[{veri['duygu_durumu']}] {veri['icerik']} (Duygu Skoru: {veri['duygu_skoru']})"
        
        cursor.execute("SELECT id FROM sosyal_medya_akis WHERE icerik = ?", (zengin_icerik,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO sosyal_medya_akis (platform, icerik) VALUES (?, ?)', 
                           (veri['platform'], zengin_icerik))
            eklenen_sayi += 1
    conn.commit()
    conn.close()
    return eklenen_sayi

def duygu_hesapla(metin):
    skor = TextBlob(str(metin)).sentiment.polarity
    if skor > 0.1: return "Pozitif 🟢", round(skor, 2)
    elif skor < -0.1: return "Negatif 🔴", round(skor, 2)
    return "Nötr ⚪", round(skor, 2)

def youtube_kaziyici(anahtar_kelime):
    print(f"📺 YouTube Botu Göreve Başladı: '{anahtar_kelime}' aranıyor...")
    veriler = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Arka planda çalışması daha verimli
        page = browser.new_page()

        try:
            search_url = f"https://www.youtube.com/results?search_query={anahtar_kelime}"
            page.goto(search_url, wait_until="networkidle")
            
            # YouTube sonuçlarını aşağı kaydır
            for _ in range(2):
                page.mouse.wheel(0, 1500)
                page.wait_for_timeout(2000)

            videolar = page.query_selector_all("a#video-title")
            
            for v in videolar[:20]:
                baslik = v.get_attribute("title")
                if baslik and len(baslik) > 10:
                    durum, skor = duygu_hesapla(baslik)
                    veriler.append({
                        "platform": "YouTube",
                        "icerik": baslik,
                        "duygu_durumu": durum,
                        "duygu_skoru": skor
                    })
                    print(f"✅ YT'den çekildi: {baslik[:40]}...")
            
            if veriler:
                eklenen = veritabanina_kaydet(veriler)
                print(f"\n🎉 YouTube görevi tamamlandı. Veritabanına {eklenen} yeni veri eklendi.")
            
        except Exception as e:
            print(f"YouTube Botu bir engelle karşılaştı: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    youtube_kaziyici("yapay zeka gelecek araştırmaları")