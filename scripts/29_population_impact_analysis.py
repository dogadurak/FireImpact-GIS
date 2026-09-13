import sys
import io
import os
import json
import arcpy
from arcpy.sa import *
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

# GERCEK INSAN ETKISI ANALIZI
#
# scripts/08_buffer_analysis.py (eski versiyon), yangin alanini bir NOKTA
# etrafinda uydurma 8km'lik bir daire olarak ve yerlesim yerlerini kodun
# kendi yorumunda "Ornek Manavgat koyleri koordinatlari" diye belirtilen
# TAHMINI koordinatlarla temsil ediyordu -- gercek veri degildi.
#
# Bu script:
#   1) Gercek yangin sinirini dNBR_Full_Masked_Classified.tif'ten (en buyuk
#      bitisik yanmis parca -- ana Manavgat yangini) cikartir.
#   2) Gercek yerlesim yeri konumlarini OpenStreetMap Overpass API'sinden alir
#      (bu script calistirilmadan once indirilmis: overpass_settlements.json).
#   3) Her yerlesimin gercek yangin sinirina olan gercek mesafesini hesaplar
#      (arcpy Near, UTM 36N projeksiyonunda -- dogru metre olcumu icin).
#   4) WorldPop 2020 (kisitlanmis, BM-duzeltmeli, 100m) nufus rasterini
#      1/3/5 km tampon halkalariyla kesistirip GERCEK nufus sayisi verir.

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

utm36n = arcpy.SpatialReference(32636)
wgs84 = arcpy.SpatialReference(4326)

perimeter_path = os.path.join(workspace, "main_fire_perimeter.shp")  # scripts/29a tarafindan uretildi
if not os.path.exists(perimeter_path):
    raise FileNotFoundError("Once scripts/29a_main_fire_perimeter.py calistirilmali!")

print("1. Gercek yerlesim yerleri (OpenStreetMap) okunuyor...")
with open(os.path.join(workspace, "overpass_settlements.json"), encoding="utf-8") as f:
    osm_data = json.load(f)
elements = [e for e in osm_data["elements"] if e.get("tags", {}).get("name")]
print(f"   {len(elements)} adet isimli yerlesim noktasi bulundu.")

points_gdb = os.path.join(workspace, "settlements.shp")
sr_wgs = arcpy.SpatialReference(4326)
arcpy.management.CreateFeatureclass(workspace, "settlements.shp", "POINT", spatial_reference=sr_wgs)
arcpy.management.AddField("settlements.shp", "name", "TEXT", field_length=100)
arcpy.management.AddField("settlements.shp", "place", "TEXT", field_length=30)
with arcpy.da.InsertCursor(points_gdb, ["SHAPE@XY", "name", "place"]) as cur:
    for e in elements:
        cur.insertRow(((e["lon"], e["lat"]), e["tags"].get("name", "")[:100], e["tags"].get("place", "")[:30]))

points_utm = os.path.join(workspace, "settlements_utm.shp")
arcpy.management.Project(points_gdb, points_utm, utm36n)

print("2. Yerlesimlerin gercek yangin sinirina mesafesi hesaplaniyor (arcpy Near)...")
perimeter_utm = os.path.join(workspace, "main_fire_perimeter_utm.shp")
arcpy.management.Project(perimeter_path, perimeter_utm, utm36n)
# Raster-to-polygon cikisinin cok sayida vertex icermesi (bu poligonda ~175,000)
# sonraki Buffer/Erase islemlerinde hataya yol acabiliyor -- once onarilir.
arcpy.management.RepairGeometry(perimeter_utm, "DELETE_NULL")
arcpy.analysis.Near(points_utm, perimeter_utm)

settlement_results = []
with arcpy.da.SearchCursor(points_utm, ["name", "place", "NEAR_DIST", "SHAPE@XY"]) as cur:
    for name, place, dist, xy in cur:
        settlement_results.append((name, place, dist, xy))
settlement_results.sort(key=lambda r: r[2])


def categorize(d):
    if d <= 1000:
        return "1 km - KRITIK"
    elif d <= 3000:
        return "3 km - TEHDIT"
    elif d <= 5000:
        return "5 km - TEHDIT"
    else:
        return "Etkilenmedi (>5km)"


print("\n--- GERCEK MESAFEYE GORE ETKILENEN YERLESIMLER (ilk 20, en yakindan) ---")
for name, place, dist, xy in settlement_results[:20]:
    print(f"  {name} ({place}): {dist:,.0f} m -> {categorize(dist)}")

counts = {"1 km - KRITIK": 0, "3 km - TEHDIT": 0, "5 km - TEHDIT": 0, "Etkilenmedi (>5km)": 0}
for _, _, dist, _ in settlement_results:
    counts[categorize(dist)] += 1
print("\n--- Kategoriye Gore Yerlesim Sayisi ---")
for k, v in counts.items():
    print(f"  {k}: {v} yerlesim")

