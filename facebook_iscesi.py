from playwright.sync_api import sync_playwright
import requests
from textblob import TextBlob

API_URL = "http://127.0.0.1:8000/api/v1/veri-gonder/"

def duygu_hesapla(metin):
    skor = TextBlob(str(metin)).sentiment.polarity
    if skor > 0.1: return "Pozitif 🟢", round(skor, 2)
    elif skor < -0.1: return "Negatif 🔴", round(skor, 2)
    return "Nötr ⚪", round(skor, 2)

def facebook_mobil_kazi(grup_id):
    print(f"🕵️‍♂️ Facebook Mobil İşçisi Devrede: Grup ID '{grup_id}'...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            storage_state="facebook_oturum.json",
            viewport={'width': 375, 'height': 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        )
        page = context.new_page()

        try:
            hedef_url = f"https://m.facebook.com/groups/{grup_id}"
            page.goto(hedef_url)
            page.wait_for_timeout(4000) # Sayfanın kendine gelmesini bekle
            
            # --- ANTİ-YÖNLENDİRME (REDIRECT) KALKANI ---
            # Eğer Facebook araya "Şifreyi Kaydet" ekranı soktuysa URL değişmiştir.
            # URL'de grubun ID'si yoksa, bizi yönlendirmiş demektir.
            if grup_id not in page.url:
                print(f"⚠️ Facebook araya onay ekranı soktu. Hedefe zorla geri dönülüyor...")
                page.goto(hedef_url)
                page.wait_for_timeout(4000)
            # --------------------------------------------

            print("⏳ Sayfa doğrulandı. Verilerin düşmesi için aşağı kaydırılıyor...")
            for _ in range(3):
                page.mouse.wheel(0, 1500)
                page.wait_for_timeout(2500)

            elementler = page.query_selector_all("p, span, div[data-comment-id], div[dir='auto']")
            
            basarili = 0
            hafiza_seti = set()

            for el in elementler:
                try:
                    metin = el.inner_text().strip()
                except:
                    continue
                
                # 'Kerem Keremsin' gibi Facebook sistem metinlerini de filtreliyoruz
                if metin and len(metin) > 35 and "beğen" not in metin.lower() and "yorum" not in metin.lower() and "kerem" not in metin.lower() and metin not in hafiza_seti:
                    hafiza_seti.add(metin)
                    durum, skor = duygu_hesapla(metin)
                    
                    paket = {
                        "platform": "Facebook (Mobil Grup)",
                        "kategori": "Yapay Zeka/Teknoloji",
                        "icerik": metin,
                        "duygu_durumu": durum,
                        "duygu_skoru": skor
                    }
                    
                    res = requests.post(API_URL, json=paket)
                    if res.status_code == 201:
                        basarili += 1
                        print(f"✅ FB Mobil'den sızdırıldı: {metin[:50]}...")
                        
            print(f"\n🎉 Görev tamamlandı. API'ye {basarili} yeni Facebook grup verisi enjekte edildi.")

        except Exception as e:
            print(f"❌ Kritik hata: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    facebook_mobil_kazi("yapayzekatoplulugu")
