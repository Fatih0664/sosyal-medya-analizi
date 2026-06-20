import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os
import pandas as pd

def nihai_twitter_kaziyici(hedef_hesap="webtekno", hedef_tweet_sayisi=50):
    print("🚀 X (Twitter) Nihai Kazıcı başlatılıyor...")
    options = uc.ChromeOptions()
    
    # 1. HİLE: Chrome'un dili Türkçe'ye zorlanıyor ve Otomatik Çeviri tamamen kapatılıyor
    options.add_argument("--lang=tr-TR")
    options.add_argument("--disable-features=Translate")
    
    profil_yolu = os.path.join(os.getcwd(), "chrome_profil")
    options.add_argument(f"--user-data-dir={profil_yolu}")
    
    driver = uc.Chrome(options=options, version_main=149)
    
    try:
        url = f"https://x.com/{hedef_hesap}"
        print(f"{url} adresine gidiliyor...")
        driver.get(url)
        
        print("Oturumun yüklenmesi için 8 saniye bekleniyor...")
        time.sleep(8) 
        
        gonderiler = {} 
        durma_sayaci = 0
        
        print(f"\n--- HEDEF: {hedef_tweet_sayisi} TWEET ---")
        
        while len(gonderiler) < hedef_tweet_sayisi and durma_sayaci < 5:
            tweet_elementleri = driver.find_elements(By.CSS_SELECTOR, "article[data-testid='tweet']")
            baslangic_sayisi = len(gonderiler)
            
            for tweet in tweet_elementleri:
                try:
                    metin_el = tweet.find_element(By.CSS_SELECTOR, "div[data-testid='tweetText']")
                    tweet_metin = metin_el.text
                    
                    if tweet_metin in gonderiler:
                        continue 
                    
                    try:
                        tarih_el = tweet.find_element(By.TAG_NAME, "time")
                        tweet_tarih = tarih_el.get_attribute("datetime").replace('T', ' ')[:19]
                    except:
                        tweet_tarih = ""
                        
                    try:
                        begeni_el = tweet.find_element(By.CSS_SELECTOR, "button[data-testid='like']")
                        tweet_etkilesim = begeni_el.get_attribute("aria-label").split(' ')[0]
                        if not tweet_etkilesim.isdigit():
                            tweet_etkilesim = "0"
                    except:
                        tweet_etkilesim = "0"
                        
                    if tweet_metin:
                        gonderiler[tweet_metin] = {
                            'tarih': tweet_tarih,
                            'platform': 'Twitter/X',
                            'metin': tweet_metin.replace('\n', ' ')[:80] + "...", 
                            'etkilesim': tweet_etkilesim
                        }
                        print(f"[{len(gonderiler)}/{hedef_tweet_sayisi}] Yeni tweet yakalandı.")
                    
                    if len(gonderiler) >= hedef_tweet_sayisi:
                        break
                        
                except Exception:
                    continue 
            
            if len(gonderiler) >= hedef_tweet_sayisi:
                break
            
            # --- 2. HİLE: HEDEFE KİLİTLİ KAYDIRMA ---
            if tweet_elementleri:
                # Ekranda yüklenmiş olan EN SON tweeti bul ve tam olarak onun üzerine kaydır
                son_tweet = tweet_elementleri[-1]
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", son_tweet)
                time.sleep(3) # Yeni tweetlerin gelmesi için bekle
            
            # Eğer yeni tweet eklenmediyse durma sayacını artır
            if len(gonderiler) == baslangic_sayisi:
                durma_sayaci += 1
                print("Yeni tweet yüklenmesi bekleniyor...")
                time.sleep(2)
            else:
                durma_sayaci = 0
                
        print("\n--- PANDAS İLE KAYIT ---")
        if gonderiler:
            df = pd.DataFrame(gonderiler.values())
            dosya_adi = f"twitter_{hedef_hesap}_verisi_genis.csv"
            df.to_csv(dosya_adi, index=False, encoding='utf-8-sig')
            
            print("\n--- ÇEKİLEN VERİNİN İLK 5 SATIRI ---")
            print(df.head())
            print(f"\n🎉 Zafer! Toplam {len(gonderiler)} tweet '{dosya_adi}' dosyasına kaydedildi!")
        else:
            print("❌ Hiç tweet toplanamadı.")
            
    except Exception as e:
        print(f"Kritik Hata: {e}")
    finally:
        driver.quit()
        print("Tarayıcı kapatıldı.")

if __name__ == '__main__':
    nihai_twitter_kaziyici()