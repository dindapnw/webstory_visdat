"""Mengubah data mentah BPS + shapefile menjadi file siap pakai di folder data/.
Jalankan sekali (butuh geopandas): python prepare_data.py "<folder data mentah>" """
import sys, re, json, openpyxl, pandas as pd, numpy as np, geopandas as gpd
SRC = sys.argv[1] if len(sys.argv) > 1 else "data_mentah"; OUT = "data/"
FIXPROV = {"KEP. BANGKA BELITUNG": "KEPULAUAN BANGKA BELITUNG", "KEP. RIAU": "KEPULAUAN RIAU", "D I YOGYAKARTA": "DI YOGYAKARTA"}
FIXKAB = {"TOBA SAMOSIR / TOBA": "TOBA SAMOSIR", "KEP. SERIBU": "KEPULAUAN SERIBU", "MAHAKAM ULU": "MAHAKAM HULU",
          "KOTA MAKASAR": "KOTA MAKASSAR", "MAMUJU UTARA / PASANGKAYU": "PASANGKAYU", "FAKFAK": "FAK FAK",
          "MALUKU TENGGARA BARAT / KEPULAUAN TANIMBAR": "MALUKU TENGGARA BARAT"}
FIXSHP = {"S I A K": "SIAK", "KOTA D U M A I": "KOTA DUMAI", "KOTA B A T A M": "KOTA BATAM"}
SHOW = {"TOBA SAMOSIR": "Toba", "PASANGKAYU": "Pasangkayu", "MALUKU TENGGARA BARAT": "Kepulauan Tanimbar", "MAHAKAM HULU": "Mahakam Ulu"}

def pretty(s):
    s = s.title()
    for a, b in {"Dki ": "DKI ", "Di ": "DI "}.items():
        if s.startswith(a): s = b + s[len(a):]
    return s

def num(v): return float(str(v).replace(",", "."))
def read_csv(f):
    out = []
    for l in open(f, encoding="utf-8-sig").read().splitlines()[2:]:
        r = l.split(";")
        try: out.append((r[0], num(r[1]), num(r[2])))
        except Exception: pass
    return pd.DataFrame(out, columns=["nama", "v2024", "v2025"])
def read_xlsx(f):
    ws = openpyxl.load_workbook(f, read_only=True, data_only=True).active
    out = [(r[0], r[1], r[2]) for r in ws.iter_rows(min_row=4, values_only=True) if isinstance(r[1], (int, float))]
    return pd.DataFrame(out, columns=["nama", "v2024", "v2025"])
def tidy(df, scale):
    out, p = [], None
    for n, a, b in df.itertuples(index=False):
        if n == "INDONESIA": continue
        if n.isupper(): p = FIXPROV.get(n, n); out.append((p, None, a * scale, b * scale))
        else: out.append((p, n, a * scale, b * scale))
    return pd.DataFrame(out, columns=["prov", "kab", "v2024", "v2025"])

d1 = tidy(read_xlsx(f"{SRC}/Proporsi Perempuan Pernah Kawin 15-49 tahun yang  Pernah Melahirkan Anak Lahir Hidup dalam 2 Tahun Terakhir Tidak di Fasilitas Kesehatan Menurut Kabupaten_Kota.xlsx"), 100)
d2 = tidy(read_csv(f"{SRC}/Proporsi Perempuan Pernah Kawin 15-49 tahun yang Melahirkan Anak Lahir Hidup Yang Pertama Kali Berumur Kurang dari 20 tahun Menurut KabupatenKota.csv"), 100)
d3 = tidy(read_csv(f"{SRC}/Proporsi Perempuan Umur 20-24 Tahun Yang Berstatus Kawin Atau Berstatus Hidup Bersama Sebelum Umur 18 Tahun Menurut Provinsi (Persen).csv"), 1)

# ---- geometri
g = gpd.read_file(f"{SRC}/shp/merge.shp")
g["prov"] = g.nmprov.fillna(g.PROV); g["kab"] = g.nmkab.fillna(g.KAB)
g["kode"] = g.idkab.fillna(g.ID).astype(str); g["kdk"] = g.kdkab.fillna(g.KODE_KAB).astype(int)
g["key"] = [("KOTA " if (k.startswith("KOTA ") or n >= 71) else "") + re.sub(r"^KOTA ", "", k) for k, n in zip(g.kab, g.kdk)]
g["key"] = g.key.replace(FIXSHP)
g = g[~((g.kode == "9201") & (g.prov == "PAPUA BARAT")) ].sort_values("kode", ascending=False).drop_duplicates("kode")
def kabdf(d, name):
    x = d[d.kab.notna()].copy(); x["key"] = x.kab.str.upper().replace(FIXKAB)
    return x.set_index("key")[["v2024", "v2025"]].rename(columns=lambda c: c[1:]).add_prefix(name + "_")
