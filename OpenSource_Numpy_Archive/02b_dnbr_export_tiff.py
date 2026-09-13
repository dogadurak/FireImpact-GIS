import os
from arcgis.gis import GIS
from arcgis.raster.functions import band_arithmetic
from arcgis.geocoding import geocode
import pandas as pd

def main():
    print("ArcGIS Online'a bağlanılıyor...")
    gis = GIS("https://www.arcgis.com", "dogadurak_imag", "dogaduramooc#301")
    
    print("Manavgat koordinatları alınıyor...")
    manavgat_area = geocode("Manavgat, Antalya, Turkey")[0]['extent']

    print("Sentinel-2 veri setleri filtreleniyor...")
    sentinel_items = gis.content.search('title:"Sentinel-2 Views"', item_type='Imagery Layer', outside_org=True)
    sentinel_layer = sentinel_items[0].layers[0]

    pre_fire = sentinel_layer.filter_by(
        where="(Category = 1) AND (CloudCover <= 10)", 
        time=[pd.Timestamp('2021-07-10'), pd.Timestamp('2021-07-27')]
    )
    post_fire = sentinel_layer.filter_by(
        where="(Category = 1) AND (CloudCover <= 10)", 
        time=[pd.Timestamp('2021-08-15'), pd.Timestamp('2021-08-30')]
    )

    print("NBR hesaplanıyor...")
    pre_nbr = band_arithmetic(pre_fire, "(b8 - b12) / (b8 + b12)")
    post_nbr = band_arithmetic(post_fire, "(b8 - b12) / (b8 + b12)")
    dnbr = band_arithmetic([pre_nbr, post_nbr], "(b1 - b2)")

    # 1. TIFF olarak yerel bilgisayara dışa aktar
    print("Tek bantlı dNBR GeoTIFF olarak indiriliyor (Lütfen bekleyin, bu işlem internet hızına bağlı olarak sürebilir)...")
    save_dir = os.path.join(os.getcwd())
    
    # export_image expects bounding box string "xmin, ymin, xmax, ymax"
    bbox_str = f"{manavgat_area['xmin']},{manavgat_area['ymin']},{manavgat_area['xmax']},{manavgat_area['ymax']}"
    
    dnbr.export_image(
        bbox=bbox_str,
        bbox_sr=4326,
        image_sr=4326,
        size=[1200, 800],
        f='image',
        export_format='tiff',
        save_folder=save_dir,
        save_file='manavgat_dnbr.tif'
    )
    
    tiff_path = os.path.join(save_dir, 'manavgat_dnbr.tif')
    print(f"TIFF başarıyla indirildi: {tiff_path}")

    # 2. ArcGIS Online'a Yükle ve Yayınla
    print("TIFF dosyası ArcGIS Online'a yükleniyor...")
    item_props = {
        'title': 'Manavgat 2021 dNBR Tek Bantlı GeoTIFF',
        'type': 'Image', # Uploading a raster dataset requires type 'Image' usually.
        'tags': ['Fire', 'Manavgat', 'NBR', 'TIFF']
    }
    
    try:
        # Eski hatalı katmanları arayıp silelim (İsteğe bağlı)
        # old_items = gis.content.search('title:"Manavgat_2021_dNBR_Analysis"', item_type='Imagery Layer')
        # for i in old_items: i.delete()
        
        tif_item = gis.content.add(item_properties=item_props, data=tiff_path)
        print("Yüklendi! Şimdi Görüntü Katmanı olarak yayınlanıyor (Publish ediliyor)...")
        published_layer = tif_item.publish()
        print(f"HARİKA HABER! Yeni tek bantlı dNBR katmanınız hazır: {published_layer.title}")
        print("Artık Map Viewer'da açtığınızda doğrudan 'Classify' (Sınıflandırılmış) stilini kullanabilirsiniz.")
    except Exception as e:
        print(f"Yükleme sırasında hata oluştu: {e}")

if __name__ == "__main__":
    main()
