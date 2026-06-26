import csv
import os
import math


def median(values):
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
    return sorted_vals[mid]


def distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


QUARTIERS_TOULON = {
    "Mourillon":     (43.1189, 5.9441),
    "Centre-ville":  (43.1247, 5.9302),
    "Haute-ville":   (43.1268, 5.9280),
    "Saint-Roch":    (43.1198, 5.9198),
    "Sainte-Anne":   (43.1150, 5.9050),
    "Pont du Las":   (43.1320, 5.9150),
    "Siblas":        (43.1380, 5.9220),
    "Valbertrand":   (43.1420, 5.9350),
    "Saint-Jean":    (43.1100, 5.9320),
    "Aguillon":      (43.1280, 5.9420),
    "La Rode":       (43.1350, 5.9480),
    "Bon Rencontre": (43.1230, 5.9350),
}


def assign_quartier(lat, lon):
    min_dist = float("inf")
    closest = "Autre"
    for quartier, (qlat, qlon) in QUARTIERS_TOULON.items():
        d = distance_km(lat, lon, qlat, qlon)
        if d < min_dist:
            min_dist = d
            closest = quartier
    return closest


def compute_dvf_medianes(output_file=None):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if output_file is None:
        output_file = os.path.join(base, "data", "dvf_medianes.csv")

    raw_folder = os.path.join(base, "data", "raw")

    transactions = []
    for filename in os.listdir(raw_folder):
        if filename.endswith(".csv") and "83137" in filename:
            filepath = os.path.join(raw_folder, filename)
            with open(filepath, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    transactions.append(row)

    print(f"{len(transactions)} transactions brutes chargées")

    quartiers = {}
    skipped = 0

    for t in transactions:
        try:
            type_local = t.get("type_local", "")
            if type_local not in ["Appartement", "Maison"]:
                skipped += 1
                continue

            prix_str = t.get("valeur_fonciere", "").replace(",", ".").strip()
            surface_str = t.get("surface_reelle_bati", "").replace(",", ".").strip()
            lat_str = t.get("latitude", "").replace(",", ".").strip()
            lon_str = t.get("longitude", "").replace(",", ".").strip()

            if not prix_str or not surface_str or not lat_str or not lon_str:
                skipped += 1
                continue

            prix = float(prix_str)
            surface = float(surface_str)
            lat = float(lat_str)
            lon = float(lon_str)

            if prix <= 0 or surface <= 0 or lat == 0 or lon == 0:
                skipped += 1
                continue

            prix_m2 = prix / surface
            # Filtre anti-aberrations : entre 500 et 15000 €/m²
            if prix_m2 < 500 or prix_m2 > 15000:
                skipped += 1
                continue

            quartier = assign_quartier(lat, lon)
            quartier = assign_quartier(lat, lon)

            if quartier not in quartiers:
                quartiers[quartier] = []
            quartiers[quartier].append(prix_m2)

        except Exception:
            skipped += 1
            continue

    print(f"{skipped} transactions ignorées")

    resultats = []
    for quartier, prix_m2_list in quartiers.items():
        if len(prix_m2_list) < 3:
            continue
        resultats.append({
            "quartier": quartier,
            "mediane_prix_m2": round(median(prix_m2_list)),
            "moyenne_prix_m2": round(sum(prix_m2_list) / len(prix_m2_list)),
            "nb_transactions": len(prix_m2_list),
            "prix_m2_min": round(min(prix_m2_list)),
            "prix_m2_max": round(max(prix_m2_list)),
        })

    resultats.sort(key=lambda x: x["mediane_prix_m2"], reverse=True)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fields = ["quartier", "mediane_prix_m2", "moyenne_prix_m2",
                  "nb_transactions", "prix_m2_min", "prix_m2_max"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(resultats)

    print(f"\n✅ {len(resultats)} quartiers analysés :")
    for r in resultats:
        print(f"  {r['quartier']} : {r['mediane_prix_m2']} €/m² ({r['nb_transactions']} transactions)")

    return resultats


if __name__ == "__main__":
    compute_dvf_medianes()