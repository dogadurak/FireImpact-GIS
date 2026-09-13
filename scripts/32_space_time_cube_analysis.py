import sys
import os
import arcpy
from arcpy.sa import *

sys.stdout.reconfigure(encoding="utf-8")

# UZAMSAL-ZAMAN KUPU (SPACE TIME CUBE) VE EMERGING HOT SPOT ANALIZI
#
# ONEMLI BILIMSEL NOT: Bu analiz SADECE 4 zaman adimi (2021 yangin-sonrasi,
# 2022, 2023, 2024) kullanmaktadir. Mann-Kendall trend testi ve Emerging Hot
# Spot Analysis, istatistiksel olarak anlamli sonuc icin genelde >=10-20 zaman
# dilimi onerir. Bu yuzden sonuclar "KESIN KANITLANMIS TREND" degil,
# "KESIFSEL/ON BULGU" olarak sunulmalidir. Bu, makine ogrenmesi DEGIL,
# mekansal istatistik yontemidir (Getis-Ord Gi* + Mann-Kendall).

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
out_folder = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\StoryMap_Katmanlari"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

true_fire = os.path.join(out_folder, "dNBR_True_Fire_Only.tif")
if not os.path.exists(true_fire):
    true_fire = os.path.join(workspace, "dNBR_True_Fire_Only.tif")

print("0. 2021 (yangin-sonrasi, Agustos) NBR baz cizgisi hesaplaniyor...")
arcpy.env.extent = arcpy.Describe(true_fire).extent
arcpy.env.cellSize = 20
arcpy.env.snapRaster = true_fire

b8 = Float(Raster(os.path.join(workspace, "post_b8_mosaic.tif")))
b12 = Float(Raster(os.path.join(workspace, "post_b12_mosaic.tif")))
post_nbr = (b8 - b12) / (b8 + b12)
post_nbr_masked = ExtractByMask(post_nbr, true_fire)
recovery_2021_path = os.path.join(out_folder, "Recovery_Full_NBR_2021.tif")
post_nbr_masked.save(recovery_2021_path)
print(f"   Kaydedildi: {recovery_2021_path}")

print("\n1. Bos bir Mosaic Dataset olusturuluyor...")
gdb = os.path.join(out_folder, "StoryMap_Katmanlari.gdb")
md_name = "Recovery_MD"
md_path = os.path.join(gdb, md_name)
sr = arcpy.Describe(true_fire).spatialReference
if arcpy.Exists(md_path):
    arcpy.management.Delete(md_path)
arcpy.management.CreateMosaicDataset(gdb, md_name, sr, 1, "32_BIT_FLOAT")

print("2. 4 yillik NBR rasterlari mozaik veri kumesine ekleniyor...")
rasters = {
    2021: recovery_2021_path,
    2022: os.path.join(out_folder, "Recovery_Full_NBR_2022.tif"),
    2023: os.path.join(out_folder, "Recovery_Full_NBR_2023.tif"),
    2024: os.path.join(out_folder, "Recovery_Full_NBR_2024.tif"),
}
raster_list = ";".join(rasters.values())
arcpy.management.AddRastersToMosaicDataset(md_path, "Raster Dataset", raster_list,
                                            duplicate_items_action="OVERWRITE_DUPLICATES")

print("3. Zaman (StdTime) ve degisken (Variable) alanlari ekleniyor ve dolduruluyor...")
arcpy.management.AddField(md_path, "StdTime", "DATE")
arcpy.management.AddField(md_path, "Variable", "TEXT", field_length=20)
with arcpy.da.UpdateCursor(md_path, ["Name", "StdTime", "Variable"]) as cursor:
    for row in cursor:
        name = row[0]
        row[2] = "NBR"
        for year in rasters:
            if str(year) in name:
                row[1] = f"08/15/{year}"
                cursor.updateRow(row)
                break

print("4. Mozaik veri kumesi cok-boyutlu (multidimensional) hale getiriliyor...")
arcpy.md.BuildMultidimensionalInfo(md_path, "Variable", "StdTime")

print("5. Uzamsal-Zaman Kupu (Space Time Cube) olusturuluyor...")
cube_path = os.path.join(out_folder, "Manavgat_Recovery_Cube.nc")
arcpy.stpm.CreateSpaceTimeCubeMDRasterLayer(md_path, cube_path)
print(f"   Kaydedildi: {cube_path}")

print("\n6. Emerging Hot Spot Analysis calistiriliyor...")
hotspot_out = os.path.join(gdb, "Recovery_HotSpots")
arcpy.stpm.EmergingHotSpotAnalysis(cube_path, "NBR_VALUE", hotspot_out)
print(f"   Kaydedildi: {hotspot_out}")

arcpy.CheckInExtension("Spatial")
print("\n!!! TAMAMLANDI !!!")
