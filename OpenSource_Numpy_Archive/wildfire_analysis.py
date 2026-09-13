import os
from arcgis.gis import GIS
from arcgis.raster.functions import band_arithmetic
from arcgis.geocoding import geocode
import pandas as pd

def main():
    print("ArcGIS API for Python yüklemesi ve kütüphane içe aktarımı başarılı.")
    
    kullanici_adi = "dogadurak_imag"
    sifre = "dogaduramooc#301"

    print("ArcGIS Online'a bağlanılıyor...")
    try:
        gis = GIS("https://www.arcgis.com", kullanici_adi, sifre)
        print("ArcGIS Online'a dışarıdan (Antigravity IDE) başarıyla bağlanıldı!")
    except Exception as e:
        print(f"Bağlantı hatası: {e}")
        return

    print("Sentinel-2 veri seti aranıyor...")
    sentinel_items = gis.content.search('title:"Sentinel-2 Views" OR title:"Multispectral Landsat"', 
                                       item_type='Imagery Layer', 
                                       outside_org=True)
    
    if not sentinel_items:
        print("Veri seti bulunamadı!")
        return
        
    sentinel_item = sentinel_items[0]
    sentinel_layer = sentinel_item.layers[0]
    print(f"Kullanılacak Veri Seti: {sentinel_item.title}")

    print("Manavgat koordinatları alınıyor...")
    manavgat_area = geocode("Manavgat, Antalya, Turkey")[0]['extent']
    print(f"Koordinatlar: {manavgat_area}")
    
    print("\nAdım 1 ve 2 başarıyla tamamlandı. Python ortamı hazır!")

if __name__ == "__main__":
    main()
