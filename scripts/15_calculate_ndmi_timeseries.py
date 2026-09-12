import arcpy
import os
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

years = [2021, 2022, 2023, 2024]
fire_extent = "dNBR_Full_Masked_Classified.tif"

print("1. Sadece yanan alanlari (Siddet >= 2) ayiklayarak Maske olusturuluyor...")
try:
    burned_mask = ExtractByAttributes(fire_extent, "Value >= 2")
except Exception as e:
    print(f"Hata: fire_extent maskesi olusturulamadi. {e}")
    exit(1)

for year in years:
    print(f"\n--- YIL: {year} ---")
    
    if year == 2021:
        n_b8 = "post_fire_B08.tif"
        n_b12 = "post_fire_B12.tif"
        s_b8 = "post_fire_south_B08.tif"
        s_b12 = "post_fire_south_B12.tif"
    else:
        n_b8 = f"ndmi_{year}_north_B08.tif"
        n_b12 = f"ndmi_{year}_north_B12.tif"
        s_b8 = f"ndmi_{year}_south_B08.tif"
        s_b12 = f"ndmi_{year}_south_B12.tif"

    b8_mosaic = f"temp_b8_{year}.tif"
    b12_mosaic = f"temp_b12_{year}.tif"

    print("Kuzey ve Guney B08 (NIR) Birlestiriliyor...")
    arcpy.management.MosaicToNewRaster([n_b8, s_b8], workspace, b8_mosaic, 
                                       pixel_type="16_BIT_UNSIGNED", number_of_bands=1)
                                       
    print("Kuzey ve Guney B12 (SWIR) Birlestiriliyor...")
    arcpy.env.extent = arcpy.Describe(n_b8).extent
    arcpy.env.cellSize = 10
    arcpy.management.MosaicToNewRaster([n_b12, s_b12], workspace, b12_mosaic, 
                                       pixel_type="16_BIT_UNSIGNED", number_of_bands=1)
    
    print("Yanan alana gore kirpiliyor (Extract by Mask)...")
    b8_masked = ExtractByMask(b8_mosaic, burned_mask)
    b12_masked = ExtractByMask(b12_mosaic, burned_mask)
    
    print("Bitki Ortusu Nem/Iyilesme Indeksi (NBR) Hesaplaniyor...")
    b8_float = Float(b8_masked)
    b12_float = Float(b12_masked)
    nbr = (b8_float - b12_float) / (b8_float + b12_float)
    
    out_name = f"Recovery_NBR_{year}.tif"
    nbr.save(out_name)
    print(f"Bitti: {out_name}")

print("\n!!! TUM YILLARIN IYILESME/KURAKLIK ANALIZI TAMAMLANDI !!!")
