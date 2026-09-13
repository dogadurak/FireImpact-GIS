import os
import rasterio
import numpy as np
from arcgis.gis import GIS
from arcgis.geocoding import geocode
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

def download_bands(layer, time_filter, bbox_str, save_file):
    print(f"[{save_file}] İndiriliyor... (Sadece B8, B11, B12 bantları)")
    filtered = layer.filter_by(
        where="(Category = 1) AND (CloudCover <= 10)", 
        time=time_filter
    )
    
    save_dir = os.path.dirname(save_file)
    base_name = os.path.basename(save_file)
    
    filtered.export_image(
        bbox=bbox_str,
        bbox_sr=4326,
        image_sr=4326,
        size=[1200, 800],
        f='image',
        export_format='tiff',
        band_ids=[7, 11, 12], # B8(NIR), B11(SWIR1), B12(SWIR2)
        save_folder=save_dir,
        save_file=base_name
    )
    print(f"[{save_file}] Tamamlandı.")

def calc_index(tif_path, index_type):
    # tif_path 3 bantlı: Band 1 (B8), Band 2 (B11), Band 3 (B12)
    with rasterio.open(tif_path) as src:
        b8 = src.read(1).astype('float32')
        b11 = src.read(2).astype('float32')
        b12 = src.read(3).astype('float32')
        meta = src.meta.copy()

    # Sıfıra bölmeyi önle
    np.seterr(divide='ignore', invalid='ignore')
    
    if index_type == "NBR":
        # NBR = (B8 - B12) / (B8 + B12)
        result = (b8 - b12) / (b8 + b12 + 1e-8)
    elif index_type == "NDMI":
        # NDMI = (B8 - B11) / (B8 + B11)
        result = (b8 - b11) / (b8 + b11 + 1e-8)
    
    # -1 ile 1 arasına sınırla
    result = np.clip(result, -1.0, 1.0)
    
    return result, meta

def save_single_band(data, meta, out_path):
    meta.update({
        "count": 1,
        "dtype": 'float32',
        "compress": 'lzw'
    })
    with rasterio.open(out_path, 'w', **meta) as dst:
        dst.write(data, 1)

def main():
    print("ArcGIS Online'a bağlanılıyor...")
    gis = GIS("https://www.arcgis.com", "dogadurak_imag", "dogaduramooc#301")
    
    manavgat_area = geocode("Manavgat, Antalya, Turkey")[0]['extent']
    bbox_str = f"{manavgat_area['xmin']},{manavgat_area['ymin']},{manavgat_area['xmax']},{manavgat_area['ymax']}"
    
    sentinel_items = gis.content.search('title:"Sentinel-2 Views"', item_type='Imagery Layer', outside_org=True)
    layer = sentinel_items[0].layers[0]

    work_dir = os.getcwd()
    
    # Dosya yolları
    pre_tif = os.path.join(work_dir, 'raw_pre_2021.tif')
    post_tif = os.path.join(work_dir, 'raw_post_2021.tif')
    post_2022_tif = os.path.join(work_dir, 'raw_post_2022.tif')
    post_2023_tif = os.path.join(work_dir, 'raw_post_2023.tif')
    
    # 1. Ham verileri (3 bant) indir
    download_bands(layer, [pd.Timestamp('2021-07-10'), pd.Timestamp('2021-07-27')], bbox_str, pre_tif)
    download_bands(layer, [pd.Timestamp('2021-08-15'), pd.Timestamp('2021-08-30')], bbox_str, post_tif)
    download_bands(layer, [pd.Timestamp('2022-07-15'), pd.Timestamp('2022-08-15')], bbox_str, post_2022_tif)
    download_bands(layer, [pd.Timestamp('2023-07-15'), pd.Timestamp('2023-08-15')], bbox_str, post_2023_tif)

    print("\nLokal Hesaplamalar yapılıyor (Numpy ile)...")
    
    # 2. dNBR Hesapla
    pre_nbr, meta = calc_index(pre_tif, "NBR")
    post_nbr, _ = calc_index(post_tif, "NBR")
    dnbr = pre_nbr - post_nbr
    
    save_single_band(dnbr, meta, os.path.join(work_dir, 'FINAL_manavgat_dnbr.tif'))
    print("Oluşturuldu: FINAL_manavgat_dnbr.tif")

    # 3. NDMI Hesapla
    ndmi_2021, _ = calc_index(post_tif, "NDMI")
    save_single_band(ndmi_2021, meta, os.path.join(work_dir, 'FINAL_manavgat_ndmi_2021.tif'))
    print("Oluşturuldu: FINAL_manavgat_ndmi_2021.tif")

    ndmi_2022, _ = calc_index(post_2022_tif, "NDMI")
    save_single_band(ndmi_2022, meta, os.path.join(work_dir, 'FINAL_manavgat_ndmi_2022.tif'))
    print("Oluşturuldu: FINAL_manavgat_ndmi_2022.tif")
    
    ndmi_2023, _ = calc_index(post_2023_tif, "NDMI")
    save_single_band(ndmi_2023, meta, os.path.join(work_dir, 'FINAL_manavgat_ndmi_2023.tif'))
    print("Oluşturuldu: FINAL_manavgat_ndmi_2023.tif")
    
    # Çöp temizliği (ham TIFF'leri silelim)
    for f in [pre_tif, post_tif, post_2022_tif, post_2023_tif]:
        if os.path.exists(f): os.remove(f)

    print("\nİŞLEM TAMAM! Tüm temiz, tek bantlı analiz TIFF'leri hazırlandı.")

if __name__ == "__main__":
    main()
