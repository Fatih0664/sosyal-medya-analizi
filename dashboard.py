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
        "lang_select": "🌐 Dil Seçimi / Language",
        "plat_select": "🔍 Platform Seçin:",
        "cat_select": "📂 Kategori Seçin:",
        "total": "📌 Toplam Çekilen Veri",
        "pos": "🟢 Pozitif İçerik",
        "neg": "🔴 Negatif İçerik",
        "neu": "⚪ Nötr İçerik",
        "chart_plat": "📊 Platform Dağılımı",
        "chart_emo": "🎯 Duygu Dağılımı (Pasta Grafik)",
        "wordcloud": "☁️ En Çok Geçen Kelimeler",
        "table": "🔍 Filtrelenmiş Canlı Veriler",
        "download": "📥 Bu Tabloyu Excel Olarak İndir",
        "no_filter": "Seçilen filtrelere uygun veri bulunamadı.",
        "no_data": "Veritabanında henüz veri yok."
    },
    "English": {
        "title": "Web and Social Media Analysis",
        "lang_select": "🌐 Language",
        "plat_select": "🔍 Select Platform:",
        "cat_select": "📂 Select Category:",
        "total": "📌 Total Extracted Data",
        "pos": "🟢 Positive Content",
        "neg": "🔴 Negative Content",
        "neu": "⚪ Neutral Content",
        "chart_plat": "📊 Platform Distribution",
        "chart_emo": "🎯 Sentiment Distribution",
        "wordcloud": "☁️ Most Frequent Words",
        "table": "🔍 Filtered Live Data",
        "download": "📥 Download Table as Excel",
        "no_filter": "No data found for the selected filters.",
        "no_data": "No data in the database yet."
    },
    "Deutsch": {
        "title": "Web- und Social-Media-Analyse",
        "lang_select": "🌐 Sprache",
        "plat_select": "🔍 Plattform wählen:",
        "cat_select": "📂 Kategorie wählen:",
        "total": "📌 Gesamtdaten",
        "pos": "🟢 Positiver Inhalt",
        "neg": "🔴 Negativer Inhalt",
        "neu": "⚪ Neutraler Inhalt",
        "chart_plat": "📊 Plattformverteilung",
        "chart_emo": "🎯 Stimmungsverteilung",
        "wordcloud": "☁️ Häufigste Wörter",
        "table": "🔍 Gefilterte Live-Daten",
        "download": "📥 Als Excel herunterladen",
        "no_filter": "Keine Daten für diese Filter gefunden.",
        "no_data": "Noch keine Daten in der Datenbank."
    },
    "Français": {
        "title": "Analyse du Web et des Réseaux Sociaux",
        "lang_select": "🌐 Langue",
        "plat_select": "🔍 Choisir la plateforme:",
        "cat_select": "📂 Choisir la catégorie:",
        "total": "📌 Données Totales",
        "pos": "🟢 Contenu Positif",
        "neg": "🔴 Contenu Négatif",
        "neu": "⚪ Contenu Neutre",
        "chart_plat": "📊 Distribution des Plateformes",
        "chart_emo": "🎯 Distribution des Sentiments",
        "wordcloud": "☁️ Mots les plus fréquents",
        "table": "🔍 Données en direct filtrées",
        "download": "📥 Télécharger en Excel",
        "no_filter": "Aucune donnée trouvée pour ces filtres.",
        "no_data": "Aucune donnée dans la base de données."
    },
    "中文": {
        "title": "网络和社交媒体分析",
        "lang_select": "🌐 语言",
        "plat_select": "🔍 选择平台：",
        "cat_select": "📂 选择类别：",
        "total": "📌 提取的数据总数",
        "pos": "🟢 正面内容",
        "neg": "🔴 负面内容",
        "neu": "⚪ 中立内容",
        "chart_plat": "📊 平台分布",
        "chart_emo": "🎯 情绪分布",
        "wordcloud": "☁️ 最常出现的词",
        "table": "🔍 过滤后的实时数据",
        "download": "📥 下载为 Excel 表格",
        "no_filter": "未找到符合所选过滤器的数据。",
        "no_data": "数据库中尚无数据。"
    },
    "العربية": {
        "title": "تحليل الويب ووسائل التواصل الاجتماعي",
        "lang_select": "🌐 اللغة",
        "plat_select": "🔍 اختر المنصة:",
        "cat_select": "📂 اختر الفئة:",
        "total": "📌 إجمالي البيانات المستخرجة",
        "pos": "🟢 محتوى إيجابي",
        "neg": "🔴 محتوى سلبي",
        "neu": "⚪ محتوى محايد",
        "chart_plat": "📊 توزيع المنصات",
        "chart_emo": "🎯 توزيع المشاعر",
        "wordcloud": "☁️ الكلمات الأكثر تكراراً",
        "table": "🔍 البيانات الحية المفلترة",
        "download": "📥 تحميل كملف Excel",
        "no_filter": "لم يتم العثور على بيانات تطابق الفلاتر.",
        "no_data": "لا توجد بيانات جديدة في قاعدة البيانات."
    }
}

