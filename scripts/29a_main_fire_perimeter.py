import arcpy, os
from arcpy.sa import *

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

dnbr_path = os.path.join(workspace, "dNBR_Full_Masked_Classified.tif")
burned = Con(Raster(dnbr_path) >= 2, 1)
regions = RegionGroup(burned, "FOUR", "WITHIN", "NO_LINK")

table = os.path.join(workspace, "_region_sizes_tmp.dbf")
ZonalStatisticsAsTable(regions, "Value", regions, table, "DATA", "ALL")
best_id, best_count = None, -1
with arcpy.da.SearchCursor(table, ["Value", "COUNT"]) as cur:
    for value, count in cur:
        if count > best_count:
            best_id, best_count = int(value), count
print(f"En buyuk bitisik parca ID: {best_id}, alan: {best_count*0.01:,.1f} ha (ana Manavgat yangini)")

main_fire = Con(regions == best_id, 1)
main_fire_path = os.path.join(workspace, "Main_Manavgat_Fire.tif")
main_fire.save(main_fire_path)

poly = os.path.join(workspace, "main_fire_poly.shp")
arcpy.conversion.RasterToPolygon(main_fire_path, poly, "SIMPLIFY", "VALUE", "MULTIPLE_OUTER_PART")
dissolved = os.path.join(workspace, "main_fire_perimeter.shp")
arcpy.management.Dissolve(poly, dissolved)

wgs84 = arcpy.SpatialReference(4326)
desc = arcpy.Describe(dissolved)
ext_wgs = desc.extent.projectAs(wgs84)
print(f"BBOX (WGS84): {ext_wgs.XMin},{ext_wgs.YMin},{ext_wgs.XMax},{ext_wgs.YMax}")
with arcpy.da.SearchCursor(dissolved, ["SHAPE@"]) as cur:
    for row in cur:
        c = arcpy.PointGeometry(row[0].centroid, desc.spatialReference).projectAs(wgs84)
        print(f"CENTROID (WGS84): {c.firstPoint.Y},{c.firstPoint.X}")

arcpy.management.Delete(table)
arcpy.CheckInExtension("Spatial")
print("TAMAMLANDI")