print("\n3. 1/3/5 km tampon halkalari olusturuluyor (gercek yangin sinirindan)...")
b1 = os.path.join(workspace, "buf_1km.shp")
b3 = os.path.join(workspace, "buf_3km.shp")
b5 = os.path.join(workspace, "buf_5km.shp")
arcpy.analysis.PairwiseBuffer(perimeter_utm, b1, "1000 Meters", dissolve_option="ALL")
arcpy.analysis.PairwiseBuffer(perimeter_utm, b3, "3000 Meters", dissolve_option="ALL")
arcpy.analysis.PairwiseBuffer(perimeter_utm, b5, "5000 Meters", dissolve_option="ALL")

ring1 = os.path.join(workspace, "ring_1km.shp")  # fire perimeter -> 1km
ring3 = os.path.join(workspace, "ring_3km.shp")  # 1km -> 3km
ring5 = os.path.join(workspace, "ring_5km.shp")  # 3km -> 5km
arcpy.analysis.PairwiseErase(b1, perimeter_utm, ring1)
arcpy.analysis.PairwiseErase(b3, b1, ring3)
arcpy.analysis.PairwiseErase(b5, b3, ring5)

print("4. Nufus rasteri (WorldPop 2020) her halka icin toplaniyor...")
pop_raster = os.path.join(workspace, "tur_population_2020.tif")
pop_results = {}
for label, ring_fc in [("Yangin Alani Ici", perimeter_utm), ("0-1 km", ring1), ("1-3 km", ring3), ("3-5 km", ring5)]:
    ring_wgs = os.path.join(workspace, "_ring_wgs_tmp.shp")
    arcpy.management.Project(ring_fc, ring_wgs, wgs84)
    table = os.path.join(workspace, "_pop_zonal_tmp.dbf")
    try:
        ZonalStatisticsAsTable(ring_wgs, "FID", pop_raster, table, "DATA", "SUM")
        total = 0.0
        with arcpy.da.SearchCursor(table, ["SUM"]) as cur:
            for (s,) in cur:
                total += s
        pop_results[label] = total
    except Exception as ex:
        print(f"   UYARI: {label} icin nufus hesaplanamadi: {ex}")
        pop_results[label] = None
    print(f"   {label}: {pop_results[label]:,.0f} kisi" if pop_results[label] is not None else f"   {label}: hesaplanamadi")

total_5km = sum(v for v in pop_results.values() if v is not None)
print(f"\n   TOPLAM (yangin alani + 5km icindeki tum halkalar): ~{total_5km:,.0f} kisi (WorldPop 2020 tahmini)")

print("\n5. Harita olusturuluyor...")
fig, ax = plt.subplots(figsize=(11, 11))


def plot_shp(path, **kwargs):
    with arcpy.da.SearchCursor(path, ["SHAPE@"]) as cur:
        for (shape,) in cur:
            parts = shape.getPart()
            for part in parts:
                xs = [pt.X for pt in part if pt]
                ys = [pt.Y for pt in part if pt]
                ax.fill(xs, ys, **kwargs)


plot_shp(b5, color="#fee08b", alpha=0.5, edgecolor="none", zorder=1)
plot_shp(b3, color="#fdae61", alpha=0.6, edgecolor="none", zorder=2)
plot_shp(b1, color="#f46d43", alpha=0.7, edgecolor="none", zorder=3)
plot_shp(perimeter_utm, color="#4d0000", alpha=0.9, edgecolor="black", zorder=4)

with arcpy.da.SearchCursor(points_utm, ["name", "SHAPE@XY"]) as cur:
    fire_extent_pts = [row for row in arcpy.da.SearchCursor(perimeter_utm, ["SHAPE@"])]
for name, place, dist, (x, y) in settlement_results:
    if dist <= 5000:
        ax.scatter(x, y, color="blue", marker="^", s=60, zorder=5)
        ax.annotate(name, xy=(x, y), xytext=(4, 4), textcoords="offset points", fontsize=8, fontweight="bold")

ax.set_aspect("equal")
ax.set_axis_off()
legend_handles = [
    mpatches.Patch(color="#4d0000", alpha=0.9, label="Gercek Yangin Siniri (dNBR'den)"),
    mpatches.Patch(color="#f46d43", alpha=0.7, label="0-1 km Kritik Bolge"),
    mpatches.Patch(color="#fdae61", alpha=0.6, label="1-3 km Tehdit Bolgesi"),
    mpatches.Patch(color="#fee08b", alpha=0.5, label="3-5 km Tehdit Bolgesi"),
    plt.Line2D([0], [0], marker="^", color="w", markerfacecolor="blue", markersize=10, label="Gercek Yerlesim Yerleri (OSM)"),
]
ax.legend(handles=legend_handles, loc="lower right", fontsize=9, title="Etki Alanlari (Gercek Veri)")
ax.set_title("Manavgat Yangini: Gercek Sinir + Gercek Yerlesimler + WorldPop Nufus Etkisi", fontsize=14, fontweight="bold")

out_png = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\manavgat_yerlesim_buffer_analizi.png"
plt.savefig(out_png, dpi=300, bbox_inches="tight")
plt.close()
print(f"\n!!! TAMAMLANDI !!! Harita guncellendi: {out_png}")
arcpy.CheckInExtension("Spatial")
