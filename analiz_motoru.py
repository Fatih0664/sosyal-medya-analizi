import sqlite3
import pandas as pd
from datetime import datetime

def istihbarat_raporu_olustur(db_yolu="turkiye_veri_agi.db", rapor_adi="Gunluk_Istihbarat_Raporu.xlsx"):
    print("🔍 Veritabanına bağlanılıyor...")
    
    try:
        # 1. Veritabanı Bağlantısı ve Veri Çekimi
        conn = sqlite3.connect(db_yolu)
        
        # DİKKAT: Buradaki SQL sorgusunu kendi tablo (örneğin: 'veriler') ve sütun isimlerine göre güncelle.
        # Örnek sütunlar: platform, icerik, tarih, duygu_skoru
        sorgu = "SELECT platform, olusturulma_tarihi AS tarih, duygu_skoru FROM sosyal_medya_akis"
        df = pd.read_sql_query(sorgu, conn)
        conn.close()

        if df.empty:
            print("⚠️ Veritabanında analiz edilecek veri bulunamadı!")
            return

        print(f"✅ Toplam {len(df)} satır veri başarıyla çekildi. Analiz başlıyor...")

        # 2. Veri Ön İşleme (Tarih formatını standartlaştırma)
        # Tarih sütununu sadece "Yıl-Ay-Gün" formatına getiriyoruz ki günlük gruplama yapabilelim
        df['tarih'] = pd.to_datetime(df['tarih']).dt.date

        # 3. İstatistiksel Hesaplamalar ve Zaman Serisi
        # A. Platformlara göre günlük mesaj/içerik sayısı (Frekans)
        gunluk_frekans = df.groupby(['tarih', 'platform']).size().unstack(fill_value=0)
        
        # B. Platformlara göre günlük ortalama duygu skoru
        gunluk_duygu = df.groupby(['tarih', 'platform'])['duygu_skoru'].mean().unstack(fill_value=0)

        # C. 7 Günlük Hareketli Ortalama (Trendleri daha net görmek için)
        frekans_sma_7 = gunluk_frekans.rolling(window=7, min_periods=1).mean()

        # 4. Excel'e Çok Sekmeli Yazdırma İşlemi
        print("📈 Excel raporu derleniyor...")
        with pd.ExcelWriter(rapor_adi, engine='xlsxwriter') as writer:
            # Sekmeleri oluştur
            gunluk_frekans.to_excel(writer, sheet_name='Günlük Frekans')
            gunluk_duygu.to_excel(writer, sheet_name='Ortalama Duygu Skoru')
            frekans_sma_7.to_excel(writer, sheet_name='7 Günlük Hareketli Ortalama')
            
            # İsteğe bağlı: Excel formatını güzelleştirme (Sütun genişliklerini ayarlama vs.)
            for sheet in writer.sheets:
                writer.sheets[sheet].set_column('A:Z', 15) # Sütunları 15 birim genişletir

        print(f"🎉 İşlem tamam! Rapor başarıyla oluşturuldu: {rapor_adi}")

    except Exception as e:
        print(f"❌ Bir hata oluştu: {e}")

if __name__ == "__main__":
    # Test etmek için fonksiyonu doğrudan çalıştırıyoruz
    istihbarat_raporu_olustur()
