import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os
import pandas as pd
import sqlite3 # Veritabanı işlemleri için eklendi

# Veritabanına bağlanıp verileri kaydeden fonksiyon
def veritabanina_kaydet(veriler_listesi):
    conn = sqlite3.connect('turkiye_veri_agi.db')
    cursor = conn.cursor()
    
    eklenen_sayi = 0
    for veri in veriler_listesi:
        # Tarih ve etkileşimi kaybetmemek için içerik metninin içine şıkça gömüyoruz
        zengin_icerik = f"[{veri['tarih']}] {veri['metin']} (Beğeni: {veri['etkilesim']})"
        
        # Veritabanında aynı metin var mı diye kontrol et (Çift kaydı önlemek için)
        cursor.execute("SELECT id FROM sosyal_medya_akis WHERE icerik = ?", (zengin_icerik,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO sosyal_medya_akis (platform, icerik)
                VALUES (?, ?)
            ''', (veri['platform'], zengin_icerik))
            eklenen_sayi += 1
            
    conn.commit()
    conn.close()
    return eklenen_sayi

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
                            'platform': 'X/Twitter', # İsmi dashboard için güncelledik
                            'metin': tweet_metin.replace('\n', ' '), # Metni kesmeden tamamını alıyoruz
                            'etkilesim': tweet_etkilesim
                        }
                        print(f"[{len(gonderiler)}/{hedef_tweet_sayisi}] Yeni tweet yakalandı.")
                    
                    if len(gonderiler) >= hedef_tweet_sayisi:
                        break
                        
                except Exception:
                    continue 
            
            if len(gonderiler) >= hedef_tweet_sayisi:
                break
            
            # --- 2. HİLE: GÜVENLİ KAYDIRMA ---
            try:
                # Belirli bir tweete tutunmak yerine doğrudan pencereyi aşağı kaydırıyoruz
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3.5) # Twitter'ın yeni verileri yüklemesi için zaman veriyoruz
            except Exception as e:
                print(f"Kaydırma sırasında küçük bir takılma: {e}")
                
            # Eğer yeni tweet eklenmediyse durma sayacını artır (Sonsuz döngüyü engellemek için)
            if len(gonderiler) == baslangic_sayisi:
                durma_sayaci += 1
                print("Yeni tweet yüklenmesi bekleniyor...")
                time.sleep(2)
            else:
                durma_sayaci = 0
                
        print("\n--- VERİTABANINA KAYIT ---")
        if gonderiler:
            veriler_listesi = list(gonderiler.values())
            
            # Veritabanına kaydetme fonksiyonunu çağırıyoruz
            eklenen_kayit = veritabanina_kaydet(veriler_listesi)
            
            # İsteğe bağlı olarak CSV yedeğini de tutmaya devam ediyoruz (Opsiyonel ama güvenli)
            df = pd.DataFrame(veriler_listesi)
            df.to_csv(f"twitter_{hedef_hesap}_yedek.csv", index=False, encoding='utf-8-sig')
            
            print(f"\n🎉 Zafer! Toplam {len(gonderiler)} tweet çekildi.")
            print(f"💾 {eklenen_kayit} yeni tweet veritabanına eklendi (Zaten var olanlar atlandı).")
        else:
            print("❌ Hiç tweet toplanamadı.")
            
    except Exception as e:
        print(f"Kritik Hata: {e}")
    finally:
        driver.quit()
        print("Tarayıcı kapatıldı.")

if __name__ == '__main__':
    nihai_twitter_kaziyici()