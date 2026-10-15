"""Metro center points (bounding-box centers) from Oxford's City reference.gpkg. Writes city_xy.json."""
import sqlite3, json, sys
c = sqlite3.connect(sys.argv[1] if len(sys.argv) > 1 else "City reference.gpkg")
t = c.execute("select table_name from gpkg_contents").fetchone()[0]
rows = c.execute(f'select t.Code,(r.minx+r.maxx)/2,(r.miny+r.maxy)/2 from "{t}" t join "rtree_{t}_geom" r on r.id=t.fid').fetchall()
json.dump({k: [round(x, 3), round(y, 3)] for k, x, y in rows}, open("city_xy.json", "w"))
print("cities", len(rows))
