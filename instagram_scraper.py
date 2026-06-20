import instaloader
import pandas as pd
from datetime import datetime

def instagram_veri_cek(hedef_hesap, bot_kullanici_adi, bot_sifre, limit=50):
    print(f"[{hedef_hesap}] profiline bağlanılıyor...")
    
    L = instaloader.Instaloader()
    
    try:
        # Sisteme test hesabımızla giriş yapıyoruz
        print(f"'{bot_kullanici_adi}' hesabı ile giriş yapılıyor...")
        L.login(bot_kullanici_adi, bot_sifre)
        print("Giriş başarılı! Veriler çekiliyor...")
        
        # Profili getir
        profile = instaloader.Profile.from_username(L.context, hedef_hesap)
    except instaloader.exceptions.BadCredentialsException:
        print("Hata: Kullanıcı adı veya şifre yanlış.")
        return []
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        print("Hata: İki faktörlü doğrulama (2FA) açık. Lütfen 2FA olmayan bir test hesabı kullanın.")
        return []
    except Exception as e:
        print(f"Bağlantı/Giriş hatası: {e}")
        return []

    veriler = []
    sayac = 0
    
    for post in profile.get_posts():
        if sayac >= limit:
            break
            
        veriler.append({
            'tarih': post.date,
            'platform': 'Instagram',
            'metin': post.caption if post.caption else "", 
            'etkilesim': post.likes 
        })
        sayac += 1
        
        if sayac % 10 == 0:
            print(f"{sayac} gönderi çekildi...")
            
    return veriler

def ana_calistirici():
    hedef_hesap = 'webtekno'
    
    # BURAYA TEST HESABININ BİLGİLERİNİ GİRİN
    test_hesabi_kullanici_adi = "hoyratadamm"
    test_hesabi_sifresi = "64hoyrat1532"
    
    ham_veri_listesi = instagram_veri_cek(hedef_hesap, test_hesabi_kullanici_adi, test_hesabi_sifresi, limit=50)
    
    if ham_veri_listesi:
        print(f"\n{len(ham_veri_listesi)} adet gönderi başarıyla çekildi.")
        
        df = pd.DataFrame(ham_veri_listesi)
        df = df[['tarih', 'platform', 'metin', 'etkilesim']]
        
        print("\n--- ÇEKİLEN VERİNİN İLK 5 SATIRI ---")
        print(df.head())
        
        dosya_adi = f"instagram_{hedef_hesap}_verisi.csv"
        df.to_csv(dosya_adi, index=False, encoding='utf-8')
        print(f"\nVeriler başarıyla '{dosya_adi}' dosyasına kaydedildi!")
    else:
        print("\nVeri çekme işlemi başarısız oldu.")

if __name__ == '__main__':
    ana_calistirici()