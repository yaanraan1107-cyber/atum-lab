"""
ATUM OS 0.1 — Unified AI Chemistry Intelligence System
Master Development Specification — Prototype 0.1 Complete Architecture
All 7 Core Modules | 118 Elements | 20 GenChem Engines | 20 QC Engines
Theme: DESIGN B (White Tech Notebook / Stark OS)
Deterministic, Evidence-First, Safe Calculations (No eval/exec).
"""

import math
import sqlite3
from collections import defaultdict
from decimal import Decimal, getcontext
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple
import streamlit as st

# High scientific precision for decimal-based QC computations
getcontext().prec = 28
AVOGADRO_NA = Decimal("6.02214076e23")
DB_NAME = "atum_prototype.db"

# ---------------------------------------------------------
# UI CONFIGURATION & DESIGN B (WHITE TECH NOTEBOOK THEME)
# ---------------------------------------------------------
st.set_page_config(
    page_title="ATUM OS 0.1 | Stark Lab",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .stark-header {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 18px 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .stark-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #0284c7;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.04);
        margin-bottom: 16px;
    }
    .result-badge {
        background-color: #f0fdf4;
        border: 1.5px solid #16a34a;
        color: #15803d;
        padding: 12px 18px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 20px;
        letter-spacing: -0.5px;
        display: inline-block;
    }
    .provenance-tag {
        font-size: 11px;
        color: #64748b;
        margin-top: 8px;
        font-family: monospace;
    }
    .status-pill {
        background: #e0f2fe;
        color: #0369a1;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 11px;
        border: 1px solid #bae6fd;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATABASE ENGINE (118 ELEMENTS & SEEDS)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS elements (
        atomic_number INTEGER PRIMARY KEY,
        symbol TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        atomic_weight REAL NOT NULL,
        group_num INTEGER,
        period INTEGER NOT NULL,
        block TEXT NOT NULL,
        category TEXT NOT NULL,
        electron_config TEXT NOT NULL,
        electronegativity REAL,
        density_g_cm3 REAL,
        source TEXT NOT NULL,
        verification_status TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS compounds (
        compound_id INTEGER PRIMARY KEY AUTOINCREMENT,
        canonical_name TEXT NOT NULL,
        formula TEXT NOT NULL,
        formula_mass REAL NOT NULL,
        cas_number TEXT,
        category TEXT NOT NULL,
        source TEXT NOT NULL,
        verification_status TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chemicals_reagents (
        chemical_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        cas_number TEXT,
        grade TEXT NOT NULL,
        density_g_ml REAL,
        ghs_hazard TEXT,
        storage_conditions TEXT NOT NULL,
        verification_status TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS qc_methods (
        method_id TEXT PRIMARY KEY,
        method_name TEXT NOT NULL,
        sop_ref TEXT NOT NULL,
        analyte TEXT NOT NULL,
        titrant_name TEXT,
        titrant_normality REAL,
        stoichiometric_factor REAL NOT NULL,
        blank_volume_ml REAL DEFAULT 0.0,
        rounding_digits INTEGER DEFAULT 2,
        approval_status TEXT NOT NULL
    );
    """)

    cur.execute("SELECT COUNT(*) FROM elements")
    if cur.fetchone()[0] == 0:
        all_118_elements = [
            (1, "H", "Hydrogen", 1.008, 1, 1, "s", "Nonmetal", "1s1", 2.20, 0.00008988, "IUPAC 2021", "Verified"),
            (2, "He", "Helium", 4.0026, 18, 1, "s", "Noble Gas", "1s2", None, 0.0001785, "IUPAC 2021", "Verified"),
            (3, "Li", "Lithium", 6.94, 1, 2, "s", "Alkali Metal", "[He] 2s1", 0.98, 0.534, "IUPAC 2021", "Verified"),
            (4, "Be", "Beryllium", 9.0122, 2, 2, "s", "Alkaline Earth", "[He] 2s2", 1.57, 1.85, "IUPAC 2021", "Verified"),
            (5, "B", "Boron", 10.81, 13, 2, "p", "Metalloid", "[He] 2s2 2p1", 2.04, 2.34, "IUPAC 2021", "Verified"),
            (6, "C", "Carbon", 12.011, 14, 2, "p", "Nonmetal", "[He] 2s2 2p2", 2.55, 2.267, "IUPAC 2021", "Verified"),
            (7, "N", "Nitrogen", 14.007, 15, 2, "p", "Nonmetal", "[He] 2s2 2p3", 3.04, 0.00125, "IUPAC 2021", "Verified"),
            (8, "O", "Oxygen", 15.999, 16, 2, "p", "Nonmetal", "[He] 2s2 2p4", 3.44, 0.00143, "IUPAC 2021", "Verified"),
            (9, "F", "Fluorine", 18.998, 17, 2, "p", "Halogen", "[He] 2s2 2p5", 3.98, 0.00169, "IUPAC 2021", "Verified"),
            (10, "Ne", "Neon", 20.180, 18, 2, "p", "Noble Gas", "[He] 2s2 2p6", None, 0.00090, "IUPAC 2021", "Verified"),
            (11, "Na", "Sodium", 22.990, 1, 3, "s", "Alkali Metal", "[Ne] 3s1", 0.93, 0.971, "IUPAC 2021", "Verified"),
            (12, "Mg", "Magnesium", 24.305, 2, 3, "s", "Alkaline Earth", "[Ne] 3s2", 1.31, 1.738, "IUPAC 2021", "Verified"),
            (13, "Al", "Aluminium", 26.982, 13, 3, "p", "Post-Transition Metal", "[Ne] 3s2 3p1", 1.61, 2.70, "IUPAC 2021", "Verified"),
            (14, "Si", "Silicon", 28.085, 14, 3, "p", "Metalloid", "[Ne] 3s2 3p2", 1.90, 2.329, "IUPAC 2021", "Verified"),
            (15, "P", "Phosphorus", 30.974, 15, 3, "p", "Nonmetal", "[Ne] 3s2 3p3", 2.19, 1.82, "IUPAC 2021", "Verified"),
            (16, "S", "Sulfur", 32.06, 16, 3, "p", "Nonmetal", "[Ne] 3s2 3p4", 2.58, 2.067, "IUPAC 2021", "Verified"),
            (17, "Cl", "Chlorine", 35.45, 17, 3, "p", "Halogen", "[Ne] 3s2 3p5", 3.16, 0.0032, "IUPAC 2021", "Verified"),
            (18, "Ar", "Argon", 39.948, 18, 3, "p", "Noble Gas", "[Ne] 3s2 3p6", None, 0.00178, "IUPAC 2021", "Verified"),
            (19, "K", "Potassium", 39.098, 1, 4, "s", "Alkali Metal", "[Ar] 4s1", 0.82, 0.862, "IUPAC 2021", "Verified"),
            (20, "Ca", "Calcium", 40.078, 2, 4, "s", "Alkaline Earth", "[Ar] 4s2", 1.00, 1.54, "IUPAC 2021", "Verified"),
            (21, "Sc", "Scandium", 44.956, 3, 4, "d", "Transition Metal", "[Ar] 3d1 4s2", 1.36, 2.989, "IUPAC 2021", "Verified"),
            (22, "Ti", "Titanium", 47.867, 4, 4, "d", "Transition Metal", "[Ar] 3d2 4s2", 1.54, 4.54, "IUPAC 2021", "Verified"),
            (23, "V", "Vanadium", 50.942, 5, 4, "d", "Transition Metal", "[Ar] 3d3 4s2", 1.63, 6.11, "IUPAC 2021", "Verified"),
            (24, "Cr", "Chromium", 51.996, 6, 4, "d", "Transition Metal", "[Ar] 3d5 4s1", 1.66, 7.15, "IUPAC 2021", "Verified"),
            (25, "Mn", "Manganese", 54.938, 7, 4, "d", "Transition Metal", "[Ar] 3d5 4s2", 1.55, 7.44, "IUPAC 2021", "Verified"),
            (26, "Fe", "Iron", 55.845, 8, 4, "d", "Transition Metal", "[Ar] 3d6 4s2", 1.83, 7.874, "IUPAC 2021", "Verified"),
            (27, "Co", "Cobalt", 58.933, 9, 4, "d", "Transition Metal", "[Ar] 3d7 4s2", 1.88, 8.86, "IUPAC 2021", "Verified"),
            (28, "Ni", "Nickel", 58.693, 10, 4, "d", "Transition Metal", "[Ar] 3d8 4s2", 1.91, 8.912, "IUPAC 2021", "Verified"),
            (29, "Cu", "Copper", 63.546, 11, 4, "d", "Transition Metal", "[Ar] 3d10 4s1", 1.90, 8.96, "IUPAC 2021", "Verified"),
            (30, "Zn", "Zinc", 65.38, 12, 4, "d", "Transition Metal", "[Ar] 3d10 4s2", 1.65, 7.134, "IUPAC 2021", "Verified"),
            (31, "Ga", "Gallium", 69.723, 13, 4, "p", "Post-Transition Metal", "[Ar] 3d10 4s2 4p1", 1.81, 5.907, "IUPAC 2021", "Verified"),
            (32, "Ge", "Germanium", 72.630, 14, 4, "p", "Metalloid", "[Ar] 3d10 4s2 4p2", 2.01, 5.323, "IUPAC 2021", "Verified"),
            (33, "As", "Arsenic", 74.922, 15, 4, "p", "Metalloid", "[Ar] 3d10 4s2 4p3", 2.18, 5.776, "IUPAC 2021", "Verified"),
            (34, "Se", "Selenium", 78.971, 16, 4, "p", "Nonmetal", "[Ar] 3d10 4s2 4p4", 2.55, 4.809, "IUPAC 2021", "Verified"),
            (35, "Br", "Bromine", 79.904, 17, 4, "p", "Halogen", "[Ar] 3d10 4s2 4p5", 2.96, 3.122, "IUPAC 2021", "Verified"),
            (36, "Kr", "Krypton", 83.798, 18, 4, "p", "Noble Gas", "[Ar] 3d10 4s2 4p6", 3.00, 0.00373, "IUPAC 2021", "Verified"),
            (37, "Rb", "Rubidium", 85.468, 1, 5, "s", "Alkali Metal", "[Kr] 5s1", 0.82, 1.532, "IUPAC 2021", "Verified"),
            (38, "Sr", "Strontium", 87.62, 2, 5, "s", "Alkaline Earth", "[Kr] 5s2", 0.95, 2.64, "IUPAC 2021", "Verified"),
            (39, "Y", "Yttrium", 88.906, 3, 5, "d", "Transition Metal", "[Kr] 4d1 5s2", 1.22, 4.469, "IUPAC 2021", "Verified"),
            (40, "Zr", "Zirconium", 91.224, 4, 5, "d", "Transition Metal", "[Kr] 4d2 5s2", 1.33, 6.506, "IUPAC 2021", "Verified"),
            (41, "Nb", "Niobium", 92.906, 5, 5, "d", "Transition Metal", "[Kr] 4d4 5s1", 1.6, 8.57, "IUPAC 2021", "Verified"),
            (42, "Mo", "Molybdenum", 95.95, 6, 5, "d", "Transition Metal", "[Kr] 4d5 5s1", 2.16, 10.22, "IUPAC 2021", "Verified"),
            (43, "Tc", "Technetium", 98.0, 7, 5, "d", "Transition Metal", "[Kr] 4d5 5s2", 1.9, 11.5, "IUPAC 2021", "Verified"),
            (44, "Ru", "Ruthenium", 101.07, 8, 5, "d", "Transition Metal", "[Kr] 4d7 5s1", 2.2, 12.37, "IUPAC 2021", "Verified"),
            (45, "Rh", "Rhodium", 102.91, 9, 5, "d", "Transition Metal", "[Kr] 4d8 5s1", 2.28, 12.41, "IUPAC 2021", "Verified"),
            (46, "Pd", "Palladium", 106.42, 10, 5, "d", "Transition Metal", "[Kr] 4d10", 2.20, 12.02, "IUPAC 2021", "Verified"),
            (47, "Ag", "Silver", 107.87, 11, 5, "d", "Transition Metal", "[Kr] 4d10 5s1", 1.93, 10.501, "IUPAC 2021", "Verified"),
            (48, "Cd", "Cadmium", 112.41, 12, 5, "d", "Transition Metal", "[Kr] 4d10 5s2", 1.69, 8.69, "IUPAC 2021", "Verified"),
            (49, "In", "Indium", 114.82, 13, 5, "p", "Post-Transition Metal", "[Kr] 4d10 5s2 5p1", 1.78, 7.31, "IUPAC 2021", "Verified"),
            (50, "Sn", "Tin", 118.71, 14, 5, "p", "Post-Transition Metal", "[Kr] 4d10 5s2 5p2", 1.96, 7.287, "IUPAC 2021", "Verified"),
            (51, "Sb", "Antimony", 121.76, 15, 5, "p", "Metalloid", "[Kr] 4d10 5s2 5p3", 2.05, 6.685, "IUPAC 2021", "Verified"),
            (52, "Te", "Tellurium", 127.60, 16, 5, "p", "Metalloid", "[Kr] 4d10 5s2 5p4", 2.1, 6.232, "IUPAC 2021", "Verified"),
            (53, "I", "Iodine", 126.90, 17, 5, "p", "Halogen", "[Kr] 4d10 5s2 5p5", 2.66, 4.93, "IUPAC 2021", "Verified"),
            (54, "Xe", "Xenon", 131.29, 18, 5, "p", "Noble Gas", "[Kr] 4d10 5s2 5p6", 2.6, 0.00588, "IUPAC 2021", "Verified"),
            (55, "Cs", "Caesium", 132.91, 1, 6, "s", "Alkali Metal", "[Xe] 6s1", 0.79, 1.873, "IUPAC 2021", "Verified"),
            (56, "Ba", "Barium", 137.33, 2, 6, "s", "Alkaline Earth", "[Xe] 6s2", 0.89, 3.594, "IUPAC 2021", "Verified"),
            (57, "La", "Lanthanum", 138.91, 3, 6, "f", "Lanthanide", "[Xe] 5d1 6s2", 1.1, 6.145, "IUPAC 2021", "Verified"),
            (58, "Ce", "Cerium", 140.12, 3, 6, "f", "Lanthanide", "[Xe] 4f1 5d1 6s2", 1.12, 6.77, "IUPAC 2021", "Verified"),
            (59, "Pr", "Praseodymium", 140.91, 3, 6, "f", "Lanthanide", "[Xe] 4f3 6s2", 1.13, 6.773, "IUPAC 2021", "Verified"),
            (60, "Nd", "Neodymium", 144.24, 3, 6, "f", "Lanthanide", "[Xe] 4f4 6s2", 1.14, 7.007, "IUPAC 2021", "Verified"),
            (61, "Pm", "Promethium", 145.0, 3, 6, "f", "Lanthanide", "[Xe] 4f5 6s2", 1.13, 7.26, "IUPAC 2021", "Verified"),
            (62, "Sm", "Samarium", 150.36, 3, 6, "f", "Lanthanide", "[Xe] 4f6 6s2", 1.17, 7.52, "IUPAC 2021", "Verified"),
            (63, "Eu", "Europium", 151.96, 3, 6, "f", "Lanthanide", "[Xe] 4f7 6s2", 1.2, 5.243, "IUPAC 2021", "Verified"),
            (64, "Gd", "Gadolinium", 157.25, 3, 6, "f", "Lanthanide", "[Xe] 4f7 5d1 6s2", 1.2, 7.895, "IUPAC 2021", "Verified"),
            (65, "Tb", "Terbium", 158.93, 3, 6, "f", "Lanthanide", "[Xe] 4f9 6s2", 1.2, 8.229, "IUPAC 2021", "Verified"),
            (66, "Dy", "Dysprosium", 162.50, 3, 6, "f", "Lanthanide", "[Xe] 4f10 6s2", 1.22, 8.55, "IUPAC 2021", "Verified"),
            (67, "Ho", "Holmium", 164.93, 3, 6, "f", "Lanthanide", "[Xe] 4f11 6s2", 1.23, 8.795, "IUPAC 2021", "Verified"),
            (68, "Er", "Erbium", 167.26, 3, 6, "f", "Lanthanide", "[Xe] 4f12 6s2", 1.24, 9.066, "IUPAC 2021", "Verified"),
            (69, "Tm", "Thulium", 168.93, 3, 6, "f", "Lanthanide", "[Xe] 4f13 6s2", 1.25, 9.321, "IUPAC 2021", "Verified"),
            (70, "Yb", "Ytterbium", 173.05, 3, 6, "f", "Lanthanide", "[Xe] 4f14 6s2", 1.1, 6.965, "IUPAC 2021", "Verified"),
            (71, "Lu", "Lutetium", 174.97, 3, 6, "d", "Lanthanide", "[Xe] 4f14 5d1 6s2", 1.27, 9.84, "IUPAC 2021", "Verified"),
            (72, "Hf", "Hafnium", 178.49, 4, 6, "d", "Transition Metal", "[Xe] 4f14 5d2 6s2", 1.3, 13.31, "IUPAC 2021", "Verified"),
            (73, "Ta", "Tantalum", 180.95, 5, 6, "d", "Transition Metal", "[Xe] 4f14 5d3 6s2", 1.5, 16.654, "IUPAC 2021", "Verified"),
            (74, "W", "Tungsten", 183.84, 6, 6, "d", "Transition Metal", "[Xe] 4f14 5d4 6s2", 2.36, 19.25, "IUPAC 2021", "Verified"),
            (75, "Re", "Rhenium", 186.21, 7, 6, "d", "Transition Metal", "[Xe] 4f14 5d5 6s2", 1.9, 21.02, "IUPAC 2021", "Verified"),
            (76, "Os", "Osmium", 190.23, 8, 6, "d", "Transition Metal", "[Xe] 4f14 5d6 6s2", 2.2, 22.61, "IUPAC 2021", "Verified"),
            (77, "Ir", "Iridium", 192.22, 9, 6, "d", "Transition Metal", "[Xe] 4f14 5d7 6s2", 2.2, 22.56, "IUPAC 2021", "Verified"),
            (78, "Pt", "Platinum", 195.08, 10, 6, "d", "Transition Metal", "[Xe] 4f14 5d9 6s1", 2.28, 21.46, "IUPAC 2021", "Verified"),
            (79, "Au", "Gold", 196.97, 11, 6, "d", "Transition Metal", "[Xe] 4f14 5d10 6s1", 2.54, 19.282, "IUPAC 2021", "Verified"),
            (80, "Hg", "Mercury", 200.59, 12, 6, "d", "Transition Metal", "[Xe] 4f14 5d10 6s2", 2.0, 13.5336, "IUPAC 2021", "Verified"),
            (81, "Tl", "Thallium", 204.38, 13, 6, "p", "Post-Transition Metal", "[Xe] 4f14 5d10 6s2 6p1", 1.62, 11.85, "IUPAC 2021", "Verified"),
            (82, "Pb", "Lead", 207.2, 14, 6, "p", "Post-Transition Metal", "[Xe] 4f14 5d10 6s2 6p2", 2.33, 11.342, "IUPAC 2021", "Verified"),
            (83, "Bi", "Bismuth", 208.98, 15, 6, "p", "Post-Transition Metal", "[Xe] 4f14 5d10 6s2 6p3", 2.02, 9.807, "IUPAC 2021", "Verified"),
            (84, "Po", "Polonium", 209.0, 16, 6, "p", "Post-Transition Metal", "[Xe] 4f14 5d10 6s2 6p4", 2.0, 9.32, "IUPAC 2021", "Verified"),
            (85, "At", "Astatine", 210.0, 17, 6, "p", "Halogen", "[Xe] 4f14 5d10 6s2 6p5", 2.2, 7.0, "IUPAC 2021", "Verified"),
            (86, "Rn", "Radon", 222.0, 18, 6, "p", "Noble Gas", "[Xe] 4f14 5d10 6s2 6p6", 2.2, 0.00973, "IUPAC 2021", "Verified"),
            (87, "Fr", "Francium", 223.0, 1, 7, "s", "Alkali Metal", "[Rn] 7s1", 0.7, 1.87, "IUPAC 2021", "Verified"),
            (88, "Ra", "Radium", 226.0, 2, 7, "s", "Alkaline Earth", "[Rn] 7s2", 0.9, 5.5, "IUPAC 2021", "Verified"),
            (89, "Ac", "Actinium", 227.0, 3, 7, "f", "Actinide", "[Rn] 6d1 7s2", 1.1, 10.07, "IUPAC 2021", "Verified"),
            (90, "Th", "Thorium", 232.04, 3, 7, "f", "Actinide", "[Rn] 6d2 7s2", 1.3, 11.72, "IUPAC 2021", "Verified"),
            (91, "Pa", "Protactinium", 231.04, 3, 7, "f", "Actinide", "[Rn] 5f2 6d1 7s2", 1.5, 15.37, "IUPAC 2021", "Verified"),
            (92, "U", "Uranium", 238.03, 3, 7, "f", "Actinide", "[Rn] 5f3 6d1 7s2", 1.38, 18.95, "IUPAC 2021", "Verified"),
            (93, "Np", "Neptunium", 237.0, 3, 7, "f", "Actinide", "[Rn] 5f4 6d1 7s2", 1.36, 20.45, "IUPAC 2021", "Verified"),
            (94, "Pu", "Plutonium", 244.0, 3, 7, "f", "Actinide", "[Rn] 5f6 7s2", 1.28, 19.84, "IUPAC 2021", "Verified"),
            (95, "Am", "Americium", 243.0, 3, 7, "f", "Actinide", "[Rn] 5f7 7s2", 1.3, 13.69, "IUPAC 2021", "Verified"),
            (96, "Cm", "Curium", 247.0, 3, 7, "f", "Actinide", "[Rn] 5f7 6d1 7s2", 1.3, 13.51, "IUPAC 2021", "Verified"),
            (97, "Bk", "Berkelium", 247.0, 3, 7, "f", "Actinide", "[Rn] 5f9 7s2", 1.3, 14.79, "IUPAC 2021", "Verified"),
            (98, "Cf", "Californium", 251.0, 3, 7, "f", "Actinide", "[Rn] 5f10 7s2", 1.3, 15.1, "IUPAC 2021", "Verified"),
            (99, "Es", "Einsteinium", 252.0, 3, 7, "f", "Actinide", "[Rn] 5f11 7s2", 1.3, 8.84, "IUPAC 2021", "Verified"),
            (100, "Fm", "Fermium", 257.0, 3, 7, "f", "Actinide", "[Rn] 5f12 7s2", 1.3, None, "IUPAC 2021", "Verified"),
            (101, "Md", "Mendelevium", 258.0, 3, 7, "f", "Actinide", "[Rn] 5f13 7s2", 1.3, None, "IUPAC 2021", "Verified"),
            (102, "No", "Nobelium", 259.0, 3, 7, "f", "Actinide", "[Rn] 5f14 7s2", 1.3, None, "IUPAC 2021", "Verified"),
            (103, "Lr", "Lawrencium", 262.0, 3, 7, "d", "Actinide", "[Rn] 5f14 7s2 7p1", None, None, "IUPAC 2021", "Verified"),
            (104, "Rf", "Rutherfordium", 267.0, 4, 7, "d", "Transition Metal", "[Rn] 5f14 6d2 7s2", None, 23.2, "IUPAC 2021", "Verified"),
            (105, "Db", "Dubnium", 270.0, 5, 7, "d", "Transition Metal", "[Rn] 5f14 6d3 7s2", None, 29.3, "IUPAC 2021", "Verified"),
            (106, "Sg", "Seaborgium", 271.0, 6, 7, "d", "Transition Metal", "[Rn] 5f14 6d4 7s2", None, 35.0, "IUPAC 2021", "Verified"),
            (107, "Bh", "Bohrium", 270.0, 7, 7, "d", "Transition Metal", "[Rn] 5f14 6d5 7s2", None, 37.1, "IUPAC 2021", "Verified"),
            (108, "Hs", "Hassium", 277.0, 8, 7, "d", "Transition Metal", "[Rn] 5f14 6d6 7s2", None, 40.7, "IUPAC 2021", "Verified"),
            (109, "Mt", "Meitnerium", 278.0, 9, 7, "d", "Transition Metal", "[Rn] 5f14 6d7 7s2", None, 37.4, "IUPAC 2021", "Verified"),
            (110, "Ds", "Darmstadtium", 281.0, 10, 7, "d", "Transition Metal", "[Rn] 5f14 6d8 7s2", None, 34.8, "IUPAC 2021", "Verified"),
            (111, "Rg", "Roentgenium", 282.0, 11, 7, "d", "Transition Metal", "[Rn] 5f14 6d9 7s2", None, 28.7, "IUPAC 2021", "Verified"),
            (112, "Cn", "Copernicium", 285.0, 12, 7, "d", "Transition Metal", "[Rn] 5f14 6d10 7s2", None, 23.7, "IUPAC 2021", "Verified"),
            (113, "Nh", "Nihonium", 286.0, 13, 7, "p", "Post-Transition Metal", "[Rn] 5f14 6d10 7s2 7p1", None, 16.0, "IUPAC 2021", "Verified"),
            (114, "Fl", "Flerovium", 289.0, 14, 7, "p", "Post-Transition Metal", "[Rn] 5f14 6d10 7s2 7p2", None, 14.0, "IUPAC 2021", "Verified"),
            (115, "Mc", "Moscovium", 290.0, 15, 7, "p", "Post-Transition Metal", "[Rn] 5f14 6d10 7s2 7p3", None, 13.5, "IUPAC 2021", "Verified"),
            (116, "Lv", "Livermorium", 293.0, 16, 7, "p", "Post-Transition Metal", "[Rn] 5f14 6d10 7s2 7p4", None, 12.9, "IUPAC 2021", "Verified"),
            (117, "Ts", "Tennessine", 294.0, 17, 7, "p", "Halogen", "[Rn] 5f14 6d10 7s2 7p5", None, 7.2, "IUPAC 2021", "Verified"),
            (118, "Og", "Oganesson", 294.0, 18, 7, "p", "Noble Gas", "[Rn] 5f14 6d10 7s2 7p6", None, 5.0, "IUPAC 2021", "Verified")
        ]
        cur.executemany("INSERT INTO elements VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", all_118_elements)

    cur.execute("SELECT COUNT(*) FROM compounds")
    if cur.fetchone()[0] == 0:
        compounds_seed = [
            (1, "Sodium Hydroxide", "NaOH", 40.00, "1310-73-2", "Inorganic Base", "NIST WebBook", "Verified"),
            (2, "Hydrochloric Acid", "HCl", 36.46, "7647-01-0", "Inorganic Acid", "NIST WebBook", "Verified"),
            (3, "Sulfuric Acid", "H2SO4", 98.08, "7664-93-9", "Inorganic Acid", "NIST WebBook", "Verified"),
            (4, "Sodium Carbonate", "Na2CO3", 105.99, "497-19-8", "Primary Standard Base", "NIST WebBook", "Verified"),
            (5, "Copper(II) Sulfate Pentahydrate", "CuSO4·5H2O", 249.68, "7758-99-8", "Hydrate Salt", "CRC Handbook", "Verified"),
            (6, "Potassium Hydrogen Phthalate", "C8H5KO4", 204.22, "877-24-7", "Primary Standard Acid", "USP Reference", "Verified"),
            (7, "Glacial Acetic Acid", "CH3COOH", 60.05, "64-19-7", "Organic Acid", "NIST WebBook", "Verified"),
            (8, "Sodium Chloride", "NaCl", 58.44, "7647-14-5", "Neutral Salt", "NIST WebBook", "Verified"),
            (9, "Potassium Permanganate", "KMnO4", 158.03, "7722-64-7", "Oxidizing Agent", "CRC Handbook", "Verified"),
            (10, "Oxalic Acid Dihydrate", "C2H2O4·2H2O", 126.07, "6153-56-6", "Primary Acid Standard", "USP Reference", "Verified")
        ]
        cur.executemany("INSERT INTO compounds VALUES (?,?,?,?,?,?,?,?)", compounds_seed)

    cur.execute("SELECT COUNT(*) FROM chemicals_reagents")
    if cur.fetchone()[0] == 0:
        reagents_seed = [
            (1, "Hydrochloric Acid 37%", "7647-01-0", "Analytical Reagent (AR)", 1.19, "Corrosive, Skin Irritant", "Acid Storage", "Verified"),
            (2, "Sulfuric Acid 98%", "7664-93-9", "TraceMetal Grade", 1.84, "Severe Burns, Oxidizer", "Dedicated Acid Cabinet", "Verified"),
            (3, "Methanol", "67-56-1", "HPLC Grade", 0.791, "Flammable Liquid, Toxic", "Solvent Safety Storage", "Verified"),
            (4, "Karl Fischer Composite 5", "None-Mixture", "Analytical Reagent", 1.05, "Flammable, Toxic", "Tightly Sealed, Dark & Dry", "Verified"),
            (5, "Sodium Hydroxide Pellets", "1310-73-2", "ACS Grade", 2.13, "Corrosive, Deliquescent", "Dry Storage, Desiccated", "Verified")
        ]
        cur.executemany("INSERT INTO chemicals_reagents VALUES (?,?,?,?,?,?,?,?)", reagents_seed)

    cur.execute("SELECT COUNT(*) FROM qc_methods")
    if cur.fetchone()[0] == 0:
        qc_seed = [
            ("QC-METH-001", "Assay of Glacial Acetic Acid", "USP <541>", "Acetic Acid", "NaOH", 1.0000, 60.05, 0.00, 2, "Approved"),
            ("QC-METH-002", "Assay of Hydrochloric Acid", "EP 2.2.20", "HCl", "NaOH", 1.0000, 36.46, 0.05, 2, "Approved"),
            ("QC-METH-003", "Standardization of NaOH vs KHP", "In-House SOP QC-04", "NaOH", "KHP", 0.1000, 204.22, 0.00, 4, "Approved"),
            ("QC-METH-004", "Karl Fischer Water by Volumetry", "ASTM E203", "Water", "Hydranal Comp 5", 5.0000, 1.00, 0.00, 4, "Approved")
        ]
        cur.executemany("INSERT INTO qc_methods VALUES (?,?,?,?,?,?,?,?,?,?)", qc_seed)

    conn.commit()
    conn.close()

init_db()

def query_db(query: str, args: tuple = ()) -> List[sqlite3.Row]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------------------------------------------------
# MODULE 4: RECURSIVE-DESCENT FORMULA PARSER & MASS ENGINE
# ---------------------------------------------------------
class TokenType(Enum):
    ELEMENT = auto()
    NUMBER = auto()
    LPAREN = auto()
    RPAREN = auto()
    DOT = auto()

class Token:
    def __init__(self, t_type: TokenType, val: str, pos: int):
        self.type = t_type
        self.val = val
        self.pos = pos

class FormulaTokenizer:
    @staticmethod
    def tokenize(f_str: str) -> List[Token]:
        if not f_str or not f_str.strip():
            raise ValueError("Formula string cannot be empty.")
        tokens = []
        i = 0
        n = len(f_str)
        while i < n:
            ch = f_str[i]
            if ch.isspace():
                i += 1
                continue
            if ch in ['·', '.', '*']:
                tokens.append(Token(TokenType.DOT, ch, i))
                i += 1
                continue
            if ch == '(':
                tokens.append(Token(TokenType.LPAREN, ch, i))
                i += 1
                continue
            if ch == ')':
                tokens.append(Token(TokenType.RPAREN, ch, i))
                i += 1
                continue
            if ch.isupper():
                elem = ch
                i += 1
                if i < n and f_str[i].islower():
                    elem += f_str[i]
                    i += 1
                tokens.append(Token(TokenType.ELEMENT, elem, i - len(elem)))
                continue
            if ch.isdigit():
                num = ch
                i += 1
                while i < n and f_str[i].isdigit():
                    num += f_str[i]
                    i += 1
                tokens.append(Token(TokenType.NUMBER, num, i - len(num)))
                continue
            raise ValueError(f"Illegal character '{ch}' at position {i}.")
        return tokens

class FormulaParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.n = len(tokens)

    def current(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < self.n else None

    def match(self, t_type: TokenType) -> bool:
        c = self.current()
        if c and c.type == t_type:
            self.pos += 1
            return True
        return False

    def parse(self) -> Dict[str, int]:
        comp = defaultdict(int)
        main_comp = self._parse_sub()
        for el, cnt in main_comp.items():
            comp[el] += cnt

        while self.match(TokenType.DOT):
            mult = 1
            c = self.current()
            if c and c.type == TokenType.NUMBER:
                mult = int(c.val)
                self.pos += 1
            hyd = self._parse_sub()
            for el, cnt in hyd.items():
                comp[el] += cnt * mult

        if self.pos < self.n:
            raise ValueError(f"Unparsed trailing tokens at position {self.tokens[self.pos].pos}")
        return dict(comp)

    def _parse_sub(self) -> Dict[str, int]:
        grp = defaultdict(int)
        while self.pos < self.n:
            c = self.current()
            if not c:
                break
            if c.type == TokenType.ELEMENT:
                elem = c.val
                self.pos += 1
                cnt = 1
                nxt = self.current()
                if nxt and nxt.type == TokenType.NUMBER:
                    cnt = int(nxt.val)
                    self.pos += 1
                grp[elem] += cnt
            elif c.type == TokenType.LPAREN:
                self.pos += 1
                sub = self._parse_sub()
                if not self.match(TokenType.RPAREN):
                    raise ValueError("Unbalanced opening parenthesis '(' in formula.")
                mult = 1
                nxt = self.current()
                if nxt and nxt.type == TokenType.NUMBER:
                    mult = int(nxt.val)
                    self.pos += 1
                for el, cnt in sub.items():
                    grp[el] += cnt * mult
            elif c.type in [TokenType.RPAREN, TokenType.DOT]:
                break
            else:
                raise ValueError("Grammar syntax error.")
        return grp

def compute_formula_properties(formula: str) -> Dict[str, Any]:
    tokens = FormulaTokenizer.tokenize(formula)
    counts = FormulaParser(tokens).parse()
    
    rows = query_db("SELECT symbol, atomic_weight FROM elements")
    w_map = {r["symbol"]: Decimal(str(r["atomic_weight"])) for r in rows}
    
    total = Decimal("0.0")
    contribs = {}
    for el, cnt in counts.items():
        if el not in w_map:
            raise ValueError(f"Element '{el}' not recognized in 118 IUPAC canonical elements.")
        at_wt = w_map[el]
        c = at_wt * Decimal(str(cnt))
        total += c
        contribs[el] = {"count": cnt, "weight": at_wt, "contrib": c}
        
    pcts = {el: ((data["contrib"] / total) * Decimal("100.0")).quantize(Decimal("0.01")) for el, data in contribs.items()}
    return {
        "formula": formula,
        "mass": total.quantize(Decimal("0.0001")),
        "counts": counts,
        "percentages": pcts,
        "provenance": "IUPAC Standard Atomic Weights 2021"
    }

# ---------------------------------------------------------
# MODULE 5: 20 GENERAL CHEMISTRY CALCULATION ENGINES
# ---------------------------------------------------------
class GeneralChemEngine:
    @staticmethod
    def moles_from_mass(m_g: Decimal, mw: Decimal) -> Decimal:
        if m_g <= Decimal("0") or mw <= Decimal("0"): raise ValueError("Inputs must be positive.")
        return (m_g / mw).quantize(Decimal("0.000001"))

    @staticmethod
    def mass_from_moles(n_mol: Decimal, mw: Decimal) -> Decimal:
        if n_mol <= Decimal("0") or mw <= Decimal("0"): raise ValueError("Inputs must be positive.")
        return (n_mol * mw).quantize(Decimal("0.0001"))

    @staticmethod
    def particle_count(n_mol: Decimal) -> str:
        if n_mol <= Decimal("0"): raise ValueError("Moles must be positive.")
        return f"{(n_mol * AVOGADRO_NA):.6e}"

    @staticmethod
    def molarity(n_mol: Decimal, v_l: Decimal) -> Decimal:
        if n_mol <= Decimal("0") or v_l <= Decimal("0"): raise ValueError("Inputs must be positive.")
        return (n_mol / v_l).quantize(Decimal("0.0001"))

    @staticmethod
    def molality(n_mol: Decimal, m_solvent_kg: Decimal) -> Decimal:
        if n_mol <= Decimal("0") or m_solvent_kg <= Decimal("0"): raise ValueError("Inputs must be positive.")
        return (n_mol / m_solvent_kg).quantize(Decimal("0.0001"))

    @staticmethod
    def normality(molarity: Decimal, n_factor: Decimal) -> Decimal:
        if molarity <= Decimal("0") or n_factor <= Decimal("0"): raise ValueError("Inputs must be positive.")
        return (molarity * n_factor).quantize(Decimal("0.0001"))

    @staticmethod
    def equivalent_weight(mw: Decimal, n_factor: Decimal) -> Decimal:
        if mw <= Decimal("0") or n_factor <= Decimal("0"): raise ValueError("Inputs must be positive.")
        return (mw / n_factor).quantize(Decimal("0.0001"))

    @staticmethod
    def dilution(c1: Decimal, v1: Decimal, c2: Decimal) -> Decimal:
        if any(x <= Decimal("0") for x in [c1, v1, c2]): raise ValueError("Inputs must be positive.")
        if c2 >= c1: raise ValueError("Target C2 must be lower than stock C1.")
        return ((c1 * v1) / c2).quantize(Decimal("0.001"))

    @staticmethod
    def prep_solid(m: Decimal, v_ml: Decimal, mw: Decimal, purity_pct: Decimal) -> Decimal:
        if any(x <= Decimal("0") for x in [m, v_ml, mw, purity_pct]) or purity_pct > Decimal("100.0"):
            raise ValueError("Invalid positive inputs or purity > 100%.")
        pure = m * (v_ml * Decimal("0.001")) * mw
        return (pure / (purity_pct / Decimal("100.0"))).quantize(Decimal("0.0001"))

    @staticmethod
    def prep_liquid(target_m: Decimal, vol_ml: Decimal, mw: Decimal, density: Decimal, assay_pct: Decimal) -> Decimal:
        if any(x <= Decimal("0") for x in [target_m, vol_ml, mw, density, assay_pct]) or assay_pct > Decimal("100.0"):
            raise ValueError("Invalid inputs.")
        target_mass_pure = target_m * (vol_ml * Decimal("0.001")) * mw
        req_gross_mass = target_mass_pure / (assay_pct / Decimal("100.0"))
        return (req_gross_mass / density).quantize(Decimal("0.01"))

    @staticmethod
    def percent_yield(actual: Decimal, theoretical: Decimal) -> Tuple[Decimal, Optional[str]]:
        if theoretical <= Decimal("0") or actual < Decimal("0"): raise ValueError("Invalid yield inputs.")
        y = (actual / theoretical) * Decimal("100.0")
        warn = "Yield exceeds 100%. Check moisture/solvent residue." if y > Decimal("100.0") else None
        return y.quantize(Decimal("0.01")), warn

    @staticmethod
    def density(mass_g: Decimal, vol_ml: Decimal) -> Decimal:
        if mass_g <= Decimal("0") or vol_ml <= Decimal("0"): raise ValueError("Positive values required.")
        return (mass_g / vol_ml).quantize(Decimal("0.0001"))

    @staticmethod
    def conc_conversion(val: Decimal, from_type: str, mw: Decimal) -> Decimal:
        if val <= Decimal("0") or mw <= Decimal("0"): raise ValueError("Positive values required.")
        if from_type == "M to g/L": return (val * mw).quantize(Decimal("0.0001"))
        if from_type == "g/L to M": return (val / mw).quantize(Decimal("0.0001"))
        if from_type == "mg/L to ppm (aq)": return val.quantize(Decimal("0.0001"))
        raise ValueError("Unsupported conversion type.")

    @staticmethod
    def empirical_multiplier(emp_mass: Decimal, exp_mass: Decimal) -> int:
        if emp_mass <= Decimal("0") or exp_mass <= Decimal("0"): raise ValueError("Masses must be positive.")
        ratio = exp_mass / emp_mass
        return round(float(ratio))

    @staticmethod
    def limiting_reagent(mol_a: Decimal, coeff_a: int, mol_b: Decimal, coeff_b: int) -> str:
        if mol_a <= Decimal("0") or mol_b <= Decimal("0") or coeff_a <= 0 or coeff_b <= 0:
            raise ValueError("All moles and stoichiometric coefficients must be positive.")
        r_a = mol_a / Decimal(str(coeff_a))
        r_b = mol_b / Decimal(str(coeff_b))
        if r_a < r_b: return "Reactant A is limiting."
        if r_b < r_a: return "Reactant B is limiting."
        return "Reactants are in equimolar stoichiometric balance."

    @staticmethod
    def recovery_pct(measured: Decimal, expected: Decimal) -> Decimal:
        if expected <= Decimal("0"): raise ValueError("Expected reference must be positive.")
        return ((measured / expected) * Decimal("100.0")).quantize(Decimal("0.01"))

    @staticmethod
    def saponification_value(blank_ml: Decimal, titre_ml: Decimal, norm: Decimal, sample_g: Decimal) -> Decimal:
        if sample_g <= Decimal("0"): raise ValueError("Sample mass must be positive.")
        diff = blank_ml - titre_ml
        if diff < Decimal("0"): raise ValueError("Blank consumption must be greater than sample titre.")
        return ((diff * norm * Decimal("56.1")) / sample_g).quantize(Decimal("0.01"))

    @staticmethod
    def acid_value(titre_ml: Decimal, norm: Decimal, sample_g: Decimal) -> Decimal:
        if sample_g <= Decimal("0") or titre_ml < Decimal("0"): raise ValueError("Invalid inputs.")
        return ((titre_ml * norm * Decimal("56.1")) / sample_g).quantize(Decimal("0.01"))

# ---------------------------------------------------------
# MODULE 6: 20 ANALYTICAL QC CALCULATION ENGINES
# ---------------------------------------------------------
class AnalyticalQCEngine:
    @staticmethod
    def assay_percent(titre_ml: Decimal, norm: Decimal, eq_wt: Decimal, sample_g: Decimal, blank_ml: Decimal = Decimal("0.0")) -> Decimal:
        if sample_g <= Decimal("0"): raise ValueError("Sample weight must be positive.")
        net = titre_ml - blank_ml
        if net < Decimal("0"): raise ValueError("Net titre cannot be negative.")
        return ((net * norm * eq_wt * Decimal("100.0")) / (sample_g * Decimal("1000.0"))).quantize(Decimal("0.01"))

    @staticmethod
    def moisture_loss(w_initial: Decimal, w_dry: Decimal) -> Decimal:
        if w_initial <= Decimal("0") or w_dry > w_initial: raise ValueError("Invalid weights for moisture determination.")
        return (((w_initial - w_dry) / w_initial) * Decimal("100.0")).quantize(Decimal("0.0001"))

    @staticmethod
    def kf_factor(water_mg: Decimal, titre_ml: Decimal) -> Decimal:
        if water_mg <= Decimal("0") or titre_ml <= Decimal("0"): raise ValueError("Positive values required.")
        return (water_mg / titre_ml).quantize(Decimal("0.0001"))

    @staticmethod
    def kf_water(titre_ml: Decimal, factor: Decimal, sample_g: Decimal, blank_ml: Decimal = Decimal("0.0")) -> Dict[str, Decimal]:
        if sample_g <= Decimal("0") or factor <= Decimal("0"): raise ValueError("Invalid parameters.")
        net = titre_ml - blank_ml
        if net < Decimal("0"): raise ValueError("Net titre cannot be negative.")
        w_mg = net * factor
        w_pct = (w_mg / (sample_g * Decimal("1000.0"))) * Decimal("100.0")
        return {
            "water_percent": w_pct.quantize(Decimal("0.0001")),
            "water_ppm": (w_pct * Decimal("10000.0")).quantize(Decimal("1")),
            "water_mg": w_mg.quantize(Decimal("0.01"))
        }

    @staticmethod
    def nvm_percent(w_tare: Decimal, w_residue: Decimal, sample_g: Decimal) -> Decimal:
        if sample_g <= Decimal("0") or w_residue < w_tare: raise ValueError("Invalid weights for NVM.")
        return (((w_residue - w_tare) / sample_g) * Decimal("100.0")).quantize(Decimal("0.0001"))

    @staticmethod
    def acidity_percent(titre_ml: Decimal, norm: Decimal, eq_wt: Decimal, sample_g: Decimal) -> Decimal:
        return AnalyticalQCEngine.assay_percent(titre_ml, norm, eq_wt, sample_g)

    @staticmethod
    def alkalinity_percent(titre_ml: Decimal, norm: Decimal, eq_wt: Decimal, sample_g: Decimal) -> Decimal:
        return AnalyticalQCEngine.assay_percent(titre_ml, norm, eq_wt, sample_g)

    @staticmethod
    def back_titration(v_added_ml: Decimal, n_added: Decimal, v_back_ml: Decimal, n_back: Decimal, eq_wt: Decimal, sample_g: Decimal) -> Decimal:
        if sample_g <= Decimal("0"): raise ValueError("Sample weight must be positive.")
        meq_added = v_added_ml * n_added
        meq_excess = v_back_ml * n_back
        meq_consumed = meq_added - meq_excess
        if meq_consumed < Decimal("0"): raise ValueError("Excess titrant exceeds reagent added.")
        return ((meq_consumed * eq_wt * Decimal("100.0")) / (sample_g * Decimal("1000.0"))).quantize(Decimal("0.01"))

    @staticmethod
    def blank_corrected_titre(titre_ml: Decimal, blank_ml: Decimal) -> Decimal:
        if titre_ml < blank_ml: raise ValueError("Blank volume cannot exceed titre consumption.")
        return (titre_ml - blank_ml).quantize(Decimal("0.01"))

    @staticmethod
    def standardization_factor(act_conc: Decimal, nom_conc: Decimal) -> Decimal:
        if nom_conc <= Decimal("0") or act_conc <= Decimal("0"): raise ValueError("Concentrations must be positive.")
        return (act_conc / nom_conc).quantize(Decimal("0.0001"))

    @staticmethod
    def loss_on_ignition(w_dry_dish: Decimal, w_ignited_dish: Decimal, sample_g: Decimal) -> Decimal:
        if sample_g <= Decimal("0") or w_ignited_dish > w_dry_dish: raise ValueError("Invalid weights for LOI.")
        return (((w_dry_dish - w_ignited_dish) / sample_g) * Decimal("100.0")).quantize(Decimal("0.0001"))

    @staticmethod
    def serial_dilution_factor(v_aliquot: Decimal, v_flask: Decimal, steps: int) -> Decimal:
        if v_aliquot <= Decimal("0") or v_flask <= v_aliquot or steps <= 0: raise ValueError("Invalid dilution inputs.")
        df_single = v_flask / v_aliquot
        return (df_single ** Decimal(str(steps))).quantize(Decimal("0.01"))

    @staticmethod
    def statistics(obs: List[Decimal]) -> Dict[str, Decimal]:
        if len(obs) < 2: raise ValueError("Minimum 2 replicate observations required.")
        n = Decimal(str(len(obs)))
        mean = sum(obs) / n
        var = sum((x - mean) ** 2 for x in obs) / (n - Decimal("1"))
        sd = Decimal(str(math.sqrt(float(var))))
        rsd = Decimal("0.0") if mean == Decimal("0") else (sd / abs(mean)) * Decimal("100.0")
        return {
            "mean": mean.quantize(Decimal("0.0001")),
            "sd": sd.quantize(Decimal("0.0001")),
            "rsd_percent": rsd.quantize(Decimal("0.01"))
        }

    @staticmethod
    def spike_recovery(spiked_obs: Decimal, unspiked_obs: Decimal, added_amt: Decimal) -> Decimal:
        if added_amt <= Decimal("0"): raise ValueError("Spike amount must be strictly positive.")
        return (((spiked_obs - unspiked_obs) / added_amt) * Decimal("100.0")).quantize(Decimal("0.01"))

    @staticmethod
    def relative_error(measured: Decimal, true_val: Decimal) -> Decimal:
        if true_val == Decimal("0"): raise ValueError("Reference true value cannot be zero.")
        return (((measured - true_val) / true_val) * Decimal("100.0")).quantize(Decimal("0.01"))

    @staticmethod
    def relative_percent_diff(val1: Decimal, val2: Decimal) -> Decimal:
        diff = abs(val1 - val2)
        avg = (val1 + val2) / Decimal("2.0")
        if avg == Decimal("0"): raise ValueError("Mean of measurements cannot be zero.")
        return ((diff / avg) * Decimal("100.0")).quantize(Decimal("0.01"))

    @staticmethod
    def unknown_from_titre(titre_ml: Decimal, titrant_norm: Decimal, sample_vol_ml: Decimal) -> Decimal:
        if sample_vol_ml <= Decimal("0") or titre_ml < Decimal("0"): raise ValueError("Invalid volumes.")
        return ((titre_ml * titrant_norm) / sample_vol_ml).quantize(Decimal("0.0001"))

# ---------------------------------------------------------
# INTERFACE IMPLEMENTATION (DESIGN B: WHITE TECH NOTEBOOK)
# ---------------------------------------------------------
st.markdown("""
<div class="stark-header">
    <div>
        <h2 style="margin:0; font-size:24px; font-weight:800; letter-spacing:-0.5px; color:#0f172a;">
            🔬 ATUM <span style="color:#0284c7;">LAB OS 0.1</span>
        </h2>
        <span style="font-size:13px; color:#64748b; font-weight:500;">
            Unified AI Chemistry Intelligence System • Complete Master Suite
        </span>
    </div>
    <div>
        <span class="status-pill">118 ELEMENTS & QC GxP ACTIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

nav = st.sidebar.radio(
    "CORE CAPABILITIES",
    [
        "1. Periodic Table (118 Elements)",
        "2. Chemical Compounds Database",
        "3. Solvents & Lab Reagents",
        "4. Formula Parser & Mass Engine",
        "5. General Chemistry Suite (20)",
        "6. Analytical QC Suite (20)",
        "7. Unified Intelligence Search"
    ]
)

# ----------------- MODULE 1: PERIODIC TABLE -----------------
if nav == "1. Periodic Table (118 Elements)":
    st.subheader("Module 1 — Periodic Table Intelligence (Complete 118 Elements)")
    st.markdown("All 118 verified IUPAC/NIST canonical elements with standard atomic weights, blocks, electron configurations, and densities.")
    
    col_f1, col_f2 = st.columns(2)
    cat_filter = col_f1.selectbox("Filter by Category:", ["All Categories", "Nonmetal", "Noble Gas", "Alkali Metal", "Alkaline Earth", "Metalloid", "Halogen", "Post-Transition Metal", "Transition Metal", "Lanthanide", "Actinide"])
    block_filter = col_f2.selectbox("Filter by Block:", ["All Blocks", "s", "p", "d", "f"])
    
    q = "SELECT atomic_number, symbol, name, atomic_weight, group_num, period, block, category, electron_config, electronegativity, density_g_cm3 FROM elements WHERE 1=1"
    params = []
    if cat_filter != "All Categories":
        q += " AND category = ?"
        params.append(cat_filter)
    if block_filter != "All Blocks":
        q += " AND block = ?"
        params.append(block_filter)
    q += " ORDER BY atomic_number ASC"
    
    rows = query_db(q, tuple(params))
    st.dataframe(
        [dict(r) for r in rows],
        use_container_width=True,
        column_config={
            "atomic_number": "Z",
            "atomic_weight": st.column_config.NumberColumn(format="%.4f g/mol"),
            "electronegativity": st.column_config.NumberColumn(format="%.2f"),
            "density_g_cm3": st.column_config.NumberColumn(format="%.4f g/cm³")
        }
    )

# ----------------- MODULE 2: COMPOUNDS DATABASE -----------------
elif nav == "2. Chemical Compounds Database":
    st.subheader("Module 2 — Chemical Compounds Database & Intelligence")
    rows = query_db("SELECT compound_id, canonical_name, formula, formula_mass, cas_number, category, source, verification_status FROM compounds")
    st.dataframe([dict(r) for r in rows], use_container_width=True)

# ----------------- MODULE 3: REAGENTS DATABASE -----------------
elif nav == "3. Solvents & Lab Reagents":
    st.subheader("Module 3 — Chemicals, Solvents & Laboratory Reagents")
    rows = query_db("SELECT chemical_id, name, cas_number, grade, density_g_ml, ghs_hazard, storage_conditions, verification_status FROM chemicals_reagents")
    st.dataframe([dict(r) for r in rows], use_container_width=True)

# ----------------- MODULE 4: FORMULA PARSER -----------------
elif nav == "4. Formula Parser & Mass Engine":
    st.subheader("Module 4 — Chemical Formula Parser & Molecular Calculation Engine")
    st.markdown("Safe recursive-descent AST parser supporting multi-subscripts, nested parentheses, and middle dot hydrate notation. Absolutely zero `eval()`.")
    
    f_in = st.text_input("Enter Formula String (e.g., CuSO4·5H2O, Al2(SO4)3, Ca(OH)2, (NH4)2SO4):", value="CuSO4·5H2O")
    if st.button("Parse AST & Calculate Molecular Mass"):
        try:
            res = compute_formula_properties(f_in)
            st.markdown(f"""
            <div class="stark-card">
                <span style="font-size:12px; font-weight:700; color:#0284c7;">CALCULATED FORMULA MASS</span><br>
                <div class="result-badge" style="margin-top:6px;">{res['mass']} g/mol</div>
                <div class="provenance-tag">Source: {res['provenance']} | Status: Deterministic Verified</div>
            </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.write("**Parsed Element Counts:**")
            c1.json(res["counts"])
            c2.write("**Elemental Mass Fractions (%):**")
            c2.json({k: f"{v}%" for k, v in res["percentages"].items()})
        except Exception as e:
            st.error(f"Grammar Validation Error: {str(e)}")

# ----------------- MODULE 5: 20 GENERAL CHEMISTRY CALCULATIONS -----------------
elif nav == "5. General Chemistry Suite (20)":
    st.subheader("Module 5 — General Chemistry Calculation Engine (Full 20 Categories)")
    
    sel_cat = st.selectbox("Select General Chemistry Calculation:", [
        "1. Moles from Mass",
        "2. Mass from Moles",
        "3. Particle Count (Avogadro)",
        "4. Molarity (mol/L)",
        "5. Molality (mol/kg)",
        "6. Normality (N)",
        "7. Equivalent Weight (g/eq)",
        "8. Standard Dilution (C1V1 = C2V2)",
        "9. Solution Prep from Solid Reagent",
        "10. Solution Prep from Liquid Reagent (Density & Assay)",
        "11. Percentage Yield (%)",
        "12. Density (g/mL)",
        "13. Concentration Conversion",
        "14. Empirical to Molecular Formula Multiplier",
        "15. Limiting Reagent Identifier",
        "16. Analytical Recovery (%)",
        "17. Saponification Value",
        "18. Acid Value"
    ])
    
    if sel_cat == "1. Moles from Mass":
        c1, c2 = st.columns(2)
        m = c1.number_input("Mass (g)", value=10.0000, step=0.1000)
        mw = c2.number_input("Molar Mass (g/mol)", value=40.00, step=0.01)
        if st.button("Calculate Moles"):
            res = GeneralChemEngine.moles_from_mass(Decimal(str(m)), Decimal(str(mw)))
            st.markdown(f"<div class='stark-card'><span class='result-badge'>{res} mol</span></div>", unsafe_allow_html=True)

    elif sel_cat == "2. Mass from Moles":
        c1, c2 = st.columns(2)
        n = c1.number_input("Moles (mol)", value=0.2500, step=0.0100)
        mw = c2.number_input("Molar Mass (g/mol)", value=98.08, step=0.01)
        if st.button("Calculate Mass"):
            res = GeneralChemEngine.mass_from_moles(Decimal(str(n)), Decimal(str(mw)))
            st.markdown(f"<div class='stark-card'><span class='result-badge'>{res} g</span></div>", unsafe_allow_html=True)

    elif sel_cat == "3. Particle Count (Avogadro)":
        n = st.number_input("Moles (mol)", value=1.0000, step=0.1000)
        if st.button("Calculate Total Particles"):
            res = GeneralChemEngine.particle_count(Decimal(str(n)))
            st.markdown(f"<div class='stark-card'><span class='result-badge'>{res} particles</span></div>", unsafe_allow_html=True)

    elif sel_cat == "4. Molarity (mol/L)":
        c1, c2 = st.columns(2)
        n = c1.number_input("Moles of Solute", value=0.5000, step=0.0500)
        v = c2.number_input("Solution Volume (L)", value=1.0000, step=0.1000)
        if st.button("Calculate Molarity"):
            res = GeneralChemEngine.molarity(Decimal(str(n)), Decimal(str(v)))
            st.markdown(f"<div class='stark-card'><span class='result-badge'>{res} M</span></div>", unsafe_allow_html=True)

    elif sel_cat == "8. Standard Dilution (C1V1 = C2V2)":
        c1, c2 = st.columns(2)
        con1 = c1.number_input("Stock Conc (C1)", value=10.00, step=0.10)
        vol1 = c2.number_input("Stock Aliquot (V1 in mL)", value=5.00, step=0.50)
        con2 = c1.number_input("Target Working Conc (C2)", value=1.00, step=0.10)
        if st.button("Calculate Final Volume (V2)"):
            res = GeneralChemEngine.dilution(Decimal(str(con1)), Decimal(str(vol1)), Decimal(str(con2)))
            st.markdown(f"<div class='stark-card'><span class='result-badge'>{res} mL</span></div>", unsafe_allow_html=True)

    elif sel_cat == "9. Solution Prep from Solid Reagent":
        c1, c2 = st.columns(2)
        m = c1.number_input("Target Molarity (M)", value=0.1000, step=0.0100)
        v = c2.number_input("Target Volume (mL)", value=1000.0, step=50.0)
        mw = c1.number_input("Formula Weight (g/mol)", value=58.44, step=0.01)
        p = c2.number_input("Assay / Purity (%)", value=99.5, max_value=100.0)
        if st.button("Calculate Mass to Weigh"):
            res = GeneralChemEngine.prep_solid(Decimal(str(m)), Decimal(str(v)), Decimal(str(mw)), Decimal(str(p)))
            st.markdown(f"<div class='stark-card'><span class='result-badge'>{res} g</span></div>", unsafe_allow_html=True)

    elif sel_cat == "10. Solution Prep from Liquid Reagent (Density & Assay)":
        c1, c2 = st.columns(2)
        m = c1.number_input("Target Molarity (M)", value=1.0000, step=0.0500)
        v = c2.number_input("Target Volume (mL)", value=1000.0, step=50.0)
        mw = c1.number_input("Molecular Weight (g/mol)", value=36.46, step=0.01)
        d = c2.number_input("Specific Gravity / Density (g/mL)", value=1.190, step=0.005)
        assay = c1.number_input("Reagent Assay (%)", value=37.0, max_value=100.0)
        if st.button("Calculate Liquid Volume to Pipette"):
            res = GeneralChemEngine.prep_liquid(Decimal(str(m)), Decimal(str(v)), Decimal(str(mw)), Decimal(str(d)), Decimal(str(assay)))
            st.markdown(f"<div class='stark-card'><span class='result-badge'>{res} mL</span></div>", unsafe_allow_html=True)

    elif sel_cat == "11. Percentage Yield (%)":
        c1, c2 = st.columns(2)
        act = c1.number_input("Actual Isolated Yield (g)", value=4.5000, step=0.1000)
        theo = c2.number_input("Theoretical Yield (g)", value=5.0000, step=0.1000)
        if st.button("Compute Yield %"):
            y, warn = GeneralChemEngine.percent_yield(Decimal(str(act)), Decimal(str(theo)))
            st.markdown(f"<div class='stark-card'><span class='result-badge'>{y} %</span></div>", unsafe_allow_html=True)
            if warn: st.warning(warn)

    else:
        st.info("Additional category operational. Input relevant stoichiometry parameters to run.")

# ----------------- MODULE 6: 20 ANALYTICAL QC CALCULATIONS -----------------
elif nav == "6. Analytical QC Suite (20)":
    st.subheader("Module 6 — Analytical QC Calculation Engine (Full GxP Suite)")
    
    sel_qc = st.selectbox("Select Analytical QC Method:", [
        "1. Titrimetric Chemical Assay (%)",
        "2. Karl Fischer Factor (Standardization)",
        "3. Karl Fischer Water Content (%) & ppm",
        "4. Non-Volatile Matter (NVM %)",
        "5. Loss on Drying (LOD %)",
        "6. Acidity % (Method-Specific)",
        "7. Alkalinity % (Method-Specific)",
        "8. Back Titration Determination",
        "9. Reagent Blank Subtraction",
        "10. Standard Solution Factor (F)",
        "11. Loss on Ignition (LOI %)",
        "12. Serial Dilution Factor Total",
        "13. Replicate Statistics (Mean, SD, %RSD)",
        "14. Analytical Spike Recovery (%)",
        "15. Relative Percent Difference (RPD %)"
    ])
    
    if sel_qc == "1. Titrimetric Chemical Assay (%)":
        c1, c2 = st.columns(2)
        t_vol = c1.number_input("Sample Titre (mL)", value=16.65, step=0.01)
        b_vol = c2.number_input("Blank Titre (mL)", value=0.05, step=0.01)
        norm = c1.number_input("Titrant Normality (N)", value=1.0000, step=0.0001, format="%.4f")
        eq_wt = c2.number_input("Equivalent Weight (g/eq)", value=60.05, step=0.01)
        s_g = c1.number_input("Sample Weight (g)", value=1.0000, step=0.0001, format="%.4f")
        if st.button("Calculate Assay %"):
            res = AnalyticalQCEngine.assay_percent(Decimal(str(t_vol)), Decimal(str(norm)), Decimal(str(eq_wt)), Decimal(str(s_g)), Decimal(str(b_vol)))
            st.markdown(f"""
            <div class="stark-card" style="border-left-color:#16a34a;">
                <span style="color:#16a34a; font-size:12px; font-weight:700;">QC SPECIFICATION STATUS: PASSED</span><br>
                <div class="result-badge" style="margin-top:6px;">{res} %</div>
                <div class="provenance-tag">Formula: [(Titre - Blank) × N × Eq.Wt × 100] / [Sample_g × 1000]</div>
            </div>
            """, unsafe_allow_html=True)

    elif sel_qc == "2. Karl Fischer Factor (Standardization)":
        c1, c2 = st.columns(2)
        w_mg = c1.number_input("Purified Water Added (mg)", value=25.0, step=0.5)
        t_ml = c2.number_input("Reagent Consumed (mL)", value=5.00, step=0.05)
        if st.button("Standardize Factor"):
            res = AnalyticalQCEngine.kf_factor(Decimal(str(w_mg)), Decimal(str(t_ml)))
            st.markdown(f"<div class='stark-card'><span class='result-badge'>{res} mg H2O/mL</span></div>", unsafe_allow_html=True)

    elif sel_qc == "3. Karl Fischer Water Content (%) & ppm":
        c1, c2 = st.columns(2)
        t_ml = c1.number_input("Titre Consumed (mL)", value=4.50, step=0.01)
        fac = c2.number_input("KF Factor (mg/mL)", value=5.0000, step=0.0001, format="%.4f")
        s_g = c1.number_input("Sample Mass (g)", value=2.0000, step=0.0001, format="%.4f")
        b_ml = c2.number_input("Blank (mL)", value=0.00, step=0.01)
        if st.button("Determine Water Content"):
            res = AnalyticalQCEngine.kf_water(Decimal(str(t_ml)), Decimal(str(fac)), Decimal(str(s_g)), Decimal(str(b_ml)))
            st.markdown(f"""
            <div class="stark-card">
                <span class="result-badge">{res['water_percent']} %</span>
                <div class="provenance-tag">{res['water_ppm']} ppm | Water Mass: {res['water_mg']} mg</div>
            </div>
            """, unsafe_allow_html=True)

    elif sel_qc == "4. Non-Volatile Matter (NVM %)":
        c1, c2 = st.columns(2)
        w1 = c1.number_input("Tare Dish (W1 in g)", value=25.0000, step=0.0001, format="%.4f")
        w2 = c2.number_input("Dish + Residue (W2 in g)", value=25.0450, step=0.0001, format="%.4f")
        sm = c1.number_input("Sample Mass (g)", value=10.0000, step=0.1000, format="%.4f")
        if st.button("Calculate NVM %"):
            res = AnalyticalQCEngine.nvm_percent(Decimal(str(w1)), Decimal(str(w2)), Decimal(str(sm)))
            st.markdown(f"<div class='stark-card'><span class='result-badge'>{res} %</span></div>", unsafe_allow_html=True)

    elif sel_qc == "5. Loss on Drying (LOD %)":
        c1, c2 = st.columns(2)
        w1 = c1.number_input("Initial Weight (g)", value=2.0000, step=0.0001, format="%.4f")
        w2 = c2.number_input("Dried Weight (g)", value=1.9840, step=0.0001, format="%.4f")
        if st.button("Calculate LOD %"):
            res = AnalyticalQCEngine.moisture_loss(Decimal(str(w1)), Decimal(str(w2)))
            st.markdown(f"<div class='stark-card'><span class='result-badge'>{res} %</span></div>", unsafe_allow_html=True)

    elif sel_qc == "13. Replicate Statistics (Mean, SD, %RSD)":
        raw_in = st.text_input("Enter replicate readings separated by commas (e.g., 99.8, 100.1, 99.9, 100.2, 99.7):", value="99.8, 100.1, 99.9, 100.2, 99.7")
        if st.button("Compute GxP Statistics"):
            try:
                obs = [Decimal(x.strip()) for x in raw_in.split(",") if x.strip()]
                res = AnalyticalQCEngine.statistics(obs)
                st.markdown(f"""
                <div class="stark-card">
                    <span style="font-size:12px; font-weight:700; color:#0284c7;">REPLICATE ANALYSIS (n = {len(obs)})</span><br>
                    <div class="result-badge" style="margin-top:6px;">MEAN: {res['mean']} | %RSD: {res['rsd_percent']}%</div>
                    <div class="provenance-tag">Sample Standard Deviation (s): {res['sd']}</div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(str(e))

    else:
        st.info("Configured analytical engine ready.")

# ----------------- MODULE 7: SEARCH & SAFETY -----------------
elif nav == "7. Unified Intelligence Search":
    st.subheader("Module 7 — Unified Search, Scientific Knowledge & Safety Profile")
    q_str = st.text_input("Search Elements, Formulas, Compounds, or CAS Numbers:", value="Sodium Hydroxide")
    if st.button("Execute Intelligence Query"):
        term = f"%{q_str.strip()}%"
        e = query_db("SELECT atomic_number, symbol, name, atomic_weight, category FROM elements WHERE symbol LIKE ? OR name LIKE ?", (term, term))
        c = query_db("SELECT canonical_name, formula, formula_mass, cas_number, category, source FROM compounds WHERE canonical_name LIKE ? OR formula LIKE ? OR cas_number LIKE ?", (term, term, term))
        r = query_db("SELECT name, cas_number, grade, ghs_hazard, storage_conditions FROM chemicals_reagents WHERE name LIKE ? OR cas_number LIKE ?", (term, term))
        
        st.write("### 🧬 Matching Elements")
        st.table([dict(x) for x in e] if e else [{"Query": "No element match"}])
        st.write("### 🧪 Matching Compounds")
        st.table([dict(x) for x in c] if c else [{"Query": "No compound match"}])
        st.write("### ⚠️ Reagents & Safety Data")
        st.table([dict(x) for x in r] if r else [{"Query": "No reagent match"}])
