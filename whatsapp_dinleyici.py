from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd

def whatsapp_dinleyici():
    print("🚀 WhatsApp Canlı Mesaj Dinleyici başlatılıyor...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    driver = webdriver.Chrome(options=options)
    print("WhatsApp Web takip ediliyor. Yeni mesajlar bekleniyor...")
    
    dinlenen_mesajlar = set() # Aynı mesajı tekrar kaydetmemek için set kullanıyoruz
    
    try:
        while True:
            # WhatsApp'taki mesaj etiketlerini bul
            mesaj_elementleri = driver.find_elements(By.CSS_SELECTOR, "div[data-pre-plain-text]")
            
            for mesaj in mesaj_elementleri:
                veri = mesaj.get_attribute("data-pre-plain-text")
                metin = mesaj.text
                
                if veri not in dinlenen_mesajlar:
                    # Veriyi parçalıyoruz: [Tarih/Saat] Gönderen:
                    print(f"\n📩 YENİ MESAJ YAKALANDI!")
                    print(f"{veri} {metin}")
                    
                    # Veriyi CSV'ye anlık ekle (append modu)
                    with open("whatsapp_mesajlar.csv", "a", encoding="utf-8-sig") as f:
                        f.write(f"{veri.replace('[', '').replace(']', '')},{metin.replace(',', ';')}\n")
                    
                    dinlenen_mesajlar.add(veri)
            
            time.sleep(2) # CPU'yu yormamak için kısa bekleme
            
    except KeyboardInterrupt:
        print("\n🛑 Dinleme durduruldu.")

if __name__ == '__main__':
    whatsapp_dinleyici()