# 10 Sabit Platform
TUM_PLATFORMLAR = ["Google", "Bing", "Yahoo", "Facebook", "YouTube", "X (Twitter)", "Telegram", "Instagram", "TikTok", "WhatsApp"]

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Web ve Sosyal Medya Analizi", page_icon="🌍", layout="wide")

# YAN MENÜ: Dil Seçimi
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
        response = supabase.table("sosyal_medya_akis").select("*").order("created_at", desc=True).limit(500).execute()
        df = pd.DataFrame(response.data)
        if not df.empty and 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
        return df
    except:
        return pd.DataFrame()

df = veri_getir()

if not df.empty:
    # --- YAN MENÜ (FİLTRELEME) ---
    st.sidebar.markdown("---")
    
    # Tüm 10 platformu sabit olarak gösteriyoruz
    secilen_platformlar = st.sidebar.multiselect(
        lang["plat_select"],
        options=TUM_PLATFORMLAR,
        default=TUM_PLATFORMLAR
    )
    
    secilen_kategoriler = st.sidebar.multiselect(
        lang["cat_select"],
        options=df['kategori'].unique(),
        default=df['kategori'].unique()
    )
    
    filtrelenmis_df = df[
        (df['platform'].isin(secilen_platformlar)) & 
        (df['kategori'].isin(secilen_kategoriler))
    ]
    
    if filtrelenmis_df.empty:
        st.warning(lang["no_filter"])
    else:
        # --- Özet Metrikler ---
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric(lang["total"], len(filtrelenmis_df))
        col2.metric(lang["pos"], len(filtrelenmis_df[filtrelenmis_df['duygu_durumu'].str.contains('Pozitif', na=False)]))
        col3.metric(lang["neg"], len(filtrelenmis_df[filtrelenmis_df['duygu_durumu'].str.contains('Negatif', na=False)]))
        col4.metric(lang["neu"], len(filtrelenmis_df[filtrelenmis_df['duygu_durumu'].str.contains('Nötr', na=False)]))
        
        st.markdown("---")
        
        # --- Grafikler ---
        grafik_kolon1, grafik_kolon2 = st.columns(2)
        
        with grafik_kolon1:
            st.subheader(lang["chart_plat"])
            st.bar_chart(filtrelenmis_df['platform'].value_counts())
            
        with grafik_kolon2:
            st.subheader(lang["chart_emo"])
            duygu_sayilari = filtrelenmis_df['duygu_durumu'].value_counts()
            fig, ax = plt.subplots(figsize=(5, 5))
            renkler = ['#2ecc71' if 'Pozitif' in e else '#e74c3c' if 'Negatif' in e else '#bdc3c7' for e in duygu_sayilari.index]
            ax.pie(duygu_sayilari, labels=duygu_sayilari.index, autopct='%1.1f%%', startangle=90, colors=renkler)
            ax.axis('equal') 
            st.pyplot(fig)
            
        st.markdown("---")
        
        # --- Kelime Bulutu ---
        st.subheader(lang["wordcloud"])
        tum_metin = " ".join(filtrelenmis_df['icerik'].dropna().astype(str).tolist())
        if len(tum_metin) > 20:
            wordcloud = WordCloud(width=800, height=300, background_color="white", max_words=100, colormap="viridis").generate(tum_metin)
            fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
            ax_wc.imshow(wordcloud, interpolation="bilinear")
            ax_wc.axis("off")
            st.pyplot(fig_wc)

        st.markdown("---")
        
        # --- Tablo ve Gerçek Excel (.xlsx) İndirme ---
        st.subheader(lang["table"])
        st.dataframe(filtrelenmis_df[['created_at', 'platform', 'kategori', 'duygu_durumu', 'duygu_skoru', 'icerik']], use_container_width=True)
        
        # Gerçek Excel Dosyası Oluşturma (openpyxl)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtrelenmis_df.to_excel(writer, index=False, sheet_name='Analiz Verileri')
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label=lang["download"],
            data=buffer.getvalue(),
            file_name=f'analiz_raporu_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
else:
    st.warning(lang["no_data"])