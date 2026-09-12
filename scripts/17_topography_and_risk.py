import arcpy
from arcpy.sa import *
import os
import matplotlib.pyplot as plt

# Set workspace
workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

print("1. DEM Birlestiriliyor...")
dem0 = os.path.join(workspace, "dem_raw_0.tif")
dem1 = os.path.join(workspace, "dem_raw_1.tif")
out_dem = os.path.join(workspace, "Manavgat_DEM.tif")

if os.path.exists(dem0) and os.path.exists(dem1):
    arcpy.management.MosaicToNewRaster([dem0, dem1], workspace, "Manavgat_DEM.tif", 
                                       pixel_type="32_BIT_FLOAT", number_of_bands=1)
    dem = Raster(out_dem)
elif os.path.exists(dem0):
    dem = Raster(dem0)
else:
    raise FileNotFoundError("DEM verisi bulunamadi!")

print("2. Egim (Slope) ve Baki (Aspect) hesaplaniyor...")
slope_raster = Slope(dem, "DEGREE")
slope_raster.save(os.path.join(workspace, "Manavgat_Slope.tif"))

aspect_raster = Aspect(dem)
aspect_raster.save(os.path.join(workspace, "Manavgat_Aspect.tif"))

print("3. Gelecek Yangin Riski Modeli Olusturuluyor...")
# Egim Reclassify:
# 0-15 derece: 1 (Dusuk)
# 15-30 derece: 2 (Orta)
# >30 derece: 3 (Yuksek)
slope_reclass = Reclassify(slope_raster, "Value", 
                           RemapRange([[0, 15, 1], [15, 30, 2], [30, 90, 3]]))

# Baki Reclassify:
# Guney bakilar daha cok isinir ve kurur (Kuzey Yarimkurede).
# Guneydogu (135), Guney (180), Guneybati (225)
# 135 - 225 arasi: 3 (Yuksek Risk)
# 90-135 ve 225-270: 2 (Orta Risk)
# Diger: 1 (Dusuk Risk)
aspect_reclass = Reclassify(aspect_raster, "Value", 
                            RemapRange([[-1, 90, 1], [90, 135, 2], [135, 225, 3], [225, 270, 2], [270, 360, 1]]))

# Yangin Gecmisi / Bitki Ortusu:
# Daha once yanan yerler 
burn_severity = Raster(os.path.join(workspace, "dNBR_Full_Masked_Classified.tif"))
# Yanan alanlari (2,3,4,5) bitki ortusu kalmadigi icin su anlik risk dusuk sayilabilir, 
# ama biz genel model yapiyoruz, ormanin kalan saglam kisimlari tehlikede.
# Basit model: Egim (Agirlik %50) + Baki (Agirlik %50)
risk_model = (slope_reclass * 0.5) + (aspect_reclass * 0.5)
risk_model_out = os.path.join(workspace, "Future_Fire_Risk.tif")
risk_model.save(risk_model_out)

print("4. PNG Gorseller Uretiliyor...")
# Convert to numpy array for fast plotting (subsample to save memory)
import numpy as np

# Risk Haritasi PNG
arr = arcpy.RasterToNumPyArray(risk_model, nodata_to_value=np.nan)
plt.figure(figsize=(10, 6))
plt.imshow(arr, cmap='RdYlGn_r')
plt.colorbar(label='Risk Seviyesi (1: Dusuk, 3: Yuksek)')
plt.title("Gelecek Yangin Riski ve Egilim Modeli (Manavgat)")
plt.axis('off')
out_png = r"C:\Users\PC\.gemini\antigravity-ide\brain\55ade938-5ad7-4095-a1eb-26368b356086\manavgat_gelecek_yangin_riski.png"
plt.savefig(out_png, dpi=300, bbox_inches='tight')
plt.close()

print(f"!!! ISLEM TAMAMLANDI !!! Risk haritasi kaydedildi: {out_png}")
