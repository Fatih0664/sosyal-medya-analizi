from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd

def facebook_mobil_hack(hedef_hesap="webtekno", hedef_gonderi_sayisi=30):
    print("🚀 Facebook 'Mobile Hack' Kazıyıcı başlatılıyor...")
    options = Options()
    
    # Açık olan gerçek Chrome portumuza bağlanıyoruz
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
        
        # SİHİRLİ DOKUNUŞ: Masaüstü (www) yerine Mobil (m) sürüme gidiyoruz!
        url = f"https://m.facebook.com/{hedef_hesap}"
        print(f"Gerçek tarayıcı üzerinden MOBİL sürüme ({url}) odaklanılıyor...")
        driver.get(url)
        time.sleep(5)
        
        print(f"\n--- HEDEF: {hedef_gonderi_sayisi} GÖNDERİ ---")
        gonderiler = {}
        durma_sayaci = 0
        
        while len(gonderiler) < hedef_gonderi_sayisi and durma_sayaci < 6:
            # Mobil sürümdeki tüm paragraf <p>, <span> ve metin kutularını toplayan devasa bir ağ
            metin_elementleri = driver.find_elements(By.XPATH, "//*[self::p or self::span or @dir='auto']")
            baslangic_sayisi = len(gonderiler)
            
            for el in metin_elementleri:
                try:
                    metin = el.text.strip()
                    
                    # Sadece haber niteliği taşıyan uzun ve anlamlı metinleri al (Yorumları/butonları ele)
                    if len(metin) > 45 and metin not in gonderiler:
                        gonderiler[metin] = {
                            'tarih': time.strftime("%Y-%m-%d"),
                            'platform': 'Facebook (Mobil)',
                            'metin': metin.replace('\n', ' ')[:80] + "...",
                            'etkilesim': "Mobil Veri" # Mobilde beğeni çekmek daha stabil olduğu için metne odaklanıyoruz
                        }
                        print(f"[{len(gonderiler)}/{hedef_gonderi_sayisi}] Veri başarıyla söküldü.")
                        
                        if len(gonderiler) >= hedef_gonderi_sayisi:
                            break
                except:
                    continue
            
            if len(gonderiler) >= hedef_gonderi_sayisi:
                break
                
            # Mobilde sayfa kaydırmak masaüstüne göre çok daha kolay ve dertsizdir
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            if len(gonderiler) == baslangic_sayisi:
                durma_sayaci += 1
                print("Sayfa aşağı kaydırıldı, yeni veri yüklenmesi bekleniyor...")
            else:
                durma_sayaci = 0
                
        print("\n--- PANDAS İLE KAYIT ---")
        if gonderiler:
            df = pd.DataFrame(gonderiler.values())
            dosya_adi = f"facebook_{hedef_hesap}_mobil_verisi.csv"
            df.to_csv(dosya_adi, index=False, encoding='utf-8-sig')
            
            print("\n--- ÇEKİLEN VERİNİN İLK 5 SATIRI ---")
            print(df.head())
            print(f"\n🎉 Zafer! Toplam {len(gonderiler)} gönderi '{dosya_adi}' dosyasına kaydedildi!")
        else:
            print("❌ Mobil sürümden de veri alınamadı.")
            
    except Exception as e:
        print(f"Kritik Hata: {e}")

if __name__ == '__main__':
    facebook_mobil_hack()