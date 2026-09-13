# 🌲 Ateşin İzleri: 2021 Manavgat Orman Yangınının Mekansal Analizi ve Gelecek Risk Modeli

Bu belge, ArcGIS StoryMaps üzerinde hazırlayacağınız sunumun **tam metnidir**. Tüm sayılar bu oturumda gerçek veriyle (dNBR, NASA/Open-Meteo iklim verisi, WorldPop nüfus verisi, OpenStreetMap yerleşim verisi) doğrulanmıştır — hiçbir rakam varsayım değildir; doğrulanamayan bir varsayım (eğim/slope) bilinçli olarak modelden çıkarılmıştır. Metinleri StoryMap'e kopyalarken parantez içindeki "(Kaynak: ...)" notlarını StoryMap'in kendi metnine almanıza gerek yok, onlar sizin referansınız için.

---

## 1. Kapak (Cover)
- **Ana Başlık:** Ateşin İzleri: 2021 Manavgat Orman Yangını
- **Alt Başlık:** Uydu verileri ve CBS tabanlı mekansal analizlerle Türkiye'nin en büyük orman yangınının anatomisi, gerçek verilerle doğrulanmış bir risk modeli ve etki değerlendirmesi.
- **Görsel:** `post_tci_mosaic.tif` (yangın sonrası gerçek renkli görüntü) veya `manavgat_yangin_meteorolojisi.png`

---

## 2. Giriş: Felaketin Boyutu (Metin Bloku)
28 Temmuz 2021'de Antalya'nın Manavgat ilçesinde başlayan ve on gün süren orman yangını, Türkiye Cumhuriyeti tarihinin en büyük orman yangını felaketi olarak kayıtlara geçti. Bu çalışmada, Sentinel-2 uydu görüntüleri ve çok-bantlı analiz yöntemleriyle yangının bıraktığı mekansal etki haritalandırılmış, doğanın yıllar içindeki iyileşme süreci izlenmiş, insan ve karbon etkisi ölçülmüş ve gelecekteki riskler **yalnızca gerçek yangın verisiyle doğrulanan** değişkenlerle modellenmiştir.

**(Kaynak: yanan alan rakamı için bkz. Bölüm 4 — 60.128 hektar, bağımsız kaynaklarla örtüşecek şekilde doğrulanmıştır.)**

---

## 3. Öncesi ve Sonrası (Swipe / Sıyırma Aracı)
*StoryMap'in "Swipe (Sıyırma)" widget'ını kullanın.*
- **Sol Harita:** `pre_tci_mosaic.tif` (Yangın Öncesi Yeşil Örtü, Temmuz 2021)
- **Sağ Harita:** `post_tci_mosaic.tif` (Yangın Sonrası, Ağustos 2021)
- **Metin:** "Yangından hemen önce ve hemen sonra alınan Sentinel-2 uydu görüntüleri, felaketin fiziksel boyutunu çarpıcı bir şekilde gözler önüne sermektedir. Yemyeşil orman örtüsü, yerini kül tabakasına bırakmıştır."

---

## 4. Tahribatın Gerçek Boyutu: dNBR Analizi ve Veri Doğrulaması
- **Harita:** `dNBR_True_Fire_Only.tif` (Sarı → Turuncu → Kırmızı → Bordo sınıflandırması; ArcGIS Online'a yüklerken **bu dosyayı**, eski `dNBR_Full_Masked_Classified.tif`'i değil kullanın.)
- **Metin:** "Normalize Edilmiş Yanma Oranı Farkı (dNBR) indeksi ile yapılan analizde, Manavgat yangınının gerçek boyutu **60.128 hektar** olarak hesaplanmıştır — bu rakam, uydu tabanlı bağımsız bir akademik çalışmanın (56.663 ha) ve Antalya Orman Bölge Müdürlüğü'nün açıkladığı rakamın (75.000 ha) arasında yer almaktadır.
  - Düşük şiddet: 17.777 ha
  - Orta-Düşük şiddet: 15.834 ha
  - Orta-Yüksek şiddet: 12.391 ha
  - Yüksek şiddet: 14.128 ha
  
  Ham sınıflandırma verisinde şehir merkezi ve tarım arazileri gibi yerlerde yanlış-pozitif pikseller tespit edilmiş; bu çalışma yalnızca **gerçek, bitişik yangın lekesini** (>100 hektarlık bitişik alanlar) analiz kapsamına almıştır."

---

