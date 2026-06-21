import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:fl_chart/fl_chart.dart';

void main() {
  runApp(const BigDataApp());
}

class BigDataApp extends StatelessWidget {
  const BigDataApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TR Trend Analizi',
      theme: ThemeData(primarySwatch: Colors.indigo, useMaterial3: true),
      home: const TrendEkrani(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class TrendEkrani extends StatefulWidget {
  const TrendEkrani({Key? key}) : super(key: key);

  @override
  _TrendEkraniState createState() => _TrendEkraniState();
}

class _TrendEkraniState extends State<TrendEkrani> {
  List<dynamic> tumVeriler = [];
  List<dynamic> gosterilecekVeriler = [];
  List<dynamic> kelimeBulutuVerisi = [];
  bool isLoading = true;
  String seciliFiltre = 'Tümü';

  final String apiUrl = "https://dijital-istihbarat-sistemi.onrender.com/api/v1/trendler/Teknoloji";
  final String kelimeBulutuUrl = "https://dijital-istihbarat-sistemi.onrender.com/api/v1/kelime-bulutu/";

  int pozitifSayisi = 0;
  int negatifSayisi = 0;
  int notrSayisi = 0;
  List<MapEntry<String, int>> topPlatformlar = [];

  @override
  void initState() {
    super.initState();
    verileriCek();
  }

  Future<void> verileriCek() async {
    setState(() { isLoading = true; });
    try {
      print("API İsteği Başlıyor: $apiUrl");
      
      final response = await http.get(
        Uri.parse(apiUrl),
        headers: {"Accept": "application/json"},
      ).timeout(const Duration(seconds: 60));
      
      print("API İsteği Bitti. Durum Kodu: ${response.statusCode}");
      print("Gelen Ham Veri: ${response.body}");

      final bulutResponse = await http.get(
        Uri.parse(kelimeBulutuUrl),
        headers: {"Accept": "application/json"},
      ).timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        tumVeriler = json.decode(response.body); 
        istatistikleriHesapla();
        filtreUygula('Tümü');
      } else {
        throw Exception("Trendler API Hatası: ${response.statusCode}");
      }
      
      if (bulutResponse.statusCode == 200) {
        kelimeBulutuVerisi = json.decode(bulutResponse.body);
      } else {
        throw Exception("Kelime Bulutu API Hatası: ${bulutResponse.statusCode}");
      }

    } catch (e) {
      print("!!! YAKALANAN HATA !!! : $e");
      
      if (mounted) {
        setState(() {
          tumVeriler = [
            {"icerik": "Uygulama çöktü sandık ama UI sağlammış.", "platform": "X", "duygu_skoru": 0.5, "duygu_durumu": "Pozitif"},
            {"icerik": "Bağlantı hatası var, çözülecek.", "platform": "Telegram", "duygu_skoru": -0.8, "duygu_durumu": "Negatif"}
          ];
          kelimeBulutuVerisi = [
            {"kelime": "Bağlantı", "frekans": 100},
            {"kelime": "Hata", "frekans": 50}
          ];
          istatistikleriHesapla();
          filtreUygula('Tümü');
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Veri çekilemedi, sahte veri yüklendi. Hata: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() { isLoading = false; });
      }
    }
  }

  void istatistikleriHesapla() {
    pozitifSayisi = tumVeriler.where((v) => v['duygu_durumu'].toString().contains('Pozitif')).length;
    negatifSayisi = tumVeriler.where((v) => v['duygu_durumu'].toString().contains('Negatif')).length;
    notrSayisi = tumVeriler.where((v) => v['duygu_durumu'].toString().contains('Nötr')).length;

    Map<String, int> platformSayilari = {};
    for (var v in tumVeriler) {
      String p = v['platform'].toString();
      if (p.contains('Facebook')) p = 'Facebook';
      else if (p.contains('Telegram')) p = 'Telegram';
      else if (p.contains('YouTube')) p = 'YouTube';
      else if (p.contains('Instagram')) p = 'Instagram';
      else if (p.contains('TikTok')) p = 'TikTok';
      else if (p.contains('WhatsApp')) p = 'WhatsApp';
      else p = 'Web/X'; 
      platformSayilari[p] = (platformSayilari[p] ?? 0) + 1;
    }

    topPlatformlar = platformSayilari.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    if (topPlatformlar.length > 5) topPlatformlar = topPlatformlar.sublist(0, 5);
  }

  void filtreUygula(String filtre) {
    setState(() {
      seciliFiltre = filtre;
      if (filtre == 'Tümü') {
        gosterilecekVeriler = List.from(tumVeriler);
      } else {
        gosterilecekVeriler = tumVeriler.where((v) => v['duygu_durumu'].toString().contains(filtre)).toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      appBar: AppBar(
        title: const Text('📊 İstihbarat Paneli', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.indigo.shade900,
        elevation: 1,
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: verileriCek)
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.only(bottom: 30),
              children: [
                const Padding(
                  padding: EdgeInsets.only(left: 16, top: 16, bottom: 8),
                  child: Text("Toplumsal Duygu Analizi", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.blueGrey)),
                ),
                _buildPieChartSection(),
                
                const Padding(
                  padding: EdgeInsets.only(left: 16, top: 8, bottom: 8),
                  child: Text("Veri Kaynakları (Top 5)", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.blueGrey)),
                ),
                _buildBarChartSection(),

                const Padding(
                  padding: EdgeInsets.only(left: 16, top: 16, bottom: 8),
                  child: Text("Gündem Radarı (Kelime Bulutu)", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.blueGrey)),
                ),
                _buildWordCloudSection(),

                const Padding(
                  padding: EdgeInsets.only(left: 16, top: 16, bottom: 8),
                  child: Text("Canlı Veri Akışı", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.blueGrey)),
                ),
                _buildFilterSection(),

                ...gosterilecekVeriler.map((veri) => _veriKartiOlustur(veri)).toList(),
              ],
            ),
    );
  }

