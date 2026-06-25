import streamlit as st
import pandas as pd
from supabase import create_client
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dijital İstihbarat Panosu", page_icon="🌍", layout="wide")

st.title("🌍 Dijital İstihbarat ve Sosyal Medya Analiz Panosu")
st.markdown("Bu pano, arka planda çalışan botun Supabase'e kaydettiği verileri canlı olarak gösterir.")

# --- SUPABASE BAĞLANTISI ---
SUPABASE_URL = "https://oskhluimvjvjhbtjqnoo.supabase.co"
SUPABASE_KEY = "sb_secret_MsMqFI2v9VF68mf6MyKhTg_wLLrlTky"

# Streamlit için bağlantıyı önbelleğe alıyoruz ki her yenilemede baştan bağlanmasın
@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Supabase bağlantı hatası: {e}")
        return None

supabase = init_connection()

# --- VERİ ÇEKME FONKSİYONU ---
# ttl=60 demek, veriyi 60 saniyede bir yenile demek (Render sunucusunu yormamak için)
@st.cache_data(ttl=60)
def veri_getir():
    if supabase is None:
        return pd.DataFrame()
        
    try:
        # Veritabanından en yeni 500 kaydı çekiyoruz
        response = supabase.table("sosyal_medya_akis").select("*").order("created_at", desc=True).limit(500).execute()
        df = pd.DataFrame(response.data)
        
        # Tarih formatını daha okunaklı hale getirelim
        if not df.empty and 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
        return df
    except Exception as e:
        st.error(f"Veri çekilirken hata oluştu: {e}")
        return pd.DataFrame()

# --- ARAYÜZ (DASHBOARD) ---
st.write("Veriler Supabase bulutundan canlı olarak çekiliyor... ⏳")
df = veri_getir()

if not df.empty:
    # 1. ÜST KISIM: Özet Metrikler
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    toplam_veri = len(df)
    pozitif_veri = len(df[df['duygu_durumu'].str.contains('Pozitif', na=False)])
    negatif_veri = len(df[df['duygu_durumu'].str.contains('Negatif', na=False)])
    notr_veri = len(df[df['duygu_durumu'].str.contains('Nötr', na=False)])
    
    col1.metric("📌 Toplam Çekilen Veri", toplam_veri)
    col2.metric("🟢 Pozitif İçerik", pozitif_veri)
    col3.metric("🔴 Negatif İçerik", negatif_veri)
    col4.metric("⚪ Nötr İçerik", notr_veri)
    
    st.markdown("---")
    
    # 2. ORTA KISIM: Platformlara Göre Dağılım Grafiği
    st.subheader("📊 Platformlara Göre İçerik Dağılımı")
    platform_sayilari = df['platform'].value_counts()
    st.bar_chart(platform_sayilari)
    
    # 3. ALT KISIM: Canlı Veri Akışı Tablosu
    st.subheader("🔍 Son Gelen Canlı Veriler")
    
    # Ekranda daha şık görünmesi için sütunları seçip sıralıyoruz
    gosterilecek_tablo = df[['created_at', 'platform', 'kategori', 'duygu_durumu', 'duygu_skoru', 'icerik']]
    st.dataframe(gosterilecek_tablo, use_container_width=True, height=400)
    
    st.caption("Not: Sonuçları yenilemek için sayfayı tazeleyebilirsiniz (Veriler 60 saniyede bir güncellenir).")

else:
    st.warning("Henüz veritabanında gösterilecek taze veri yok veya veri çekilemedi. Lütfen botun biraz daha veri toplamasını bekleyin.")