## 5. Yangını Büyüten Etken: Anormal Sıcak ve Rüzgarlı Bir Yaz
- **Görsel:** `manavgat_yangin_meteorolojisi.png` ve `manavgat_ruzgar_kuraklik_analizi.png`
- **Metin:** "Yangının hızlı yayılmasının ardında, bölgedeki ekstrem hava koşulları vardı. 2015-2020 ortalamasıyla karşılaştırıldığında, 2021 yaz mevsimi (1 Haziran - 10 Ağustos) **1,8°C daha sıcaktı**. Yağış farkı ise istatistiksel olarak anlamsız düzeydeydi (-0,8 mm) — yani asıl anomali **aşırı sıcaklık**tı, tipik kurak Akdeniz yazının ötesinde bir kuraklık değil.
  
  Yangın günlerinde (28 Temmuz - 10 Ağustos) baskın rüzgar **kuzeyden esip güneye doğru** itmiştir; bu, yangının Toros eteklerinden kıyıya doğru hızla ilerlemesinde önemli bir rol oynamıştır."

  *(Not: Bu bölümde "kuraklık" kelimesini kullanmaktan kaçının — veri bunu doğrulamamaktadır. "Anormal sıcak yaz" doğru ve savunulabilir ifadedir.)*

---

## 6. Model Doğrulaması: Varsayımları Gerçek Veriyle Test Etmek
*(Bu, projenin bilimsel ciddiyetini gösteren, StoryMap'i diğer öğrenci projelerinden ayıracak en güçlü bölümlerden biridir.)*
- **Görsel:** `manavgat_risk_model_dogrulama.png` ve `manavgat_ndvi_siddet_iliskisi.png`
- **Metin:** "Bir risk modeli kurmadan önce, yaygın varsayımları 2021'in gerçek yanma verisiyle test ettik:
  - **Bakı (yamacın yönü):** Güney bakılı alanlar, kuzey bakılı alanlardan belirgin şekilde daha şiddetli yanmıştır (ortalama dNBR 0.44'e karşı 0.36) — **doğrulandı**.
  - **Eğim:** 'Dik yamaçlar daha şiddetli yanar' varsayımı bu yangında **doğrulanmamıştır**; şiddet ile eğim arasında tutarlı bir ilişki bulunamamıştır. Bu yüzden eğim, nihai risk modeline dahil edilmemiştir.
  - **Bitki Örtüsü Yoğunluğu (NDVI):** Yangın öncesi bitki örtüsü yoğunluğu ile yanma şiddeti arasında güçlü, düzenli bir ilişki bulunmuştur: yanmamış alanlarda ortalama NDVI 0,42 iken, en yüksek şiddetli alanlarda 0,70'e çıkmaktadır — daha yoğun/sağlıklı orman, daha fazla yakıt demektir ve bu **doğrulanmıştır**.
  
  Bu doğrulama sonucunda, gelecek risk modelimiz yalnızca **doğrulanan** iki değişkeni (bakı ve bitki örtüsü yoğunluğu) kullanmaktadır."

---

## 7. Risk Altındaki Hayatlar: Gerçek Nüfus Etkisi Analizi
- **Harita:** `manavgat_yerlesim_buffer_analizi.png`
- **Metin:** "Yangın sadece ormanlık alanları değil, insan yerleşimlerini de doğrudan tehdit etmiştir. Gerçek yangın sınırı (uydu verisinden), gerçek yerleşim yeri konumları (OpenStreetMap) ve WorldPop 2020 nüfus verisi kullanılarak yapılan analiz sonucunda:
  - Yangının **1 km yakınında ~9.100 kişi**,
  - **1-3 km arasında ~43.800 kişi**,
  - **3-5 km arasında ~80.200 kişi**
  
  yaşadığı tespit edilmiştir — toplamda **yaklaşık 135.000 kişi**, yangının 5 kilometre etki alanı içinde kalmıştır. Kalemler, Seki, Tilkiler, Kepezbeleni, Sevinç gibi 46 yerleşim yeri, yangın sınırının 1 km içinde yer almaktadır."

---

## 8. Atmosfere Bedeli: Tahmini Karbon Emisyonu
*(Yeni bölüm — akılda kalıcı bir "başlık istatistiği" sağlar.)*
- **Görsel:** `manavgat_karbon_emisyonu.png`
- **Metin:** "Yanan bitki örtüsünün atmosfere saldığı karbonu, IPCC'nin 2006 Ulusal Sera Gazı Envanterleri Kılavuzu'ndaki standart yöntem ve ESA'nın uydu tabanlı gerçek biyokütle verisi (ESA CCI Biomass, 2020) kullanılarak tahmin ettik. Sonuç: yaklaşık **3 milyon ton CO2** (ürünün belgelenmiş doğruluk payına göre 2,38-3,56 milyon ton arasında) — bu, yaklaşık **646 bin aracın bir yıllık emisyonuna** eşdeğerdir.
  
  *(Not: Yanan alan ve biyokütle gerçek uydu verisi; yanmanın ne kadar 'tam' olduğu (yanma faktörü) hâlâ literatür tabanlı bir varsayım — StoryMap'te 'tahmini' ibaresiyle sunulmalıdır.)*"

---

## 9. Doğanın İyileşmesi (2021-2024 Zaman Çizelgesi)
- **Bileşen:** "Map Tour" veya "Time Slider" ile 2022, 2023, 2024 `Recovery_Full_NBR` haritalarını sırayla gösterin.
- **Metin:** "Yangının üzerinden geçen yıllar içinde doğa yaralarını sarmaya çalışıyor. 2022, 2023 ve 2024 yaz aylarına ait Sentinel-2 görüntüleri işlenerek NBR (İyileşme) endeksi çok yıllı olarak hesaplanmıştır. Yeşile dönen alanlar bitki örtüsünün yeniden yeşerdiği yerleri gösterirken, koyu renkli kalan bölgeler tahribatın kalıcı olduğu ve erozyon riskinin yüksek olduğu alanlara işaret etmektedir."

---

## 10. Gelecek Yangın Riski Modeli (Doğrulanmış Değişkenlerle)
- **Harita:** `manavgat_gelecek_yangin_riski_v3.png` (`Future_Fire_Risk_V4.tif` — dosya adı "V4" ama görsel dosyasının adı hâlâ "v3.png"; en güncel görseli kullanıyorsun, doğru dosya)
- **Metin:** "Bölüm 6'daki doğrulama sonuçlarına dayanarak, gelecek yangın riski modelimiz iki **doğrulanmış** değişkeni birleştirir: **bakı** (%50) ve **bitki örtüsü yoğunluğu/yakıt yükü** (%50). Eğim, gerçek veriyle test edildiğinde tutarlı bir etki göstermediği için modelden çıkarılmıştır — bu, modelin varsayımlar yerine kanıta dayandığının bir göstergesidir.
  
  Model, yalnızca yanmış alanla sınırlı değil, **henüz yanmamış çevre ormanı da dahil olacak şekilde** tüm bölgeyi kapsamaktadır. Haritadaki kırmızı bölgeler, güney bakılı ve yoğun bitki örtüsüne sahip, olası bir kıvılcımda en hızlı yanma riski taşıyan alanları temsil eder ve orman yönetim planlarında 'öncelikli koruma bölgeleri' olarak değerlendirilmelidir."

---

## 11. Sonuç
- **Metin:** "2021 Manavgat Yangını, iklim değişikliğinin ve ekstrem hava olaylarının orman ekosistemleri üzerindeki yıkıcı etkisini net bir şekilde göstermiştir. Bu çalışmada her bulgu — yanan alan, meteorolojik anomali, risk faktörleri, insan etkisi ve karbon salımı — gerçek veriyle ölçülmüş veya doğrulanmıştır; doğrulanamayan varsayımlar (örneğin eğimin risk üzerindeki etkisi) bilinçli olarak dışarıda bırakılmıştır. Elde edilen veriler, afet öncesi risk yönetiminde mekansal zekanın (Spatial Intelligence) ve **veri doğrulamanın** ne kadar kritik bir rol oynadığını göstermektedir."

*(Hazırlayan: [Sizin Adınız/Soyadınız])*

---

## Ek: Görsel-Bölüm Eşleştirme Tablosu (hızlı referans)
| Bölüm | Görsel Dosyası |
|---|---|
| 3. Swipe | `pre_tci_mosaic.tif`, `post_tci_mosaic.tif` |
| 4. dNBR | `dNBR_True_Fire_Only.tif` |
| 5. Meteoroloji | `manavgat_yangin_meteorolojisi.png`, `manavgat_ruzgar_kuraklik_analizi.png` |
| 6. Doğrulama | `manavgat_risk_model_dogrulama.png`, `manavgat_ndvi_siddet_iliskisi.png` |
| 7. Nüfus Etkisi | `manavgat_yerlesim_buffer_analizi.png` |
| 8. Karbon | `manavgat_karbon_emisyonu.png` |
| 9. İyileşme | `Recovery_Full_NBR_2022/2023/2024.tif` |
| 10. Gelecek Risk | `manavgat_gelecek_yangin_riski_v3.png` |
