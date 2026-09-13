import os
from arcgis.gis import GIS
from arcgis.raster.functions import band_arithmetic
from arcgis.geocoding import geocode
import pandas as pd

def main():
    print("ArcGIS Online'a bağlanılıyor...")
    kullanici_adi = "dogadurak_imag"
    sifre = "dogaduramooc#301"
    gis = GIS("https://www.arcgis.com", kullanici_adi, sifre)
    print("Bağlantı başarılı!\n")

    print("Sentinel-2 veri seti aranıyor...")
    sentinel_items = gis.content.search('title:"Sentinel-2 Views"', 
                                       item_type='Imagery Layer', 
                                       outside_org=True)
    if not sentinel_items:
        print("Veri bulunamadı.")
        return
    sentinel_layer = sentinel_items[0].layers[0]
    
    print("Manavgat koordinatları ayarlanıyor...")
    manavgat_area = geocode("Manavgat, Antalya, Turkey")[0]['extent']

    # 1. Yangın Öncesi Görüntü (Temmuz 2021)
    print("Yangın Öncesi (Temmuz 2021) verileri filtreleniyor...")
    pre_fire = sentinel_layer.filter_by(
        where="(Category = 1) AND (CloudCover <= 10)", 
        time=[pd.Timestamp('2021-07-10'), pd.Timestamp('2021-07-27')]
    )

    # 2. Yangın Sonrası Görüntü (Ağustos 2021)
    print("Yangın Sonrası (Ağustos 2021) verileri filtreleniyor...")
    post_fire = sentinel_layer.filter_by(
        where="(Category = 1) AND (CloudCover <= 10)", 
        time=[pd.Timestamp('2021-08-15'), pd.Timestamp('2021-08-30')]
    )

    # 3. NBR (Normalized Burn Ratio) Hesaplaması
    print("Yanma Şiddeti (NBR) pikselleri hesaplanıyor...")
    pre_nbr = band_arithmetic(pre_fire, "(b8 - b12) / (b8 + b12)")
    post_nbr = band_arithmetic(post_fire, "(b8 - b12) / (b8 + b12)")

    # 4. dNBR (Fark) Hesaplaması: (Öncesi - Sonrası)
    print("Hasar Fark Haritası (dNBR) oluşturuluyor...")
    dnbr = band_arithmetic([pre_nbr, post_nbr], "(b1 - b2)")

    # Harita objesini oluşturalım yerine direkt görüntüyü indirelim
    print("Hasar Fark Haritası (dNBR) PNG olarak kaydediliyor...")
    
    # Raster objesini resim olarak indir
    export_path = os.path.join(os.getcwd(), 'manavgat_dnbr.png')
    dnbr.export_image(bbox=manavgat_area, size=[800, 600], f='image', save_folder=os.getcwd(), save_file='manavgat_dnbr.png')
    print(f"Görüntü klasöre kaydedildi: {export_path}")

    # 5. Haritayı Hesaba Kaydetme (Raster Katmanı olarak)
    print("Analiz sonucu ArcGIS Online hesabınıza kaydediliyor...")
    item_properties = {
        'title': 'Manavgat 2021 Orman Yangını - dNBR Analizi',
        'snippet': 'Sentinel-2 uydu görüntüleri ile Python üzerinden hesaplanmış dNBR haritası.',
        'tags': ['Fire', 'Manavgat', 'NBR', 'Python', 'GIS']
    }
    
    try:
        saved_item = dnbr.save("Manavgat_2021_dNBR_Analysis", for_viz=True)
        print(f"\nHARİKA HABER! Harita başarıyla kaydedildi: '{saved_item.title}'")
    except Exception as e:
        print(f"Hesabınıza kaydedilirken bir uyarı oluştu (MOOC hesap kısıtlaması olabilir): {e}")

if __name__ == "__main__":
    main()
