import os
import requests
from pystac_client import Client
import planetary_computer

print("Microsoft Planetary Computer uzerinden 2022-2024 yillari Sentinel-2 (NDMI) verileri araniyor...")

bbox_north = [31.3, 36.7, 31.6, 37.0]
bbox_south = [31.3, 36.4, 31.6, 36.7]

catalog = Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

out_dir = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
os.makedirs(out_dir, exist_ok=True)

def download_asset(asset, output_path):
    if os.path.exists(output_path):
        print(f"Zaten mevcut: {output_path}")
        return
    print(f"Indiriliyor -> {output_path}")
    response = requests.get(asset.href, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

years = [2022, 2023, 2024]

for year in years:
    print(f"\n--- YIL: {year} (Agustos) ---")
    
    # NORTH TILE
    print(f"{year} - Kuzey (North) uydusu araniyor...")
    search_n = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox_north,
        datetime=f"{year}-08-01/{year}-08-30",
        query={"eo:cloud_cover": {"lt": 5}}
    )
    items_n = list(search_n.items())
    
    # Filter for exactly 36SUG
    items_n = [i for i in items_n if i.properties.get("s2:mgrs_tile") == "36SUG" or "36SUG" in i.id]

    if items_n:
        best_n = sorted(items_n, key=lambda x: x.properties["eo:cloud_cover"])[0]
        print(f"Kuzey Bulundu: {best_n.id} (Bulut: {best_n.properties['eo:cloud_cover']}%)")
        
        # Download B08 (NIR), B12 (SWIR for NDMI), SCL (Mask)
        download_asset(best_n.assets["B08"], os.path.join(out_dir, f"ndmi_{year}_north_B08.tif"))
        download_asset(best_n.assets["B12"], os.path.join(out_dir, f"ndmi_{year}_north_B12.tif"))
        download_asset(best_n.assets["SCL"], os.path.join(out_dir, f"ndmi_{year}_north_SCL.tif"))
        
        # SOUTH TILE - We must match the EXACT date/pass of the North tile!
        date_str = best_n.datetime.strftime("%Y-%m-%d")
        print(f"{year} - Guney (South) uydusu araniyor... (Ayni tarih: {date_str})")
        
        search_s = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox_south,
            datetime=f"{date_str}/{date_str}", # Match the exact date
        )
        items_s = list(search_s.items())
        # Filter for MGRS tile 36SUF
        same_pass_s = [i for i in items_s if i.properties.get("s2:mgrs_tile") == "36SUF" or "36SUF" in i.id]
        
        if same_pass_s:
            best_s = same_pass_s[0]
            print(f"Guney Bulundu: {best_s.id}")
            download_asset(best_s.assets["B08"], os.path.join(out_dir, f"ndmi_{year}_south_B08.tif"))
            download_asset(best_s.assets["B12"], os.path.join(out_dir, f"ndmi_{year}_south_B12.tif"))
            download_asset(best_s.assets["SCL"], os.path.join(out_dir, f"ndmi_{year}_south_SCL.tif"))
        else:
            print(f"HATA: {year} yili icin ayni tarihte Guney parcasi bulunamadi!")
    else:
        print(f"HATA: {year} yili icin bulutsuz Kuzey parcasi bulunamadi!")

print("\nButun yillar icin NDMI (Drought Impact) verileri indirildi!")