tab = kabdf(d2, "melahirkan_dini").join(kabdf(d1, "persalinan_nonfaskes"))
names = d2[d2.kab.notna()].assign(key=lambda x: x.kab.str.upper().replace(FIXKAB)).set_index("key").kab
g = g[g.key.isin(tab.index)].drop_duplicates("key").copy()  # kode lama Papua (91xx) digugurkan, pakai kode baru
assert not g.key.duplicated().any(), g[g.key.duplicated(keep=False)].key.tolist()
print("kab/kota cocok:", len(g), "dari", len(tab), "| tak punya poligon:", sorted(set(tab.index) - set(g.key)))
g["nama"] = [SHOW.get(k, names[k]) for k in g.key]
g["provinsi"] = g.prov.map(pretty)
g["geometry"] = g.geometry.simplify(0.01, preserve_topology=True)
pts = g.geometry.representative_point(); g["lat"], g["lon"] = pts.y.round(3), pts.x.round(3)
g = g.rename(columns={"kode": "kode_kabkota"})
ik = g[["kode_kabkota", "nama", "provinsi", "lat", "lon", "key"]].join(tab, on="key").drop(columns="key")
ik.round(2).to_csv(OUT + "indikator_kabkota.csv", index=False)
g[["kode_kabkota", "nama", "provinsi", "geometry"]].to_file(OUT + "kabkota.geojson", driver="GeoJSON", COORDINATE_PRECISION=3)

gp = g.dissolve(by="provinsi", as_index=False)[["provinsi", "geometry"]]
pp = gp.geometry.representative_point(); gp["lat"], gp["lon"] = pp.y.round(3), pp.x.round(3)
def provdf(d, name):
    x = d[d.kab.isna()].copy(); x["provinsi"] = x.prov.map(pretty)
    return x.set_index("provinsi")[["v2024", "v2025"]].rename(columns=lambda c: c[1:]).add_prefix(name + "_")
ip = provdf(d3, "perkawinan_anak").join(provdf(d2, "melahirkan_dini")).join(provdf(d1, "persalinan_nonfaskes"))
print("provinsi tanpa poligon:", sorted(set(ip.index) - set(gp.provinsi)), "| poligon tanpa data:", sorted(set(gp.provinsi) - set(ip.index)))
ip = ip.reset_index().merge(gp[["provinsi", "lat", "lon"]], on="provinsi", how="inner")
ip.round(2).to_csv(OUT + "indikator_provinsi.csv", index=False)
gp[["provinsi", "geometry"]].to_file(OUT + "provinsi.geojson", driver="GeoJSON", COORDINATE_PRECISION=3)

# ---- nasional
w = lambda f, s: openpyxl.load_workbook(f"{SRC}/{f}", read_only=True, data_only=True)[s]
ix = {r[0]: r[1:] for r in w("IPG_IKG.xlsx", "IPG_IKG").iter_rows(min_row=3, values_only=True)}
yr = [c for c in list(w("IPG_IKG.xlsx", "IPG_IKG").iter_rows(min_row=2, max_row=2, values_only=True))[0][1:] if c]
mp = {r[0]: r[1:] for r in w("managerial_parlemen.xlsx", "%perempuan").iter_rows(min_row=3, values_only=True)}
yrm = [c for c in list(w("managerial_parlemen.xlsx", "%perempuan").iter_rows(min_row=2, max_row=2, values_only=True))[0][1:] if c]
nas = pd.DataFrame({"tahun": yr, "ikg": list(ix["IKG"])[:len(yr)], "ipg": list(ix["IPG"])[:len(yr)]})
nas = nas.merge(pd.DataFrame({"tahun": yrm, "manajerial": list(mp["Managerial"])[:len(yrm)], "parlemen": list(mp["Parlemen"])[:len(yrm)]}), on="tahun")
nas.to_csv(OUT + "nasional.csv", index=False); print(nas.to_string())
rows = [l.split(";") for l in open(f"{SRC}/Perempuan di posisi managerial, menurut tingkat pendidikan.csv", encoding="utf-8-sig").read().splitlines()]
years = [int(x) for x in rows[1][1:] if x]; edu = []
for r in rows[2:]:
    if r[0] and r[1] and not r[0].startswith("Catatan"):
        edu += [(r[0].replace("<=", "≤"), y, num(v)) for y, v in zip(years, r[1:]) if v]
pd.DataFrame(edu, columns=["pendidikan", "tahun", "persen"]).to_csv(OUT + "manajerial_pendidikan.csv", index=False)
print(pd.DataFrame(edu).iloc[:, 0].unique())

# ---- migrasi (baris = tujuan/tempat tinggal sekarang, kolom = asal/5 tahun lalu)
ws = openpyxl.load_workbook(f"{SRC}/Migrasi Risen 2022.xlsx", read_only=True, data_only=True).active
R = list(ws.iter_rows(values_only=True)); head = list(R[3]); od = []
for r in R[4:]:
    if not r[0] or not re.match(r"\d+\.", str(r[0])): continue
    tuj = pretty(re.sub(r"^\d+\.\s*", "", r[0]))
    for a, v in zip(head[1:-1], r[1:-1]):
        asal = "Luar Negeri" if a == "Luar negeri" else pretty(a)
        if asal != tuj and v: od.append((asal, tuj, int(v)))
od = pd.DataFrame(od, columns=["asal", "tujuan", "jumlah"]); od.to_csv(OUT + "migrasi_od.csv", index=False)
pr = od[od.asal != "Luar Negeri"]
tot = pd.DataFrame({"masuk": pr.groupby("tujuan").jumlah.sum(), "keluar": pr.groupby("asal").jumlah.sum()}).fillna(0).astype(int)
tot["neto"] = tot.masuk - tot.keluar; tot.rename_axis("provinsi").reset_index().to_csv(OUT + "migrasi_total.csv", index=False)
print(len(od), od.asal.nunique(), od.tujuan.nunique(), tot.sort_values("neto").iloc[[0, -1]])
