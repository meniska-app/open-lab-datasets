#!/usr/bin/env python3
"""
Menisca Official Databases Synchronization Script
=================================================
Fetches and updates verified molecular passports from NIH PubChem PUG REST API
(https://pubchem.ncbi.nlm.nih.gov/rest/pug) and cell line records from
SIB ExPASy Cellosaurus REST API (https://api.cellosaurus.org), exporting them
into JSON or Dart preset snippets for Menisca's Offline-First Reagent Vault.

Usage:
  python tools/fetch_pubchem_cellosaurus.py --cid 6503 23831 5234
  python tools/fetch_pubchem_cellosaurus.py --cvcl CVCL_0045 CVCL_0030
  python tools/fetch_pubchem_cellosaurus.py --export-json official_sync_dump.json
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List


PUBCHEM_PUG_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid"
CELLOSAURUS_API_BASE = "https://api.cellosaurus.org/cell-line"


def fetch_pubchem_compound(cid: int) -> Dict[str, Any]:
    """Fetches IUPAC name, molecular formula, exact molecular weight, and CAS from NIH PubChem."""
    props = "Title,IUPACName,MolecularFormula,MolecularWeight"
    url = f"{PUBCHEM_PUG_BASE}/{cid}/property/{props}/JSON"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "MeniscaLabSuite/1.0 (https://menisca.app)"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    prop_table = payload.get("PropertyTable", {}).get("Properties", [{}])[0]

    # Fetch synonyms to extract CAS Registry Number
    syn_url = f"{PUBCHEM_PUG_BASE}/{cid}/synonyms/JSON"
    synonyms: List[str] = []
    cas_number = "N/A"
    try:
        syn_req = urllib.request.Request(
            syn_url,
            headers={"User-Agent": "MeniscaLabSuite/1.0 (https://menisca.app)"},
        )
        with urllib.request.urlopen(syn_req, timeout=15) as syn_resp:
            syn_data = json.loads(syn_resp.read().decode("utf-8"))
            info_list = (
                syn_data.get("InformationList", {}).get("Information", [{}])[0]
            )
            raw_syns = info_list.get("Synonym", [])
            synonyms = raw_syns[:6]
            for s in raw_syns:
                parts = s.split("-")
                if (
                    len(parts) == 3
                    and parts[0].isdigit()
                    and parts[1].isdigit()
                    and parts[2].isdigit()
                ):
                    cas_number = s
                    break
    except urllib.error.URLError:
        pass

    return {
        "pubchemCid": cid,
        "nameEn": prop_table.get("Title", f"CID {cid}"),
        "iupacName": prop_table.get("IUPACName", ""),
        "formula": prop_table.get("MolecularFormula", ""),
        "mw": str(prop_table.get("MolecularWeight", "0")),
        "casNumber": cas_number,
        "synonyms": synonyms,
    }


def fetch_cellosaurus_line(cvcl_id: str) -> Dict[str, Any]:
    """Fetches cell line metadata from SIB ExPASy Cellosaurus API."""
    params = urllib.parse.urlencode({"format": "json", "fields": "id,sy,ox,ca,ag,sx,dr"})
    url = f"{CELLOSAURUS_API_BASE}/{cvcl_id}?{params}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "MeniscaLabSuite/1.0 (https://menisca.app)"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    cell_list = payload.get("Cellosaurus", {}).get("cell-line-list", [])
    if not cell_list:
        return {"cellosaurusId": cvcl_id, "error": "Not found"}

    entry = cell_list[0]
    names = entry.get("name-list", [])
    primary_name = names[0].get("value", cvcl_id) if names else cvcl_id

    species_list = entry.get("species-list", [])
    organism = (
        species_list[0].get("label", "Homo sapiens")
        if species_list
        else "Homo sapiens"
    )

    return {
        "cellosaurusId": cvcl_id,
        "name": primary_name,
        "organism": organism,
        "category": entry.get("category", "Cell line"),
    }


def format_dart_reagent_snippet(record: Dict[str, Any]) -> str:
    """Formats a PubChem dictionary as a Menisca Dart ReagentRecord constructor."""
    cid = record["pubchemCid"]
    name_en = record["nameEn"].replace("'", "\\'")
    iupac = record["iupacName"].replace("'", "\\'")
    formula = record["formula"]
    mw = record["mw"]
    cas = record["casNumber"]
    return (
        f"  ReagentRecord(\n"
        f"    id: 'cid_{cid}',\n"
        f"    nameRu: '{name_en}',\n"
        f"    nameEn: '{name_en}',\n"
        f"    iupacName: '{iupac}',\n"
        f"    synonyms: {json.dumps(record['synonyms'][:3], ensure_ascii=False)},\n"
        f"    formula: '{formula}',\n"
        f"    casNumber: '{cas}',\n"
        f"    pubchemCid: {cid},\n"
        f"    mw: _d('{mw}'),\n"
        f"    solubilityWater: 'См. паспорт PubChem',\n"
        f"    storageTemp: 'RT',\n"
        f"    hazardCode: 'GHS07',\n"
        f"    category: LabPersona.bioCell,\n"
        f"    structureType: StructureSkeletonType.ring6,\n"
        f"  ),"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync NIH PubChem and SIB Cellosaurus records for Menisca."
    )
    parser.add_argument(
        "--cid",
        type=int,
        nargs="*",
        default=[],
        help="PubChem Compound IDs (CIDs) to fetch (e.g. 6503 23831 5234)",
    )
    parser.add_argument(
        "--cvcl",
        type=str,
        nargs="*",
        default=[],
        help="Cellosaurus accession IDs (e.g. CVCL_0045 CVCL_0030)",
    )
    parser.add_argument(
        "--export-json",
        type=str,
        default="",
        help="Optional path to export fetched data as JSON",
    )
    args = parser.parse_args()

    if not args.cid and not args.cvcl:
        print("Menisca Official Database Sync Tool (NIH PubChem & SIB Cellosaurus)")
        print("Usage example: python tools/fetch_pubchem_cellosaurus.py --cid 6503 --cvcl CVCL_0045")
        return 0

    results: Dict[str, Any] = {"reagents": [], "cellLines": []}

    for cid in args.cid:
        try:
            rec = fetch_pubchem_compound(cid)
            results["reagents"].append(rec)
            print(format_dart_reagent_snippet(rec))
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Failed to fetch PubChem CID {cid}: {exc}", file=sys.stderr)

    for cvcl in args.cvcl:
        try:
            line = fetch_cellosaurus_line(cvcl)
            results["cellLines"].append(line)
            print(f"// Cellosaurus: {json.dumps(line, ensure_ascii=False)}")
        except Exception as exc:  # noqa: BLE001
            print(
                f"[WARN] Failed to fetch Cellosaurus {cvcl}: {exc}",
                file=sys.stderr,
            )

    if args.export_json:
        with open(args.export_json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Exported {len(results['reagents'])} reagents and {len(results['cellLines'])} cell lines to {args.export_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

