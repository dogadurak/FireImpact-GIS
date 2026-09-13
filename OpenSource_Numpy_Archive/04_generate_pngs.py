import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def tif_to_png(tif_path, png_path, cmap, vmin, vmax, title, is_dnbr=False):
    if not os.path.exists(tif_path):
        print(f"Hata: {tif_path} bulunamadı.")
        return
        
    with rasterio.open(tif_path) as src:
        data = src.read(1)
        # 0 veya no-data değerlerini maskele (Opsiyonel)
        # NBR'da -1.0 ile 1.0 arasında değerler olur
        
    plt.figure(figsize=(12, 8))
    
    if is_dnbr:
        # dNBR Sınıflandırma Renkleri
        # < 0.1 : Unburned (Yeşil)
        # 0.1 - 0.27 : Low Severity (Sarı)
        # 0.27 - 0.44 : Mod-Low Severity (Turuncu)
        # 0.44 - 0.66 : Mod-High Severity (Kırmızı)
        # > 0.66 : High Severity (Koyu Kırmızı/Mor)
        
        cmap = mcolors.ListedColormap(['#008000', '#FFFF00', '#FFA500', '#FF0000', '#800080'])
        bounds = [-1, 0.1, 0.27, 0.44, 0.66, 2]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)
        img = plt.imshow(data, cmap=cmap, norm=norm)
        cbar = plt.colorbar(img, ticks=[0, 0.18, 0.35, 0.55, 1])
        cbar.ax.set_yticklabels(['Unburned', 'Low', 'Mod-Low', 'Mod-High', 'High'])
    else:
        # NDMI - Kuru(Kahverengi) -> Nemli(Mavi)
        img = plt.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
        plt.colorbar(img, label="NDMI Value")
        
    plt.title(title)
    plt.axis('off')
    
    plt.savefig(png_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Oluşturuldu: {png_path}")

def main():
    work_dir = os.getcwd()
    
    dnbr_tif = os.path.join(work_dir, 'FINAL_manavgat_dnbr.tif')
    ndmi_2021 = os.path.join(work_dir, 'FINAL_manavgat_ndmi_2021.tif')
    ndmi_2022 = os.path.join(work_dir, 'FINAL_manavgat_ndmi_2022.tif')
    ndmi_2023 = os.path.join(work_dir, 'FINAL_manavgat_ndmi_2023.tif')
    
    # 1. dNBR Görseli
    tif_to_png(
        dnbr_tif, 
        os.path.join(work_dir, 'manavgat_dnbr_map.png'), 
        cmap=None, vmin=None, vmax=None, 
        title="Manavgat 2021 - Burn Severity (dNBR)", 
        is_dnbr=True
    )
    
    # 2. NDMI Görselleri
    # BrBG = Kahverengi (Kuru) -> Yeşil-Mavi (Islak)
    tif_to_png(
        ndmi_2021, 
        os.path.join(work_dir, 'manavgat_ndmi_2021_map.png'), 
        cmap='BrBG', vmin=-0.5, vmax=0.5, 
        title="Manavgat - Post-Fire Moisture (August 2021)"
    )
    
    tif_to_png(
        ndmi_2022, 
        os.path.join(work_dir, 'manavgat_ndmi_2022_map.png'), 
        cmap='BrBG', vmin=-0.5, vmax=0.5, 
        title="Manavgat - Recovery Moisture (August 2022)"
    )
    
    tif_to_png(
        ndmi_2023, 
        os.path.join(work_dir, 'manavgat_ndmi_2023_map.png'), 
        cmap='BrBG', vmin=-0.5, vmax=0.5, 
        title="Manavgat - Recovery Moisture (August 2023)"
    )

if __name__ == "__main__":
    main()
