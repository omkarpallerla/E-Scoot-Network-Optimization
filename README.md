# ⚡ E-Scoot Charging Network Optimization (MILP + Power BI)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Azure](https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)

> **Mixed-Integer Linear Programming solving the Facility Location Problem for EV charging infrastructure — saving 19% of budget. Results visualized in a Power BI Azure Maps dashboard.**

---

## 📌 Business Overview

This project applies Operations Research to design the charging infrastructure for an E-Scooter fleet at Arizona State University — solving where to build stations and how many chargers to install to minimize cost while meeting all demand and equity constraints.

Solver output is exported to a **Power BI Azure Maps dashboard** giving campus operations a live command center.

---

## 🧮 Mathematical Model (MILP)

```
Minimize: Σ(Fixed_Cost × y_i) + Σ(Charger_Cost × x_i)

Subject to:
  Σ x_i ≥ Total_Demand          (Demand satisfaction)
  Σ Cost_i ≤ $35,000            (Budget constraint)
  Residential_Coverage ≥ 70%    (Equity constraint)
  y_i ∈ {0,1}, x_i ∈ Z+        (Binary/integer)
```

---

## 📈 Key Results

| Metric | Value |
|--------|-------|
| **Optimal Cost** | $28,350 |
| **Budget Saved** | $6,650 (19% under budget) |
| **Sites Selected** | 4 of 8 candidates |
| **Demand Met** | 100% |
| **Residential Coverage** | 73% (exceeds 70% constraint) |

---

## 🧠 BI Output: Azure Maps Dashboard

```
Gurobi Solver → station_results.csv → Power BI + Azure Maps
→ Campus Ops Dashboard (station map, utilization heatmap, budget breakdown)
```

---

## 🛠 Tools & Stack

| Category | Tools |
|----------|-------|
| Optimization | Python, Gurobi (gurobipy), MILP |
| Visualization | Matplotlib, Plotly, Folium |
| BI Output | CSV → Power BI Azure Maps Dashboard |
| Cloud | Azure Maps API for geospatial visualization |

---

## 🚀 How to Run

```bash
git clone https://github.com/omkarpallerla/E-Scoot-Network-Optimization.git
cd E-Scoot-Network-Optimization
pip install -r requirements.txt
# Note: Gurobi requires a license (free academic license at gurobi.com)
jupyter notebook notebooks/EScoot_MILP_Optimization.ipynb
```

---

<div align="center">
  <sub>Built by <a href="https://github.com/omkarpallerla">Omkar Pallerla</a> · MS Business Analytics, ASU · BI Engineer · Azure | GCP | Databricks Certified</sub>
</div>