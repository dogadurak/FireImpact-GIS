# 🌲 Ateşin İzleri: 2021 Manavgat Orman Yangınının Mekansal Analizi ve Gelecek Risk Modeli

Bu belge, ArcGIS StoryMaps üzerinde hazırlayacağınız sunumun **tam metnidir**. StoryMap'i oluştururken sol tarafa buradaki metinleri kopyalayabilir, sağ tarafa (veya arka plana) ise ürettiğimiz harita ve görselleri ekleyebilirsiniz.

---

## 1. Kapak (Cover)
*   **Ana Başlık:** Ateşin İzleri: 2021 Manavgat Orman Yangını
*   **Alt Başlık:** Uydu verileri, makine öğrenmesi ve CBS tabanlı mekansal analizlerle Türkiye'nin en büyük orman yangınının anatomisi ve gelecek risk projeksiyonları.
*   **Görsel:** `post_fire_TCI.tif` (Yangın sonrası simsiyah alanın gerçek renkli görüntüsü) veya `manavgat_yangin_meteorolojisi.png`

---

## 2. Giriş: Felaketin Boyutu (Metin Bloku)
28 Temmuz 2021'de Antalya'nın Manavgat ilçesinde başlayan ve günlerce süren orman yangınları, Türkiye Cumhuriyeti tarihinin en büyük orman yangını felaketlerinden biri olarak kayıtlara geçti. Bu çalışmada, Sentinel-2 uydu görüntüleri ve multispektral analiz yöntemleri kullanılarak yangının bıraktığı mekansal etki haritalandırılmış, doğanın yıllar içindeki iyileşme süreci izlenmiş ve gelecekteki olası riskler topografik olarak modellenmiştir.

---

## 3. Öncesi ve Sonrası (Swipe / Sıyırma Aracı)
*Burada StoryMap'in "Swipe (Sıyırma)" widget'ını kullanın.*
*   **Sol Harita:** `pre_fire_TCI.tif` (Yangın Öncesi Yeşil Örtü)
*   **Sağ Harita:** `post_fire_TCI.tif` (Yangın Sonrası)
*   **Metin:** "Yangından hemen önce (Temmuz başı) ve yangından hemen sonra (Ağustos ortası) alınan Sentinel-2 uydu görüntüleri, felaketin fiziksel boyutunu çarpıcı bir şekilde gözler önüne sermektedir. Kilometrelerce uzanan yemyeşil orman örtüsü, yerini siyaha bürünmüş bir kül tabakasına bırakmıştır."

---

