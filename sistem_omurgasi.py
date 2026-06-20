import re
import sqlite3  # <-- İŞTE SİSTEMİ KURTARAN EKLEME
from collections import Counter
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# --- 1. VERİTABANI ŞEMASI (POSTGRESQL HAZIRLIKLI SQLITE) ---
# Canlıya alırken burası: 'postgresql://kullanici:sifre@localhost/buyukveri' olacak
SQLALCHEMY_DATABASE_URL = "sqlite:///./turkiye_veri_agi.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Veritabanı Tablomuz (Milyonlarca satırı tutacak ana depo)
class SosyalVeri(Base):
    __tablename__ = "sosyal_medya_akis"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True) # Örn: Twitter, EksiSozluk, TikTok
    kategori = Column(String, index=True) # Örn: Teknoloji, Saglik, Siyaset
    icerik = Column(String)               # Kullanıcının yazdığı metin
    duygu_durumu = Column(String)         # Pozitif, Negatif, Nötr
    duygu_skoru = Column(Float)           # -1.0 ile 1.0 arası hassas skor
    olusturulma_tarihi = Column(DateTime, default=datetime.utcnow)

# Tabloları veritabanında fiziksel olarak yarat
Base.metadata.create_all(bind=engine)


# --- 2. FASTAPI OMURGASI (REST API) ---
app = FastAPI(title="TR Big Data API", description="Sosyal Medya Veri Toplama Merkezi")

# Botların API'ye veri gönderirken kullanacağı JSON şablonu (Pydantic Model)
class VeriPaketi(BaseModel):
    platform: str
    kategori: str
    icerik: str
    duygu_durumu: str
    duygu_skoru: float

# Uç Nokta 1: İşçi Botların Veri Yazacağı Kapı (Ingestion Endpoint)
@app.post("/api/v1/veri-gonder/", status_code=201)
def veri_kaydet(paket: VeriPaketi):
    db = SessionLocal()
    yeni_kayit = SosyalVeri(
        platform=paket.platform,
        kategori=paket.kategori,
        icerik=paket.icerik,
        duygu_durumu=paket.duygu_durumu,
        duygu_skoru=paket.duygu_skoru
    )
    db.add(yeni_kayit)
    db.commit()
    db.refresh(yeni_kayit)
    db.close()
    return {"mesaj": "Veri başarıyla merkeze eklendi", "id": yeni_kayit.id}

# Uç Nokta 2: Flutter Mobil Uygulamasının Veri Okuyacağı Kapı (Analytics Endpoint)
@app.get("/api/v1/trendler/{kategori}")
def trendleri_getir(kategori: str, limit: int = 100):
    db = SessionLocal()
    # Sadece istenen kategoriye ait son verileri getir
    veriler = db.query(SosyalVeri).filter(SosyalVeri.kategori == kategori).order_by(SosyalVeri.id.desc()).limit(limit).all()
    db.close()
    
    if not veriler:
        raise HTTPException(status_code=404, detail="Bu kategoride henüz veri yok")
    return veriler

@app.get("/api/v1/kelime-bulutu/")
def kelime_bulutu_analizi():
    try:
        # 1. Veritabanına bağlan ve tüm içerikleri çek
        conn = sqlite3.connect("turkiye_veri_agi.db")
        cursor = conn.cursor()
        cursor.execute("SELECT icerik FROM sosyal_medya_akis")
        veriler = cursor.fetchall()
        conn.close()

        # Tüm gönderileri devasa tek bir metin (string) haline getir
        tum_metin = " ".join([v[0] for v in veriler if v[0]])

        # 2. Veri Temizliği (Noktalama işaretlerini sil, sadece küçük harf yap)
        # İstatistiksel analizde büyük-küçük harf duyarlılığını ortadan kaldırıyoruz
        temiz_metin = re.sub(r'[^\w\s]', '', tum_metin).lower()

        # 3. Stop-Words (Gürültü) Filtresi
        # Toplumsal nabız ölçerken anlamsız bağlaçları çöpe atıyoruz
        gereksiz_kelimeler = {
            "bir", "ve", "bu", "da", "de", "için", "icin", "ile", "ama", "çok", 
            "gibi", "kadar", "olan", "olarak", "en", "daha", "var", "yok", "mi", 
            "mu", "ne", "o", "şu", "ki", "her", "biz", "siz", "onlar", "ben", 
            "sen", "mı", "mü", "ise", "ya", "hem", "hiç", "veya", "göre"
        }

        # Metni kelimelere ayır ve filtrele (2 harften kısa olanları da atla)
        kelimeler = temiz_metin.split()
        anlamli_kelimeler = [
            k for k in kelimeler 
            if k not in gereksiz_kelimeler and len(k) > 2 and not k.isnumeric()
        ]

        # 4. Frekans Hesaplama (En çok tekrar eden 40 kelimeyi yakala)
        frekans_dagilimi = Counter(anlamli_kelimeler).most_common(40)

        # 5. Flutter'ın rahatça okuyacağı JSON formatına dönüştür
        sonuc_paketi = [{"kelime": k[0], "frekans": k[1]} for k in frekans_dagilimi]
        
        return sonuc_paketi

    except Exception as e:
        return {"hata": str(e)}
