#!/usr/bin/env python3
"""Ingesta del modelo ESTOCÁSTICO HIDROTÉRMICO ENOS + CVaR (sddp_v16) del grupo.

Se alimenta DIRECTO de la publicación del modelo (GitHub Pages) — integración
automática diaria, con override local si se deposita el archivo en
data/modelos_externos/enos_cvar_resultados.json.

Fuente: https://fredypaeze.github.io/modelo-enos-minenergia/sddp_v16/
        (consume resultados_dashboard_v12.json, Montecarlo 10.000 simulaciones)

Extrae por horizonte (escenario ponderado NOAA): costo base, sobrecosto ENOS,
CVaR95, prob. de estrés hídrico, respaldo térmico requerido — y hace el CRUCE
con las capas observadas de Tuxilo: respaldo térmico requerido vs energía firme
a gas (ENFICC) y gas interrumpible → ¿el respaldo que pide el modelo cabe en la
capacidad real?

Publica: data/gold/enos_cvar_summary.json
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import requests

WS = Path.home() / ".openclaw" / "workspace"
DROP = WS / "data" / "modelos_externos"
GOLD = WS / "data" / "gold"
URL = "https://fredypaeze.github.io/modelo-enos-minenergia/sddp_v16/resultados_dashboard_v12.json"
TIMEOUT = 30


REPO_LOCAL = Path.home() / "modelos-externos" / "modelo-enos-minenergia"
REPO_JSON = REPO_LOCAL / "docs" / "sddp_v16" / "resultados_dashboard_v12.json"


def _sync_repo() -> bool:
    """git pull del repo del modelo (auto-hospedado en esta máquina)."""
    if not (REPO_LOCAL / ".git").exists():
        return False
    r = subprocess_run(["git", "-C", str(REPO_LOCAL), "pull", "--ff-only", "-q"], timeout=60)
    return r == 0


def subprocess_run(cmd, timeout=60) -> int:
    import subprocess
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout).returncode
    except Exception:
        return 1


def _publicar_visualizacion() -> None:
    """Copia la visualización del modelo a la web propia (canvas/tuxilo/sddp/)."""
    import shutil
    destino = Path.home() / ".openclaw" / "canvas" / "tuxilo" / "sddp"
    origen = REPO_LOCAL / "docs" / "sddp_v16"
    if origen.exists():
        destino.mkdir(parents=True, exist_ok=True)
        for f in origen.iterdir():
            if f.is_file():
                shutil.copy2(f, destino / f.name)


def _cargar() -> tuple[dict, str]:
    # prioridad: override manual → repo local sincronizado → URL pública → cache
    local = DROP / "enos_cvar_resultados.json"
    if local.exists():
        return json.loads(local.read_text(encoding="utf-8")), f"override local ({local.name})"
    _sync_repo()
    if REPO_JSON.exists():
        _publicar_visualizacion()
        return json.loads(REPO_JSON.read_text(encoding="utf-8")), "repo auto-hospedado (git pull diario)"
    r = requests.get(URL, timeout=TIMEOUT)
    r.raise_for_status()
    DROP.mkdir(parents=True, exist_ok=True)
    (DROP / "enos_cvar_cache.json").write_text(r.text, encoding="utf-8")  # evidencia bronze
    return r.json(), "GitHub Pages (publicación del grupo)"


def run() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    try:
        d, origen = _cargar()
    except Exception as e:  # noqa: BLE001
        # conservar el último cache si la URL falla
        cache = DROP / "enos_cvar_cache.json"
        if cache.exists():
            d, origen = json.loads(cache.read_text(encoding="utf-8")), "cache local (URL no disponible)"
        else:
            out = {"generated_at": now, "status": "sin_datos", "error": str(e)[:100]}
            (GOLD / "enos_cvar_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
            print("ENOS+CVaR: sin datos (URL y cache no disponibles).")
            return out

    res = d.get("resultados") or {}
    pond = res.get("ponderado_noaa") or {}
    por_horizonte = []
    for h in sorted(pond, key=lambda x: int(x)):
        r = pond[h]
        dias = r.get("dias_efectivos_simulados") or int(h)
        por_horizonte.append({
            "horizonte_dias": int(h),
            "costo_base_mm": r.get("costo_base_normal_miles_millones"),
            "sobrecosto_enos_mm": r.get("sobrecosto_respaldo_vs_neutro_miles_millones"),
            "cvar95_mm": r.get("cvar95_respaldo_miles_millones"),
            "prob_estres_hidrico_pct": r.get("prob_estres_hidrico_horizonte_pct"),
            "precio_normal": r.get("precio_normal_cop_kwh"),
            "precio_escenario": r.get("precio_escenario_promedio_cop_kwh"),
            "respaldo_termico_gwh_dia": round(r.get("respaldo_termico_requerido_gwh", 0) / dias, 1) if dias else None,
            "mix_hidro_pct": (r.get("mix_estimado") or {}).get("hidro_pct"),
        })

    # tabla comparativa de escenarios a 90 días
    escenarios_90 = []
    for key, meta in (d.get("escenarios") or {}).items():
        r = (res.get(key) or {}).get("90")
        if r:
            dias = r.get("dias_efectivos_simulados") or 90
            escenarios_90.append({
                "escenario": meta.get("label", key),
                "sobrecosto_mm": r.get("sobrecosto_respaldo_vs_neutro_miles_millones"),
                "cvar95_mm": r.get("cvar95_respaldo_miles_millones"),
                "prob_estres_pct": r.get("prob_estres_hidrico_horizonte_pct"),
                "respaldo_gwh_dia": round(r.get("respaldo_termico_requerido_gwh", 0) / dias, 1) if dias else None,
                "orden": meta.get("orden", 9),
            })
    escenarios_90.sort(key=lambda x: x["orden"])

    # --- CRUCE con capas observadas Tuxilo: ¿cabe el respaldo requerido? ---
    enficc = {}
    p = GOLD / "enficc_summary.json"
    if p.exists():
        enficc = json.loads(p.read_text(encoding="utf-8"))
    enficc_gas = enficc.get("enficc_gas_gwh")
    firme_riesgo = enficc.get("energia_firme_gas_en_riesgo_gwh")
    ref90 = next((x for x in por_horizonte if x["horizonte_dias"] == 90), None)
    cruce = None
    if ref90 and ref90.get("respaldo_termico_gwh_dia") and enficc_gas:
        req = ref90["respaldo_termico_gwh_dia"]
        cruce = {
            "respaldo_requerido_gwh_dia_90d": req,
            "enficc_gas_gwh_dia": enficc_gas,
            "cobertura_pct": round(enficc_gas / req * 100, 0),
            "enficc_gas_sin_interrumpible": round(enficc_gas - (firme_riesgo or 0), 1),
            "cobertura_sin_interrumpible_pct": round((enficc_gas - (firme_riesgo or 0)) / req * 100, 0),
            "nota": ("Cruce modelo↔observado: el respaldo térmico que el modelo estocástico requiere (ponderado NOAA, 90d) "
                     "vs la energía firme a gas observada (ENFICC). Si se descuenta el gas interrumpible, la cobertura cae — "
                     "la restricción de combustible es el supuesto que el modelo aún no incorpora."),
        }

    out = {
        "generated_at": now,
        "status": "cargado",
        "origen": origen,
        "modelo": d.get("modelo"), "version": d.get("version"),
        "modelo_generado": d.get("generado"), "fecha_corte": d.get("fecha_corte"),
        "n_simulaciones": d.get("n_simulaciones"),
        "ponderado_por_horizonte": por_horizonte,
        "escenarios_90d": escenarios_90,
        "cruce_respaldo_observado": cruce,
        "nota": ("Modelo estocástico hidrotérmico ENOS+CVaR del grupo (capa ECONÓMICA del riesgo: costo base → "
                 "sobrecosto ENOS → CVaR → prima). Montecarlo sobre volumen de embalses con escenarios ENOS. "
                 "Capa en validación: presentación, no alimenta el índice. Cifras en miles de millones de COP."),
    }
    (GOLD / "enos_cvar_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    c90 = ref90 or {}
    print(f"ENOS+CVaR {d.get('version')} ({d.get('generado')}): 90d sobrecosto {c90.get('sobrecosto_enos_mm')} MM · "
          f"CVaR95 {c90.get('cvar95_mm')} MM · respaldo req {c90.get('respaldo_termico_gwh_dia')} GWh/d · "
          f"cobertura firme gas {cruce.get('cobertura_pct') if cruce else 'N/D'}%")
    return out


if __name__ == "__main__":
    run()
