import arcpy
from arcpy.sa import *
import os

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

print("1. TCI (Gercek Renkli) Görüntüler Birlestiriliyor (Kuzey + Güney)...")
try:
    arcpy.management.MosaicToNewRaster(
        input_rasters=["pre_fire_TCI.tif", "pre_fire_south_TCI.tif"],
        output_location=workspace,
        raster_dataset_name_with_extension="pre_tci_mosaic.tif",
        pixel_type="8_BIT_UNSIGNED",
        number_of_bands=3,
        mosaic_method="LAST"
    )
    print("Pre TCI Mosaic basarili!")
except Exception as e:
    print(f"Pre TCI Hata: {e}")

try:
    arcpy.management.MosaicToNewRaster(
        input_rasters=["post_fire_TCI.tif", "post_fire_south_TCI.tif"],
        output_location=workspace,
        raster_dataset_name_with_extension="post_tci_mosaic.tif",
        pixel_type="8_BIT_UNSIGNED",
        number_of_bands=3,
        mosaic_method="LAST"
    )
    print("Post TCI Mosaic basarili!")
except Exception as e:
    print(f"Post TCI Hata: {e}")

print("2. Recovery NBR Haritalari (2022, 2023, 2024) Tam Alan (Kuzey+Güney) Icin Yeniden Hesaplaniyor...")
years = [2022, 2023, 2024]
fire_extent = "dNBR_Full_Masked_Classified.tif"

# Extent'i TAM haritaya gore ayarla (sadece kuzeye degil!)
arcpy.env.extent = arcpy.Describe(fire_extent).extent
arcpy.env.cellSize = 10

burned_mask = ExtractByAttributes(fire_extent, "Value >= 2")

for year in years:
    print(f"\n--- YIL: {year} Yeniden Hesaplaniyor ---")
    n_b8 = f"ndmi_{year}_north_B08.tif"
    n_b12 = f"ndmi_{year}_north_B12.tif"
    s_b8 = f"ndmi_{year}_south_B08.tif"
    s_b12 = f"ndmi_{year}_south_B12.tif"

    b8_mosaic = f"temp_full_b8_{year}.tif"
    b12_mosaic = f"temp_full_b12_{year}.tif"

    arcpy.management.MosaicToNewRaster([n_b8, s_b8], workspace, b8_mosaic, 
                                       pixel_type="16_BIT_UNSIGNED", number_of_bands=1)
                                       
    arcpy.management.MosaicToNewRaster([n_b12, s_b12], workspace, b12_mosaic, 
                                       pixel_type="16_BIT_UNSIGNED", number_of_bands=1)
    
    b8_masked = ExtractByMask(b8_mosaic, burned_mask)
    b12_masked = ExtractByMask(b12_mosaic, burned_mask)
    
    b8_float = Float(b8_masked)
    b12_float = Float(b12_masked)
    nbr = (b8_float - b12_float) / (b8_float + b12_float)
    
    out_name = f"Recovery_Full_NBR_{year}.tif" # Yeni isimle kaydet (Kilitlenmeyi onlemek icin)
    nbr.save(out_name)
    print(f"Bitti: {out_name}")

print("\nHATALAR DUZELTILDI VE ISLEM TAMAMLANDI!")
