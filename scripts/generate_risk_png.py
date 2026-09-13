import os
import rasterio
import matplotlib.pyplot as plt
import numpy as np

tif_path = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw\Future_Fire_Risk_V2.tif"
with rasterio.open(tif_path) as src:
    arr = src.read(1).astype(float)
    nodata = src.nodata
    
    # Mask nodata
    if nodata is not None:
        arr[arr == nodata] = np.nan
    else:
        # Fallback mask for extremely large or negative values
        arr[arr < 0] = np.nan
        arr[arr > 5] = np.nan

plt.figure(figsize=(10, 6))
plt.imshow(arr, cmap='RdYlGn_r')
plt.colorbar(label='Risk Seviyesi (1: Dusuk, 3: Yuksek)')
plt.title("Gelecek Yangin Riski ve Egilim Modeli (Manavgat)")
plt.axis('off')
out_png = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\manavgat_gelecek_yangin_riski_v2.png"
plt.savefig(out_png, dpi=300, bbox_inches='tight')
plt.close()

print(f"!!! ISLEM TAMAMLANDI !!! Risk haritasi kaydedildi: {out_png}")
