import streamlit as st
import pandas as pd
from supabase import create_client
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime
import io

# --- ÇOKLU DİL SÖZLÜĞÜ ---
DIL_SECENEKLERI = {
    "Türkçe": {
        "title": "Web ve Sosyal Medya Analizi",
        "home_tab": "🏠 Ana Sayfa",
        "lang_select": "🌐 Dil Seçimi / Language",
        "country_select": "🗺️ Ülke Filtresi",
        "cat_select": "📂 Konu Filtresi",
        "all_countries": "Tüm Dünya",
        "all_cats": "Tüm Konular",
        "total": "📌 Toplam Çekilen Veri",
        "pos": "🟢 Pozitif İçerik",
        "neg": "🔴 Negatif İçerik",
        "neu": "⚪ Nötr İçerik",
        "chart_plat": "📊 Platform Dağılımı",
        "chart_cat": "📂 Konu Dağılımı",
        "chart_emo": "🎯 Duygu Dağılımı",
        "wordcloud": "☁️ En Çok Geçen Kelimeler",
        "table": "🔍 Filtrelenmiş Canlı Veriler",
        "download": "📥 Bu Verileri Excel Olarak İndir",
        "no_filter": "Bu platformda veya seçilen filtrelerde henüz veri bulunamadı.",
        "no_data": "Veritabanında henüz veri yok."
    },
    "English": {
        "title": "Web and Social Media Analysis",
        "home_tab": "🏠 Home",
        "lang_select": "🌐 Language",
        "country_select": "🗺️ Country Filter",
        "cat_select": "📂 Topic Filter",
        "all_countries": "Whole World",
        "all_cats": "All Topics",
        "total": "📌 Total Data",
        "pos": "🟢 Positive",
        "neg": "🔴 Negative",
        "neu": "⚪ Neutral",
        "chart_plat": "📊 Platform Distribution",
        "chart_cat": "📂 Topic Distribution",
        "chart_emo": "🎯 Sentiment",
        "wordcloud": "☁️ Word Cloud",
        "table": "🔍 Live Data",
        "download": "📥 Download as Excel",
        "no_filter": "No data found for this platform or filter.",
        "no_data": "No data in the database yet."
    },
    "Deutsch": {
        "title": "Web- und Social-Media-Analyse",
        "home_tab": "🏠 Startseite",
        "lang_select": "🌐 Sprache",
        "country_select": "🗺️ Land Filter",
        "cat_select": "📂 Thema Filter",
        "all_countries": "Ganze Welt",
        "all_cats": "Alle Themen",
        "total": "📌 Gesamtdaten",
        "pos": "🟢 Positiv",
        "neg": "🔴 Negativ",
        "neu": "⚪ Neutral",
        "chart_plat": "📊 Plattformverteilung",
        "chart_cat": "📂 Themenverteilung",
        "chart_emo": "🎯 Stimmung",
        "wordcloud": "☁️ Wortwolke",
        "table": "🔍 Live-Daten",
        "download": "📥 Als Excel herunterladen",
        "no_filter": "Keine Daten gefunden.",
        "no_data": "Noch keine Daten in der Datenbank."
    },
    "Français": {
        "title": "Analyse du Web et des Réseaux Sociaux",
        "home_tab": "🏠 Accueil",
        "lang_select": "🌐 Langue",
        "country_select": "🗺️ Filtre Pays",
        "cat_select": "📂 Filtre Sujet",
        "all_countries": "Monde Entier",
        "all_cats": "Tous les Sujets",
        "total": "📌 Données Totales",
        "pos": "🟢 Positif",
        "neg": "🔴 Négatif",
        "neu": "⚪ Neutre",
        "chart_plat": "📊 Plateformes",
        "chart_cat": "📂 Sujets",
        "chart_emo": "🎯 Sentiments",
        "wordcloud": "☁️ Nuage de mots",
        "table": "🔍 Données en direct",
        "download": "📥 Télécharger en Excel",
        "no_filter": "Aucune donnée trouvée.",
        "no_data": "Aucune donnée dans la base."
    },
    "中文": {
        "title": "网络和社交媒体分析",
        "home_tab": "🏠 首页",
        "lang_select": "🌐 语言",
        "country_select": "🗺️ 国家筛选",
        "cat_select": "📂 主题筛选",
        "all_countries": "全世界",
        "all_cats": "所有主题",
        "total": "📌 总数据",
        "pos": "🟢 正面",
        "neg": "🔴 负面",
        "neu": "⚪ 中立",
        "chart_plat": "📊 平台分布",
        "chart_cat": "📂 主题分布",
        "chart_emo": "🎯 情绪",
        "wordcloud": "☁️ 词云",
        "table": "🔍 实时数据",
        "download": "📥 下载 Excel",
        "no_filter": "未找到数据。",
        "no_data": "尚无数据。"
    },
    "العربية": {
        "title": "تحليل الويب ووسائل التواصل الاجتماعي",
        "home_tab": "🏠 الرئيسية",
        "lang_select": "🌐 اللغة",
        "country_select": "🗺️ تصفية الدولة",
        "cat_select": "📂 تصفية الموضوع",
        "all_countries": "جميع أنحاء العالم",
        "all_cats": "جميع المواضيع",
        "total": "📌 إجمالي البيانات",
        "pos": "🟢 إيجابي",
        "neg": "🔴 سلبي",
        "neu": "⚪ محايد",
        "chart_plat": "📊 المنصات",
        "chart_cat": "📂 المواضيع",
        "chart_emo": "🎯 المشاعر",
        "wordcloud": "☁️ سحابة الكلمات",
        "table": "🔍 البيانات الحية",
        "download": "📥 تحميل Excel",
        "no_filter": "لم يتم العثور على بيانات.",
        "no_data": "لا توجد بيانات."
    }
}

