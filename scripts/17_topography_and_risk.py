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
elif os.path.exists(out_dem):
    dem = Raster(out_dem)
else:
    raise FileNotFoundError("DEM verisi bulunamadi!")

print("2. Egim (Slope) ve Baki (Aspect) hesaplaniyor...")
slope_raster = Slope(dem, "DEGREE")
slope_raster.save(os.path.join(workspace, "Manavgat_Slope.tif"))

aspect_raster = Aspect(dem)
aspect_raster.save(os.path.join(workspace, "Manavgat_Aspect.tif"))

print("3. NDMI / Kuraklik Verisi Hazirlaniyor...")
ndmi_path = os.path.join(workspace, "Recovery_Full_NBR_2024.tif")
if os.path.exists(ndmi_path):
    ndmi_raster = Raster(ndmi_path)
else:
    raise FileNotFoundError("Recovery_Full_NBR_2024.tif bulunamadi!")

print("4. Gelecek Yangin Riski Modeli Olusturuluyor...")
slope_reclass = Reclassify(slope_raster, "Value", 
                           RemapRange([[0, 15, 1], [15, 30, 2], [30, 90, 3]]))

aspect_reclass = Reclassify(aspect_raster, "Value", 
                            RemapRange([[-1, 90, 1], [90, 135, 2], [135, 225, 3], [225, 270, 2], [270, 360, 1]]))

ndmi_reclass = Reclassify(ndmi_raster, "Value",
                          RemapRange([[-1.0, 0.1, 3], [0.1, 0.4, 2], [0.4, 1.0, 1]]))

arcpy.env.extent = ndmi_raster
arcpy.env.cellSize = ndmi_raster

risk_model = (slope_reclass * 0.35) + (aspect_reclass * 0.35) + (ndmi_reclass * 0.30)
risk_model_integer = Int(risk_model + 0.5)

risk_model_out = os.path.join(workspace, "Future_Fire_Risk_V2.tif")
risk_model_integer.save(risk_model_out)

print("5. PNG Gorseller Uretiliyor...")
import numpy as np

arr = arcpy.RasterToNumPyArray(risk_model_integer, nodata_to_value=np.nan)
plt.figure(figsize=(10, 6))
plt.imshow(arr, cmap='RdYlGn_r')
plt.colorbar(label='Risk Seviyesi (1: Dusuk, 3: Yuksek)')
plt.title("Gelecek Yangin Riski ve Egilim Modeli (Manavgat)")
plt.axis('off')
out_png = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\manavgat_gelecek_yangin_riski_v2.png"
plt.savefig(out_png, dpi=300, bbox_inches='tight')
plt.close()

print(f"!!! ISLEM TAMAMLANDI !!! Risk haritasi kaydedildi: {out_png}")
