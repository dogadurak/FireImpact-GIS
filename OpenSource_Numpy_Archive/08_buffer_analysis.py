import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

print("Cografi Tampon (Buffer) Analizi baslatiliyor...")

try:
    # Manavgat yangin merkezi ve tahmini yangin alani poligonu
    # Merkez: 31.44, 36.78
    fire_center = Point(31.44, 36.78)

    # EPSG:4326 (Derece) -> EPSG:3857 (Metre) donusumu 
    fire_gdf = gpd.GeoDataFrame(index=[0], crs="epsg:4326", geometry=[fire_center])
    fire_gdf = fire_gdf.to_crs(epsg=3857)

    # Ana yangin poligonu (yaklasik 8km capli yanan bolge)
    burned_area = fire_gdf.buffer(8000) 
    burned_gdf = gpd.GeoDataFrame(geometry=burned_area, crs="epsg:3857")

    # Etki (Buffer) alanlarini olusturalim
    buffer_1km = burned_gdf.buffer(1000)
    buffer_3km = burned_gdf.buffer(3000)
    buffer_5km = burned_gdf.buffer(5000)

    # Koye benzer yerlesim yerleri (Ornek Manavgat koyleri koordinatlari)
    villages = {
        "Kalemler": Point(31.40, 36.80),
        "Evrenseki": Point(31.35, 36.81),
        "Sarilar": Point(31.46, 36.82),
        "Gundogdu": Point(31.30, 36.82),
        "Oymapinar": Point(31.53, 36.90)
    }

    villages_gdf = gpd.GeoDataFrame(
        {"name": list(villages.keys())}, 
        geometry=list(villages.values()), 
        crs="epsg:4326"
    )
    villages_gdf = villages_gdf.to_crs(epsg=3857)

    # Gorsellestirme
    fig, ax = plt.subplots(figsize=(10, 10))

    # Bufferlari ciz
    buffer_5km.plot(ax=ax, color='yellow', alpha=0.3, edgecolor='none')
    buffer_3km.plot(ax=ax, color='orange', alpha=0.4, edgecolor='none')
    buffer_1km.plot(ax=ax, color='red', alpha=0.5, edgecolor='none')

    # Yanan ana alani ciz
    burned_gdf.plot(ax=ax, color='black', alpha=0.7, edgecolor='black')

    # Yerlesim yerlerini ciz
    villages_gdf.plot(ax=ax, color='blue', marker='^', markersize=100, zorder=5)

    # Isimleri yaz
    for x, y, label in zip(villages_gdf.geometry.x, villages_gdf.geometry.y, villages_gdf.name):
        ax.annotate(label, xy=(x, y), xytext=(5, 5), textcoords="offset points", fontweight='bold', fontsize=11, color='darkblue')

    ax.set_axis_off()

    # Ozel Lejant
    legend_handles = [
        mpatches.Patch(color='black', alpha=0.7, label='Yanan Orman Alani'),
        mpatches.Patch(color='red', alpha=0.5, label='1 km Kritik Bolge'),
        mpatches.Patch(color='orange', alpha=0.4, label='3 km Tehdit Bolgesi'),
        mpatches.Patch(color='yellow', alpha=0.3, label='5 km Tehdit Bolgesi'),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='blue', markersize=10, label='Yerlesim Yerleri')
    ]
    ax.legend(handles=legend_handles, loc='lower right', fontsize=10, title="Etki Alanlari", title_fontsize=12)

    plt.title("Manavgat Yangini: Yerlesim Yerleri Etki (Buffer) Analizi", fontsize=16, fontweight='bold')
    plt.tight_layout()

    out_png = "manavgat_yerlesim_buffer_analizi.png"
    plt.savefig(out_png, dpi=300)
    print(f"✅ Buffer analizi tamamlandi. Harita kaydedildi: {out_png}")

except Exception as e:
    print(f"Hata: {e}")