# Sabit Listeler
TUM_PLATFORMLAR = ["Google", "Bing", "Yahoo", "Instagram", "Facebook", "X (Twitter)", "TikTok", "YouTube", "Telegram", "WhatsApp"]
ULKELER = ["Türkiye", "ABD", "Almanya", "İngiltere", "Fransa", "Rusya", "Çin", "Japonya", "Güney Kore", "İtalya", "Brezilya", "Hindistan", "Mısır", "Suudi Arabistan"]

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Web ve Sosyal Medya Analizi", page_icon="🌍", layout="wide")

secilen_dil = st.sidebar.selectbox("🌐 Dil Seçimi / Language", options=list(DIL_SECENEKLERI.keys()))
lang = DIL_SECENEKLERI[secilen_dil]

st.title(lang["title"])

# --- SUPABASE BAĞLANTISI ---
SUPABASE_URL = "https://oskhluimvjvjhbtjqnoo.supabase.co"
SUPABASE_KEY = "sb_secret_MsMqFI2v9VF68mf6MyKhTg_wLLrlTky"

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase = init_connection()

@st.cache_data(ttl=60)
def veri_getir():
    if supabase is None: return pd.DataFrame()
    try:
        response = supabase.table("sosyal_medya_akis").select("*").order("created_at", desc=True).limit(5000).execute()
        df = pd.DataFrame(response.data)
        if not df.empty and 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
            if 'ulke' not in df.columns:
                df['ulke'] = "Türkiye"
        return df
    except:
        return pd.DataFrame()

df = veri_getir()

# --- GRAFİK ÇİZİCİ YARDIMCI FONKSİYONLAR ---
def duygu_pastasi_ciz(veri_df):
    duygu_sayilari = veri_df['duygu_durumu'].value_counts()
    fig, ax = plt.subplots(figsize=(5, 5))
    renkler = ['#2ecc71' if 'Pozitif' in e else '#e74c3c' if 'Negatif' in e else '#bdc3c7' for e in duygu_sayilari.index]
    ax.pie(duygu_sayilari, labels=duygu_sayilari.index, autopct='%1.1f%%', startangle=90, colors=renkler)
    ax.axis('equal') 
    st.pyplot(fig)

def kelime_bulutu_ciz(veri_df):
    tum_metin = " ".join(veri_df['icerik'].dropna().astype(str).tolist())
    if len(tum_metin) > 20:
        wordcloud = WordCloud(width=800, height=300, background_color="white", max_words=100, colormap="viridis").generate(tum_metin)
        fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
        ax_wc.imshow(wordcloud, interpolation="bilinear")
        ax_wc.axis("off")
        st.pyplot(fig_wc)
    else:
        st.info("Kelime bulutu oluşturmak için yeterli metin verisi yok.")

