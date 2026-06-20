from playwright.sync_api import sync_playwright

def fb_mobil_oturum_kaydet():
    print("🔐 Facebook MOBİL oturum açma penceresi başlatılıyor...")
    with sync_playwright() as p:
        # Doğrudan mobil cihaz emülasyonu yapıyoruz
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 375, 'height': 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        )
        page = context.new_page()
        
        # Doğrudan mobil giriş sayfasına gidiyoruz
        page.goto("https://m.facebook.com/login/")
        print("\n⏳ Lütfen açılan MOBİL pencerede Facebook hesabınıza giriş yapın.")
        print("Giriş yapıp ana sayfayı (akışı) net olarak gördükten sonra buraya dönün ve ENTER'a basın...")
        
        input()
        context.storage_state(path="facebook_oturum.json")
        print("\n✅ Muazzam! Mobil dijital kimliğiniz 'facebook_oturum.json' dosyasına tam uyumlu işlendi!")
        browser.close()

if __name__ == "__main__":
    fb_mobil_oturum_kaydet()