## 4. Tahribatın Gerçek Boyutu: dNBR Analizi
*   **Harita:** `dNBR_Full_Masked_Classified.tif` (Bu katmanı ArcGIS Online'a yükleyip renklendirin: Sarı, Turuncu, Kırmızı, Bordo).
*   **Metin:** "Sadece optik görüntülerle yangının şiddetini ölçmek yanıltıcı olabilir. Bu projede, yangının bitki örtüsündeki nem ve klorofil kaybını bilimsel olarak ölçmek için **Normalize Edilmiş Yanma Oranı Farkı (dNBR)** indeksi kullanılmıştır.
Kızılötesi (B8) ve Kısa Dalga Kızılötesi (B12) bantları kullanılarak yapılan bu analizde, su ve bulutlar maskelenmiş; tahribat derecesi 'Düşük'ten 'Çok Yüksek'e kadar sınıflandırılmıştır. Bordo renkli alanlar, bitki örtüsünün tamamen yok olduğu ve toprağın aşırı derecede kavrulduğu en ağır hasarlı bölgeleri temsil etmektedir."

---

## 5. Yangını Büyüten Etken: Meteoroloji
*   **Görsel:** `manavgat_yangin_meteorolojisi.png` (Tek bir imaj olarak ekleyin)
*   **Metin:** "Yangının bu kadar hızlı ve kontrolsüz yayılmasının temel sebebi, bölgede yaşanan ekstrem hava koşullarıydı. NASA POWER iklim verileri kullanılarak yapılan meteorolojik analiz, felaket günlerinde sıcaklıkların aniden 40°C sınırına dayandığını, bağıl nemin ise %20'lerin altına düşerek bitki örtüsünü adeta bir 'çıraya' dönüştürdüğünü doğrulamaktadır."

---

## 6. Risk Altındaki Hayatlar: Etki Alanı Analizi (Buffer)
*   **Görsel/Harita:** `manavgat_yerlesim_buffer_analizi.png`
*   **Metin:** "Yangın sadece ormanlık alanları değil, insan yerleşimlerini de doğrudan tehdit etmiştir. Mekansal analiz (Buffer) yöntemleriyle yapılan çalışmada, Kalemler ve Evrenseki gibi yerleşim yerlerinin etrafında 1 km, 3 km ve 5 km'lik etki alanları modellenmiştir. Haritada görüldüğü üzere, birçok köy ve mahalle 'kırmızı bölge' olarak adlandırılan ve yangının merkez üssüne 1 kilometreden daha yakın olan ölümcül çemberin içinde kalmıştır."

---

## 7. Doğanın İyileşmesi (2021-2024 Zaman Çizelgesi)
*   **Bileşen:** StoryMap'te "Map Tour" veya "Time Slider" kullanarak 2022, 2023 ve 2024 yıllarına ait `Recovery_NBR` haritalarını sırayla gösterin.
*   **Metin:** "Yangının üzerinden geçen yıllar içinde doğa yaralarını sarmaya çalışıyor. 2022, 2023 ve 2024 yıllarının yaz aylarına ait Sentinel-2 görüntüleri işlenerek NBR (İyileşme) endeksi çok yıllı olarak hesaplanmıştır. 
Haritalardaki yeşile dönen alanlar genç sürgünlerin ve bitki örtüsünün yeniden yeşerdiği yerleri gösterirken; koyu renkli kalan bölgeler tahribatın kalıcı olduğu, erozyon riskinin yüksek olduğu ve belki de yapay ağaçlandırmaya ihtiyaç duyulan alanları işaret etmektedir."

---

## 8. Gelecek Yangın Riski Modeli (Predictive Analysis)
*   **Harita:** `manavgat_gelecek_yangin_riski.png` veya `Future_Fire_Risk.tif`
*   **Metin:** "Geçmişi anlamak kadar, geleceğe hazırlıklı olmak da hayati önem taşır. Copernicus uydu sisteminden elde edilen yüksek çözünürlüklü Sayısal Yükseklik Modeli (DEM) kullanılarak bölgenin Eğim (Slope) ve Bakı (Aspect) haritaları çıkartılmıştır.
Bu topografik veriler ışığında **Gelecek Yangın Riski Modeli** üretilmiştir. Haritadaki kırmızı bölgeler; yüksek eğimli ve güneye bakan (güneş altında kalarak çabuk kuruyan) yamaçları temsil eder. Olası bir kıvılcımda yangının en hızlı tırmanacağı ve müdahalenin en zor olacağı bu alanlar, orman yönetim planlarında 'öncelikli koruma bölgeleri' olarak değerlendirilmelidir."

---

## 9. Sonuç
*   **Metin:** "2021 Manavgat Yangını, iklim değişikliğinin ve ekstrem hava olaylarının orman ekosistemleri üzerindeki yıkıcı etkisini net bir şekilde göstermiştir. Bu CBS projesinde elde edilen veriler; afet öncesi risk yönetimi, afet anı tahliye planlaması ve afet sonrası rehabilitasyon çalışmalarında mekansal zekanın (Spatial Intelligence) ne kadar kritik bir rol oynadığını kanıtlamaktadır."

*(Hazırlayan: [Sizin Adınız/Soyadınız])*
