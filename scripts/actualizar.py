import json, os, sys, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone

KEY = os.environ.get("API_SPORTS_KEY", "")
BASE = "https://v1.rugby.api-sports.io"
TORNEOS = [  # (nombre en la API, pais o None, nombre para mostrar)
    ("Top 12", "Argentina", "🇦🇷 URBA Top 12"),
    ("Premiership Rugby", "England", "🏴 Premiership"),
    ("Top 14", "France", "🇫🇷 Top 14"),
    ("Super Rugby", None, "🏉 Super Rugby Pacific"),
    ("United Rugby Championship", None, "🏆 United Rugby Championship"),
    ("European Rugby Champions Cup", None, "🏆 Champions Cup"),
]
avisos = []

def api(path, **params):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"x-apisports-key": KEY})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
        if data.get("errors"):
            avisos.append(f"{path} {params}: {data['errors']}")
        return data.get("response") or []
    except Exception as e:
        avisos.append(f"{path} {params}: {e}")
        return []

def main():
    if not KEY:
        sys.exit("Falta la clave API_SPORTS_KEY")
    ahora = datetime.now(timezone.utc)
    ligas = api("/leagues")
    res, prox, vistos = [], [], set()
    for nombre, pais, mostrar in TORNEOS:
        lid = None
        for l in ligas:
            n = (l.get("name") or "").lower()
            p = ((l.get("country") or {}).get("name") or "").lower()
            if n == nombre.lower() and (pais is None or p == pais.lower()):
                lid = l["id"]; break
        if lid is None:
            avisos.append(f"No encontré el torneo: {nombre}"); continue
        for temporada in (ahora.year, ahora.year - 1):
            for g in api("/games", league=lid, season=temporada):
                if g["id"] in vistos: continue
                vistos.add(g["id"])
                try: f = datetime.fromisoformat(g["date"].replace("Z", "+00:00"))
                except Exception: continue
                st = ((g.get("status") or {}).get("short") or "").upper()
                fila = {"torneo": mostrar, "fecha": f.isoformat(),
                        "local": g["teams"]["home"]["name"], "visitante": g["teams"]["away"]["name"]}
                if st in ("FT", "AET", "AP", "PEN") and ahora - timedelta(days=10) <= f <= ahora:
                    fila["puntos_local"] = g["scores"]["home"]; fila["puntos_visitante"] = g["scores"]["away"]
                    res.append(fila)
                elif st == "NS" and ahora <= f <= ahora + timedelta(days=7):
                    prox.append(fila)
    if not res and not prox:
        print("Sin datos nuevos; no se modifica nada.", avisos); sys.exit(1)
    res.sort(key=lambda x: x["fecha"], reverse=True); prox.sort(key=lambda x: x["fecha"])
    out = {"actualizado": ahora.isoformat(), "resultados": res, "proximos": prox, "avisos": avisos}
    json.dump(out, open("data/resultados.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(res), "resultados,", len(prox), "proximos.", avisos)

main()
