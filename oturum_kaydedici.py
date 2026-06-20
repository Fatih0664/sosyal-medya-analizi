from playwright.sync_api import sync_playwright

def oturum_kaydet():
    print("🔐 Instagram oturum açma penceresi başlatılıyor...")
    with sync_playwright() as p:
        # Tarayıcıyı görünür şekilde açıyoruz ki sen giriş yapabilesin
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://www.instagram.com/accounts/login/")
        print("\n⏳ Lütfen açılan tarayıcıda kendi hesabınıza (veya yedek bir hesaba) giriş yapın.")
        print("Giriş işlemi tamamen bitip ana sayfayı gördükten sonra buraya dönün ve ENTER'a basın...")
        
        input() # Sen ENTER'a basana kadar bot burada bekler
        
        # Giriş yapıldıktan sonra tüm dijital kimliği (Çerezleri) kaydet
        context.storage_state(path="instagram_oturum.json")
        print("\n✅ Şahane! Dijital kimliğiniz 'instagram_oturum.json' dosyasına başarıyla enjekte edildi!")
        browser.close()

if __name__ == "__main__":
    oturum_kaydet()
