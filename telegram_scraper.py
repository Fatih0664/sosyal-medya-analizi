from telethon.sync import TelegramClient
import pandas as pd
import datetime

# --- KİMLİK BİLGİLERİ ---
# Aşağıdaki alanları my.telegram.org'dan aldığınız bilgilerle doldurun
api_id = '34793610'      # Örnek: '12345678' (Tırnak içinde veya integer olabilir)
api_hash = '4afa2cb64c9202e71ee91ba26a4ee405'  # Örnek: '0123456789abcdef0123456789abcdef'
phone = '+905321597022'      # Telegram'a kayıtlı telefon numaranız (ülke koduyla)

# Hedef kanalın kullanıcı adı (örneğin: 'webtekno' veya 'kriptohaber')
hedef_kanal = 'webtekno' 
cekilecek_mesaj_sayisi = 50

async def veri_cek():
    # Telegram istemcisini başlatıyoruz ('session_name' adında bir dosya oluşturur)
    client = TelegramClient('benim_oturum', api_id, api_hash)
    await client.start(phone=phone)
    
    print(f"[{hedef_kanal}] kanalına bağlanılıyor...")
    
    veriler = []
    
    # Kanaldaki mesajları çekmeye başlıyoruz
    async for mesaj in client.iter_messages(hedef_kanal, limit=cekilecek_mesaj_sayisi):
        # Eğer mesajın metni varsa (sadece fotoğraf/video değilse) al
        if mesaj.text:
            veriler.append({
                'tarih': mesaj.date,
                'platform': 'Telegram',
                'metin': mesaj.text,
                'etkilesim': mesaj.views # Telegram'da etkileşim olarak görüntülenme sayısını alıyoruz
            })
            
    # İşimiz bitince istemciyi kapatıyoruz
    await client.disconnect()
    return veriler

def ana_calistirici():
    import asyncio
    
    # Asenkron fonksiyonu çalıştır
    ham_veri_listesi = asyncio.run(veri_cek())
    
    print(f"\n{len(ham_veri_listesi)} adet metin içeren mesaj başarıyla çekildi.")
    
    # --- VERİ NORMALİZASYONU VE PANDAS ---
    # Ham veriyi Pandas DataFrame'e dönüştürüyoruz
    df = pd.DataFrame(ham_veri_listesi)
    
    if not df.empty:
        # Tarih formatını analiz için düzenliyoruz (saat dilimi bilgisini temizleme)
        df['tarih'] = pd.to_datetime(df['tarih']).dt.tz_localize(None)
        
        # Sütun sırasını düzenleme
        df = df[['tarih', 'platform', 'metin', 'etkilesim']]
        
        print("\n--- ÇEKİLEN VERİNİN İLK 5 SATIRI ---")
        print(df.head())
        
        # İleriki analizler için veriyi bir CSV dosyasına kaydediyoruz
        dosya_adi = f"telegram_{hedef_kanal}_verisi.csv"
        df.to_csv(dosya_adi, index=False, encoding='utf-8')
        print(f"\nVeriler başarıyla '{dosya_adi}' dosyasına kaydedildi!")
    else:
        print("Kanaldan hiç metin mesajı çekilemedi.")

if __name__ == '__main__':
    ana_calistirici()