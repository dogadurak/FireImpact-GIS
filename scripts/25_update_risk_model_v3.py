import os
import arcpy
from arcpy.sa import *
import numpy as np
import matplotlib.pyplot as plt

# GELECEK YANGIN RISKI MODELI - V3
# Degisiklikler (script 21 ve 24'teki dogrulama sonuclarina dayanarak):
#   - EGIM (slope) CIKARILDI: gercek dNBR verisiyle test edildiginde varsayimin
#     TERSI cikti (duz alanlar dik alanlardan daha siddetli yanmis). Bu yuzden
#     modele dahil edilmiyor -- sadece dogrulanan degiskenler kullaniliyor.
#   - BAKI (aspect) KORUNDU: guney bakili alanlar dogrulanmis sekilde daha
#     siddetli yanmis (ortalama dNBR 0.0225 vs kuzeyde 0.0122).
#   - YAKIT YUKU (NDVI) EKLENDI: yangin-oncesi NDVI ile gercek yanma siddeti
#     arasinda net ve monoton bir iliski dogrulandi (Yanmamis NDVI=0.42 ->
#     Yuksek siddet NDVI=0.70). Daha yogun/saglikli bitki ortusu = daha fazla
#     yakit = daha siddetli yanma.
#   - KAPSAM DUZELTILDI: V2'deki nem bileseni sadece yanmis alanla sinirliydi
#     (yani "gelecek riski" sadece zaten yanmis bolgede hesapliyordu). Bu
#     surumde NDVI tüm Sentinel-2 karo kapsaminda (henuz yanmamis komsu
#     ormanlik alanlar dahil) hesaplaniyor.

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

utm36n = arcpy.SpatialReference(32636)

print("1. Baki (Aspect), NDVI ile ayni ızgaraya (UTM 36N, 20m) hizalaniyor...")
aspect_utm = os.path.join(workspace, "Manavgat_Aspect_UTM_v3.tif")
arcpy.management.ProjectRaster(os.path.join(workspace, "Manavgat_Aspect.tif"), aspect_utm, utm36n, "NEAREST", 20)

print("2. Yangin-oncesi NDVI, TUM karo kapsaminda (sadece yanan alanla sinirli degil) hesaplaniyor...")
b8_mosaic = os.path.join(workspace, "pre_b8_mosaic.tif")
b4_mosaic = os.path.join(workspace, "pre_b04_mosaic.tif")
arcpy.env.extent = arcpy.Describe(b8_mosaic).extent
arcpy.env.cellSize = 20
arcpy.env.snapRaster = b8_mosaic

b08 = Float(Raster(b8_mosaic))
b04 = Float(Raster(b4_mosaic))
ndvi_full = (b08 - b04) / (b08 + b04)
ndvi_full_path = os.path.join(workspace, "Pre_Fire_NDVI_Full.tif")
ndvi_full.save(ndvi_full_path)

print("3. Baki ve NDVI risk siniflarina ayriliyor...")
aspect_reclass = Reclassify(Raster(aspect_utm), "Value",
                             RemapRange([[-1, 90, 1], [90, 135, 2], [135, 225, 3], [225, 270, 2], [270, 360, 1]]))
# NDVI -> yakit riski: dogrulanan iliskiye gore YUKSEK NDVI = YUKSEK risk
ndvi_reclass = Reclassify(Raster(ndvi_full_path), "Value",
                           RemapRange([[-1.0, 0.3, 1], [0.3, 0.5, 2], [0.5, 1.0, 3]]))

print("4. Model birlestiriliyor: Baki (%50) + Yakit/NDVI (%50)...")
arcpy.env.extent = "MINOF"
risk_model = (aspect_reclass * 0.5) + (ndvi_reclass * 0.5)
risk_model_int = Int(risk_model + 0.5)
risk_out = os.path.join(workspace, "Future_Fire_Risk_V3.tif")
risk_model_int.save(risk_out)
print(f"   Kaydedildi: {risk_out}")

print("5. PNG onizleme uretiliyor...")
arr_raw = arcpy.RasterToNumPyArray(risk_model_int, nodata_to_value=255)
arr = arr_raw.astype(float)
arr[arr == 255] = np.nan

plt.figure(figsize=(10, 6))
plt.imshow(arr, cmap="RdYlGn_r")
plt.colorbar(label="Risk Seviyesi (1: Dusuk, 3: Yuksek)")
plt.title("Gelecek Yangin Riski Modeli V3 (Baki + Yakit Yuku/NDVI)\nSadece dogrulanmis degiskenler kullanilmistir")
plt.axis("off")
out_png = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\manavgat_gelecek_yangin_riski_v3.png"
plt.savefig(out_png, dpi=300, bbox_inches="tight")
plt.close()

print(f"\n!!! TAMAMLANDI !!! Risk haritasi (V3): {risk_out}")
print(f"    Onizleme: {out_png}")
arcpy.CheckInExtension("Spatial")