# PANOLARI ÇİZEN ANA MOTOR (Her sekme bunu kullanır)
def dashboard_olustur(veri_df, sayfa_ismi, ana_sayfa_mi=False):
    if veri_df.empty:
        st.warning(lang["no_filter"])
        return

    # METRİKLER
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(lang["total"], len(veri_df))
    col2.metric(lang["pos"], len(veri_df[veri_df['duygu_durumu'].str.contains('Pozitif', na=False)]))
    col3.metric(lang["neg"], len(veri_df[veri_df['duygu_durumu'].str.contains('Negatif', na=False)]))
    col4.metric(lang["neu"], len(veri_df[veri_df['duygu_durumu'].str.contains('Nötr', na=False)]))
    st.markdown("---")
    
    # GRAFİKLER
    if ana_sayfa_mi:
        # Ana Sayfada platform dağılımı da görünür
        g1, g2 = st.columns(2)
        with g1:
            st.subheader(lang["chart_plat"])
            st.bar_chart(veri_df['platform'].value_counts().reindex(TUM_PLATFORMLAR, fill_value=0))
        with g2:
            st.subheader(lang["chart_cat"])
            st.bar_chart(veri_df['kategori'].value_counts())
        st.markdown("---")
        g3, g4 = st.columns(2)
        with g3:
            st.subheader(lang["chart_emo"])
            duygu_pastasi_ciz(veri_df)
        with g4:
            st.subheader(lang["wordcloud"])
            kelime_bulutu_ciz(veri_df)
    else:
        # Tek platform sayfasında platform grafiğine gerek yoktur
        g1, g2 = st.columns(2)
        with g1:
            st.subheader(lang["chart_cat"])
            st.bar_chart(veri_df['kategori'].value_counts())
        with g2:
            st.subheader(lang["chart_emo"])
            duygu_pastasi_ciz(veri_df)
        st.markdown("---")
        st.subheader(lang["wordcloud"])
        kelime_bulutu_ciz(veri_df)

    st.markdown("---")
    
    # VERİ TABLOSU VE EXCEL BUTONU
    st.subheader(lang["table"])
    st.dataframe(veri_df[['created_at', 'ulke', 'platform', 'kategori', 'duygu_durumu', 'duygu_skoru', 'icerik']], use_container_width=True)
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        veri_df.to_excel(writer, index=False, sheet_name=sayfa_ismi)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label=lang["download"] + f" ({sayfa_ismi})",
        data=buffer.getvalue(),
        file_name=f'{sayfa_ismi}_Raporu_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        key=f"dl_btn_{sayfa_ismi}"  # Butonların çakışmaması için benzersiz anahtar
    )


# --- ANA İŞLEYİŞ (SEKMELER) ---
if not df.empty:
    st.sidebar.markdown("---")
    
    # Yan Menü (Global Filtreler - Tüm sekmeleri etkiler)
    ulke_secenekleri = [lang["all_countries"]] + ULKELER
    secilen_ulke = st.sidebar.selectbox(lang["country_select"], options=ulke_secenekleri)
    
    kategori_secenekleri = [lang["all_cats"]] + list(df['kategori'].unique())
    secilen_kategori = st.sidebar.selectbox(lang["cat_select"], options=kategori_secenekleri)
    
    # Global Filtreyi Uygula
    filtrelenmis_df = df.copy()
    if secilen_ulke != lang["all_countries"]:
        filtrelenmis_df = filtrelenmis_df[filtrelenmis_df['ulke'] == secilen_ulke]
    if secilen_kategori != lang["all_cats"]:
        filtrelenmis_df = filtrelenmis_df[filtrelenmis_df['kategori'] == secilen_kategori]

    # SEKMELERİ (BUTONLARI) OLUŞTUR
    sekme_isimleri = [lang["home_tab"]] + TUM_PLATFORMLAR
    sekmeler = st.tabs(sekme_isimleri)

    # 1. SEKME: ANA SAYFA
    with sekmeler[0]:
        dashboard_olustur(filtrelenmis_df, "Genel_Analiz", ana_sayfa_mi=True)

    # DİĞER SEKMELER: 10 PLATFORM
    for i, platform_adi in enumerate(TUM_PLATFORMLAR):
        with sekmeler[i+1]: # i+1 çünkü 0. indeks Ana Sayfa
            # Veriyi sadece o sekmeye ait platform için daraltıyoruz
            platform_ozel_df = filtrelenmis_df[filtrelenmis_df['platform'] == platform_adi]
            dashboard_olustur(platform_ozel_df, platform_adi, ana_sayfa_mi=False)

else:
    st.warning(lang["no_data"])