  Widget _buildWordCloudSection() {
    if (kelimeBulutuVerisi.isEmpty) return const SizedBox();

    int maxFrekans = 1;
    for (var item in kelimeBulutuVerisi) {
      if ((item['frekans'] as int) > maxFrekans) {
        maxFrekans = item['frekans'] as int;
      }
    }

    return Container(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 10, offset: const Offset(0, 4))],
      ),
      child: Wrap(
        spacing: 12.0,
        runSpacing: 8.0,
        alignment: WrapAlignment.center,
        children: kelimeBulutuVerisi.map((item) {
          String kelime = item['kelime'];
          int frekans = item['frekans'];
          double fontSize = 12 + ((frekans / maxFrekans) * 24);
          Color renk = Colors.primaries[kelime.hashCode % Colors.primaries.length];

          return Text(
            kelime,
            style: TextStyle(
              fontSize: fontSize,
              fontWeight: FontWeight.bold,
              color: renk.withOpacity(0.85),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildBarChartSection() {
    if (topPlatformlar.isEmpty) return const SizedBox();
    return Container(
      height: 200,
      padding: const EdgeInsets.only(top: 24, right: 24, left: 16, bottom: 12),
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 10, offset: const Offset(0, 4))]),
      child: BarChart(
        BarChartData(
          alignment: BarChartAlignment.spaceAround,
          borderData: FlBorderData(show: false),
          gridData: FlGridData(show: false),
          titlesData: FlTitlesData(
            topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, getTitlesWidget: (value, meta) {
              if (value.toInt() >= 0 && value.toInt() < topPlatformlar.length) {
                return Padding(padding: const EdgeInsets.only(top: 8.0), child: Text(topPlatformlar[value.toInt()].key, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.indigo.shade400)));
              }
              return const Text('');
            }))
          ),
          barGroups: topPlatformlar.asMap().entries.map((entry) {
            return BarChartGroupData(x: entry.key, barRods: [BarChartRodData(toY: entry.value.value.toDouble(), color: Colors.indigo.shade300, width: 20, borderRadius: const BorderRadius.only(topLeft: Radius.circular(4), topRight: Radius.circular(4)))], showingTooltipIndicators: [0]);
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildPieChartSection() {
    int toplam = pozitifSayisi + negatifSayisi + notrSayisi;
    return Container(
      height: 180,
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 10, offset: const Offset(0, 4))]),
      child: Row(
        children: [
          Expanded(
            child: toplam == 0 
              ? const Center(child: Text("Veri Yok")) 
              : PieChart(PieChartData(sectionsSpace: 2, centerSpaceRadius: 35, sections: [
                  PieChartSectionData(color: Colors.green.shade400, value: pozitifSayisi.toDouble(), title: '%${((pozitifSayisi / toplam) * 100).toStringAsFixed(1)}', radius: 45, titleStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white)),
                  PieChartSectionData(color: Colors.red.shade400, value: negatifSayisi.toDouble(), title: '%${((negatifSayisi / toplam) * 100).toStringAsFixed(1)}', radius: 45, titleStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white)),
                  PieChartSectionData(color: Colors.grey.shade400, value: notrSayisi.toDouble(), title: '%${((notrSayisi / toplam) * 100).toStringAsFixed(1)}', radius: 45, titleStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white)),
                ])),
          ),
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _grafikLejant('Pozitif', Colors.green.shade400, pozitifSayisi),
              const SizedBox(height: 8),
              _grafikLejant('Negatif', Colors.red.shade400, negatifSayisi),
              const SizedBox(height: 8),
              _grafikLejant('Nötr', Colors.grey.shade400, notrSayisi),
            ],
          )
        ],
      ),
    );
  }

  Widget _grafikLejant(String baslik, Color renk, int sayi) {
    return Row(children: [Container(width: 10, height: 10, decoration: BoxDecoration(color: renk, shape: BoxShape.circle)), const SizedBox(width: 6), Text('$baslik ($sayi)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: Colors.grey.shade800))]);
  }

  Widget _buildFilterSection() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      child: Row(children: [_filtreButonu('Tümü', Icons.all_inclusive, Colors.indigo), _filtreButonu('Pozitif', Icons.sentiment_very_satisfied, Colors.green), _filtreButonu('Negatif', Icons.sentiment_very_dissatisfied, Colors.red), _filtreButonu('Nötr', Icons.sentiment_neutral, Colors.grey)]),
    );
  }

  Widget _filtreButonu(String baslik, IconData ikon, Color renk) {
    bool seciliMi = seciliFiltre == baslik;
    return Padding(padding: const EdgeInsets.only(right: 8.0), child: ActionChip(avatar: Icon(ikon, size: 16, color: seciliMi ? Colors.white : renk), label: Text(baslik, style: TextStyle(color: seciliMi ? Colors.white : Colors.black87, fontWeight: seciliMi ? FontWeight.bold : FontWeight.normal, fontSize: 13)), backgroundColor: seciliMi ? renk : Colors.white, side: BorderSide(color: seciliMi ? renk : Colors.grey.shade300), onPressed: () => filtreUygula(baslik)));
  }

  Widget _veriKartiOlustur(dynamic veri) {
    double skor = (veri['duygu_skoru'] as num).toDouble();
    Color durumRengi = skor > 0 ? Colors.green : (skor < 0 ? Colors.red : Colors.grey);
    return Card(margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6), elevation: 0, color: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: Colors.grey.shade200)), child: ListTile(leading: CircleAvatar(backgroundColor: durumRengi.withOpacity(0.1), child: Text(veri['platform'].toString().substring(0, 1), style: TextStyle(fontWeight: FontWeight.bold, color: durumRengi))), title: Text(veri['icerik'], style: const TextStyle(fontSize: 13), maxLines: 3, overflow: TextOverflow.ellipsis), subtitle: Padding(padding: const EdgeInsets.only(top: 8.0), child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text("Kaynak: ${veri['platform']}", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: Colors.indigo.shade300)), Text("Skor: $skor", style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: durumRengi))]))));
  }
}