# 🧬 Open Laboratory Datasets & Bench Constants

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Verified Data](https://img.shields.io/badge/Data-PubChem%20%7C%20Cellosaurus%20%7C%20ANSI--SLAS-00F0FF)](https://meniska.app)
[![Precision Math](https://img.shields.io/badge/Math-Zero%20Float%20Drift-green)](https://meniska.app)

A clean, standardized, machine-readable collection of fundamental wet-bench laboratory constants, chemical MWs, ATCC cell line proliferation metrics, and ANSI/SLAS consumable dimensions.

Designed for bioinformaticians, biotech software developers, and research students.

---

### 🚀 Looking for the Interactive Lab Companion?

All these datasets power **[meniska (meniska.app)](https://meniska.app)** — the precision offline-first companion for wet-bench science (лабораторный калькулятор для биоинженерии и химии).

* **Bench Mode:** High-contrast, wake-locked step-by-step guidance designed to be tapped with latex/nitrile gloves.
* **16 Specialized Calculators:** C1V1 serial dilutions, DNA assembly (Gibson/Golden Gate), mRNA-LNP formulation, ELISA 4PL/5PL regression, HPLC method transfer, and bioreactor scale-up.
* **Zero-Float Drift:** Native 128-bit decimal arithmetic engine.

👉 **[Launch Free Web App](https://meniska.app)** | Available for Android & iOS.

---

## 📦 What's Inside

| File | Records | Source Standard | Description |
| :--- | :--- | :--- | :--- |
| `data/reagents.json` | 274 | NIH PubChem / IUPAC | Curated buffer salts, acids, bases with exact MW, pKa, and CAS numbers |
| `data/reagents_sample.json` | 100 | NIH PubChem / IUPAC | Lightweight sample subset of most common laboratory reagents |
| `data/cell_lines.json` | 74 | SIB Cellosaurus / ATCC | Proliferation kinetics, doubling times (DT), and seeding densities |
| `data/labware_ansi_slas.json` | 31 | ANSI/SLAS Standard | Well surface areas ($cm^2$), operating volumes, and vessel geometry |
| `data/pipettes.json` | 13 | ISO 8655-2 Metrology | Piston & positive-displacement pipette volumes, systematic and random errors |
| `data/pka_scales.json` | 4 Scales | EMBOSS / IPC 2.0 / Lehninger / Bjellqvist | Complete amino acid and terminus pKa dissociation scales for protein pI |

## 🔧 Automation Tools

* `tools/fetch_pubchem_cellosaurus.py`: Python CLI tool to query NIH PubChem PUG REST API and SIB Cellosaurus REST API to fetch verified molecular passports and cell proliferation kinetics.
---
### 🌐 Localization & Community
Meniska is an offline-first laboratory calculator (лабораторный калькулятор) supporting researchers worldwide. Documentation and web-bench tools are available at [meniska.app](https://meniska.app).

## 🛠️ Usage Example (Python / JSON)

```python
import json

with open("data/cell_lines.json", "r") as f:
    cells = json.load(f)

# Find doubling time for CHO-K1
cho = next(c for c in cells if c["name"] == "CHO-K1")
print(f"CHO-K1 DT: {cho['doublingTimeHours']} hours")
