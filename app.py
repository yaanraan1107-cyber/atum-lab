"""
================================================================================
ATUM 0.1 — MOBILE LAB CALCULATOR & EXTENSIVE CHEMISTRY KNOWLEDGE BASE
================================================================================
"""

import re
import streamlit as st
from decimal import Decimal, getcontext
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

getcontext().prec = 28

st.set_page_config(
    page_title="ATUM LAB 0.1",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobile dark-mode UI styling matching screenshot
st.markdown("""
<style>
    .stApp {
        background-color: #0b111e;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .header-box {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }
    .badge {
        background-color: #064e3b;
        color: #34d399;
        font-size: 11px;
        padding: 2px 7px;
        border-radius: 5px;
        font-weight: 600;
    }
    .calc-card {
        background-color: #131c2e;
        border: 1px solid #1e293b;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 14px;
    }
    .section-tag {
        font-size: 11px;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .result-box {
        background-color: #101c33;
        border: 1px solid #10b981;
        padding: 14px;
        border-radius: 12px;
        margin-top: 14px;
        text-align: center;
    }
    .result-val {
        font-size: 24px;
        font-weight: 700;
        color: #34d399;
    }
    .audit-step {
        font-size: 12px;
        color: #94a3b8;
        text-align: left;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 1. COMPREHENSIVE LAB CHEMICALS & REAGENTS DATABASE (WITH AUTO-FILL VALUES)
# ------------------------------------------------------------------------------
@dataclass
class ChemicalItem:
    name: str
    formula: str
    mw: float
    eq_wt: float
    purity: float
    density: Optional[float]
    cas: str
    category: str

LAB_DATABASE: Dict[str, ChemicalItem] = {
    "Sodium Hydroxide (NaOH)": ChemicalItem("Sodium Hydroxide", "NaOH", 40.00, 40.00, 98.0, 2.13, "1310-73-2", "Strong Base"),
    "Hydrochloric Acid (HCl)": ChemicalItem("Hydrochloric Acid", "HCl", 36.46, 36.46, 37.0, 1.19, "7647-01-0", "Strong Acid"),
    "Sulfuric Acid (H2SO4)": ChemicalItem("Sulfuric Acid", "H2SO4", 98.08, 49.04, 98.0, 1.84, "7664-93-9", "Strong Diprotic Acid"),
    "Nitric Acid (HNO3)": ChemicalItem("Nitric Acid", "HNO3", 63.01, 63.01, 70.0, 1.42, "7697-37-2", "Strong Acid"),
    "Acetic Acid - Glacial (CH3COOH)": ChemicalItem("Acetic Acid", "CH3COOH", 60.05, 60.05, 99.5, 1.049, "64-19-7", "Organic Acid"),
    "Oxalic Acid Dihydrate": ChemicalItem("Oxalic Acid Dihydrate", "C2H2O4.2H2O", 126.07, 63.03, 99.5, 1.65, "6153-56-6", "Primary Acid Standard"),
    "Potassium Hydrogen Phthalate (KHP)": ChemicalItem("KHP", "C8H5KO4", 204.22, 204.22, 99.9, None, "877-24-7", "Primary Standard"),
    "Sodium Carbonate (Na2CO3)": ChemicalItem("Sodium Carbonate", "Na2CO3", 105.99, 53.00, 99.5, 2.54, "497-19-8", "Primary Standard Base"),
    "Sodium Bicarbonate (NaHCO3)": ChemicalItem("Sodium Bicarbonate", "NaHCO3", 84.01, 84.01, 99.0, 2.20, "144-55-8", "Buffer Salt"),
    "Sodium Chloride (NaCl)": ChemicalItem("Sodium Chloride", "NaCl", 58.44, 58.44, 99.5, 2.16, "7647-14-5", "Neutral Salt"),
    "Copper(II) Sulfate Pentahydrate": ChemicalItem("Copper Sulfate", "CuSO4.5H2O", 249.68, 249.68, 99.0, 2.28, "7758-99-8", "Hydrate Salt"),
    "Potassium Permanganate (KMnO4)": ChemicalItem("Potassium Permanganate", "KMnO4", 158.03, 31.61, 99.0, 2.70, "7722-64-7", "Redox Titrant"),
    "Silver Nitrate (AgNO3)": ChemicalItem("Silver Nitrate", "AgNO3", 169.87, 169.87, 99.8, 4.35, "7761-88-8", "Precipitation Titrant"),
    "EDTA Disodium Dihydrate": ChemicalItem("EDTA Disodium", "C10H14N2Na2O8.2H2O", 372.24, 186.12, 99.0, None, "6381-92-6", "Complexing Agent"),
    "Methanol": ChemicalItem("Methanol", "CH3OH", 32.04, 32.04, 99.8, 0.792, "67-56-1", "Organic Solvent"),
    "Ethanol": ChemicalItem("Ethanol", "C2H5OH", 46.07, 46.07, 99.9, 0.789, "64-17-5", "Organic Solvent"),
    "Isopropanol (IPA)": ChemicalItem("Isopropanol", "C3H8O", 60.10, 60.10, 99.5, 0.786, "67-63-0", "Organic Solvent"),
    "Acetone": ChemicalItem("Acetone", "C3H6O", 58.08, 58.08, 99.5, 0.784, "67-64-1", "Organic Solvent"),
    "Ethyl Acetate": ChemicalItem("Ethyl Acetate", "C4H8O2", 88.11, 88.11, 99.5, 0.902, "141-78-6", "Organic Solvent"),
    "Acetonitrile": ChemicalItem("Acetonitrile", "C2H3N", 41.05, 41.05, 99.9, 0.786, "75-05-8", "HPLC Solvent"),
    "Toluene": ChemicalItem("Toluene", "C7H8", 92.14, 92.14, 99.5, 0.867, "108-88-3", "Organic Solvent"),
    "Dichloromethane (DCM)": ChemicalItem("Dichloromethane", "CH2Cl2", 84.93, 84.93, 99.5, 1.326, "75-09-2", "Organic Solvent")
}

# ------------------------------------------------------------------------------
# 2. IUPAC ELEMENTS LOOKUP TABLE
# ------------------------------------------------------------------------------
ELEMENTS_MAP = {
    "H": ("Hydrogen", 1.008, 1), "He": ("Helium", 4.0026, 2), "Li": ("Lithium", 6.94, 3),
    "Be": ("Beryllium", 9.0122, 4), "B": ("Boron", 10.81, 5), "C": ("Carbon", 12.011, 6),
    "N": ("Nitrogen", 14.007, 7), "O": ("Oxygen", 15.999, 8), "F": ("Fluorine", 18.998, 9),
    "Ne": ("Neon", 20.180, 10), "Na": ("Sodium", 22.990, 11), "Mg": ("Magnesium", 24.305, 12),
    "Al": ("Aluminium", 26.982, 13), "Si": ("Silicon", 28.085, 14), "P": ("Phosphorus", 30.974, 15),
    "S": ("Sulfur", 32.06, 16), "Cl": ("Chlorine", 35.45, 17), "Ar": ("Argon", 39.95, 18),
    "K": ("Potassium", 39.098, 19), "Ca": ("Calcium", 40.078, 20), "Cr": ("Chromium", 51.996, 24),
    "Mn": ("Manganese", 54.938, 25), "Fe": ("Iron", 55.845, 26), "Ni": ("Nickel", 58.693, 28),
    "Cu": ("Copper", 63.546, 29), "Zn": ("Zinc", 65.38, 30), "Br": ("Bromine", 79.904, 35),
    "Ag": ("Silver", 107.87, 47), "I": ("Iodine", 126.90, 53), "Ba": ("Barium", 137.33, 56),
    "Pb": ("Lead", 207.2, 82), "Au": ("Gold", 196.97, 79), "Og": ("Oganesson", 294.0, 118)
}

# ------------------------------------------------------------------------------
# 3. RECURSIVE FORMULA PARSER ENGINE
# ------------------------------------------------------------------------------
def parse_formula(formula: str) -> Tuple[Decimal, List[str]]:
    formula = formula.strip().replace(" ", "").replace("·", ".").replace("*", ".")
    parts = formula.split(".")
    total_counts = {}
    for idx, part in enumerate(parts):
        multiplier = 1
        if idx > 0:
            m = re.match(r"^(\d+)(.*)$", part)
            if m:
                multiplier = int(m.group(1))
                part = m.group(2)
        
        part_clean = part.replace("[", "(").replace("]", ")").replace("{", "(").replace("}", ")")
        stack = [{}]
        i, n = 0, len(part_clean)
        while i < n:
            c = part_clean[i]
            if c == "(":
                stack.append({})
                i += 1
            elif c == ")":
                popped = stack.pop()
                i += 1
                num_str = ""
                while i < n and part_clean[i].isdigit():
                    num_str += part_clean[i]
                    i += 1
                b_mult = int(num_str) if num_str else 1
                for sym, cnt in popped.items():
                    stack[-1][sym] = stack[-1].get(sym, 0) + (cnt * b_mult)
            elif c.isupper():
                sym = c
                i += 1
                if i < n and part_clean[i].islower():
                    sym += part_clean[i]
                    i += 1
                num_str = ""
                while i < n and part_clean[i].isdigit():
                    num_str += part_clean[i]
                    i += 1
                cnt = int(num_str) if num_str else 1
                stack[-1][sym] = stack[-1].get(sym, 0) + cnt
            else:
                i += 1
        
        for sym, cnt in stack[0].items():
            total_counts[sym] = total_counts.get(sym, 0) + (cnt * multiplier)
    
    total_mw = Decimal("0.0")
    trail = []
    for sym, cnt in total_counts.items():
        if sym in ELEMENTS_MAP:
            name, mass, _ = ELEMENTS_MAP[sym]
            sub = Decimal(str(mass)) * Decimal(cnt)
            total_mw += sub
            trail.append(f"{sym} ({name}): {cnt} × {mass} = {sub:.4f} g/mol")
        else:
            raise ValueError(f"Unknown element symbol '{sym}'")
    return total_mw, trail

# ------------------------------------------------------------------------------
# 4. MOBILE APP USER INTERFACE
# ------------------------------------------------------------------------------
st.markdown("""
<div class="header-box">
    <div style="font-size: 28px;">🧪</div>
    <div>
        <div style="font-size: 20px; font-weight: 700;">ATUM <span class="badge">LAB 0.1</span></div>
        <div style="font-size: 12px; color: #94a3b8;">Analytical QC & Chemistry Knowledge Base</div>
    </div>
</div>
""", unsafe_allow_html=True)

nav = st.radio(
    "Navigation Menu",
    [
        "Normality Mass",
        "Molarity Mass",
        "Assay / Acidity %",
        "NVM %",
        "LOD %",
        "Formula Molar Mass",
        "Chemicals Database",
        "Periodic Elements"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# ----------------- MODULE 1: NORMALITY MASS (AUTO-FILL SUPPORT) -----------------
if nav == "Normality Mass":
    st.markdown("""
    <div class="calc-card">
        <div style="font-size: 16px; font-weight: 600;">Normality Preparation Mass</div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 3px;">
            Mass (g) = (N × Eq.Wt × Vol_mL) / (1000 × (Purity% / 100))
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_chem = st.selectbox("Quick Select Lab Chemical (Auto-fill values)", list(LAB_DATABASE.keys()), index=0)
    chem_data = LAB_DATABASE[selected_chem]

    st.markdown("<div class='section-tag'>📝 INPUT PARAMETERS</div>", unsafe_allow_html=True)
    n_input = st.number_input("Target Normality (N)", value=0.1000, step=0.0100, format="%.4f")
    vol_input = st.number_input("Target Volume (mL)", value=1000.0, step=50.0)
    eq_input = st.number_input("Equivalent Weight (Eq. Wt)", value=float(chem_data.eq_wt), step=0.1)
    purity_input = st.number_input("Reagent Purity / Assay (%)", value=float(chem_data.purity), step=0.5)

    if purity_input > 0 and vol_input > 0:
        pure_m = (Decimal(str(n_input)) * Decimal(str(eq_input)) * Decimal(str(vol_input))) / Decimal("1000.0")
        actual_m = pure_m / (Decimal(str(purity_input)) / Decimal("100.0"))

        st.markdown(f"""
        <div class="result-box">
            <div style="font-size: 12px; color: #94a3b8;">CALCULATED REQUIRED WEIGHT</div>
            <div class="result-val">{actual_m:.4f} g</div>
            <div class="audit-step">• Theoretical Pure Mass: {pure_m:.4f} g</div>
            <div class="audit-step">• Corrected for {purity_input}% Purity: {actual_m:.4f} g</div>
        </div>
        """, unsafe_allow_html=True)

# ----------------- MODULE 2: MOLARITY MASS (AUTO-FILL SUPPORT) -----------------
elif nav == "Molarity Mass":
    st.markdown("""
    <div class="calc-card">
        <div style="font-size: 16px; font-weight: 600;">Molarity Preparation Mass</div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 3px;">
            Mass (g) = (M × Mol.Wt × Vol_mL) / (1000 × (Purity% / 100))
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_chem_m = st.selectbox("Quick Select Lab Chemical (Auto-fill values)", list(LAB_DATABASE.keys()), index=9)
    chem_m_data = LAB_DATABASE[selected_chem_m]

    st.markdown("<div class='section-tag'>📝 INPUT PARAMETERS</div>", unsafe_allow_html=True)
    m_input = st.number_input("Target Molarity (M)", value=0.1000, step=0.0100, format="%.4f")
    vol_m_input = st.number_input("Target Volume (mL)", value=1000.0, step=50.0)
    mw_input = st.number_input("Molecular Weight (MW g/mol)", value=float(chem_m_data.mw), step=0.1)
    purity_m_input = st.number_input("Reagent Purity (%)", value=float(chem_m_data.purity), step=0.5)

    if purity_m_input > 0 and vol_m_input > 0:
        pure_molar = (Decimal(str(m_input)) * Decimal(str(mw_input)) * Decimal(str(vol_m_input))) / Decimal("1000.0")
        actual_molar = pure_molar / (Decimal(str(purity_m_input)) / Decimal("100.0"))

        st.markdown(f"""
        <div class="result-box">
            <div style="font-size: 12px; color: #94a3b8;">CALCULATED REQUIRED WEIGHT</div>
            <div class="result-val">{actual_molar:.4f} g</div>
            <div class="audit-step">• Pure mass: {pure_molar:.4f} g</div>
            <div class="audit-step">• Weighing mass with purity: {actual_molar:.4f} g</div>
        </div>
        """, unsafe_allow_html=True)

# ----------------- MODULE 3: CHEMICAL ASSAY / ACIDITY % -----------------
elif nav == "Assay / Acidity %":
    st.markdown("""
    <div class="calc-card">
        <div style="font-size: 16px; font-weight: 600;">Volumetric Chemical Assay / Acidity %</div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 3px;">
            Assay % = (V × N × Eq.Wt × 100) / (Sample_Weight_g × 1000)
        </div>
    </div>
    <div class="section-tag">📝 INPUT PARAMETERS</div>
    """, unsafe_allow_html=True)

    titre_val = st.number_input("Burette Titre Volume (mL)", value=14.20, step=0.10)
    norm_val = st.number_input("Standardized Titrant Normality (N)", value=0.1025, step=0.0001, format="%.4f")
    eq_analyte_val = st.number_input("Analyte Equivalent Weight", value=60.05, step=0.01, help="Acetic acid = 60.05, HCl = 36.46")
    sample_wt_val = st.number_input("Sample Weight (g)", value=5.0000, step=0.0100, format="%.4f")

    if sample_wt_val > 0:
        assay_res = (Decimal(str(titre_val)) * Decimal(str(norm_val)) * Decimal(str(eq_analyte_val)) * Decimal("100.0")) / (Decimal(str(sample_wt_val)) * Decimal("1000.0"))
        st.markdown(f"""
        <div class="result-box">
            <div style="font-size: 12px; color: #94a3b8;">ASSAY / ACIDITY RESULT</div>
            <div class="result-val">{assay_res:.4f} %</div>
            <div class="audit-step">• Method Ref: PPC-SOP-QC-ASY-010</div>
        </div>
        """, unsafe_allow_html=True)

# ----------------- MODULE 4: NON-VOLATILE MATTER (NVM) -----------------
elif nav == "NVM %":
    st.markdown("""
    <div class="calc-card">
        <div style="font-size: 16px; font-weight: 600;">Non-Volatile Matter (Residue on Evaporation)</div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 3px;">
            NVM % = ((W2 - W1) / Sample_Weight_g) × 100
        </div>
    </div>
    <div class="section-tag">📝 INPUT PARAMETERS</div>
    """, unsafe_allow_html=True)

    w1_val = st.number_input("Empty Crucible Weight (W1 in g)", value=25.0000, step=0.0001, format="%.4f")
    w2_val = st.number_input("Crucible + Residue Weight (W2 in g)", value=25.0450, step=0.0001, format="%.4f")
    sample_g_val = st.number_input("Sample Weight Taken (g)", value=10.0000, step=0.1000, format="%.4f")

    if sample_g_val > 0 and w2_val >= w1_val:
        net_res = Decimal(str(w2_val)) - Decimal(str(w1_val))
        nvm_res = (net_res / Decimal(str(sample_g_val))) * Decimal("100.0")
        st.markdown(f"""
        <div class="result-box">
            <div style="font-size: 12px; color: #94a3b8;">NON-VOLATILE MATTER (NVM)</div>
            <div class="result-val">{nvm_res:.4f} %</div>
            <div class="audit-step">• Net Residue Weight: {net_res:.5f} g</div>
        </div>
        """, unsafe_allow_html=True)
    elif w2_val < w1_val:
        st.error("W2 cannot be less than W1. Check balance weighings.")

# ----------------- MODULE 5: LOSS ON DRYING (LOD) -----------------
elif nav == "LOD %":
    st.markdown("""
    <div class="calc-card">
        <div style="font-size: 16px; font-weight: 600;">Loss on Drying (LOD / Moisture Loss)</div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 3px;">
            LOD % = ((Initial Weight - Dry Weight) / Initial Weight) × 100
        </div>
    </div>
    <div class="section-tag">📝 INPUT PARAMETERS</div>
    """, unsafe_allow_html=True)

    init_wt = st.number_input("Initial Sample Weight (W1 in g)", value=2.0000, step=0.0001, format="%.4f")
    dry_wt = st.number_input("Constant Dry Weight (W2 in g)", value=1.9840, step=0.0001, format="%.4f")

    if init_wt > 0 and dry_wt <= init_wt:
        loss_val = Decimal(str(init_wt)) - Decimal(str(dry_wt))
        lod_res = (loss_val / Decimal(str(init_wt))) * Decimal("100.0")
        st.markdown(f"""
        <div class="result-box">
            <div style="font-size: 12px; color: #94a3b8;">LOSS ON DRYING (LOD)</div>
            <div class="result-val">{lod_res:.4f} %</div>
            <div class="audit-step">• Net Mass Loss: {loss_val:.5f} g</div>
        </div>
        """, unsafe_allow_html=True)
    elif dry_wt > init_wt:
        st.error("Dry weight cannot be greater than initial sample weight.")

# ----------------- MODULE 6: FORMULA PARSER & MOLAR MASS -----------------
elif nav == "Formula Molar Mass":
    st.markdown("""
    <div class="calc-card">
        <div style="font-size: 16px; font-weight: 600;">Formula Molar Mass Engine</div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 3px;">
            Supports brackets and hydrates (e.g., CuSO4.5H2O, Al2(SO4)3, Na2CO3)
        </div>
    </div>
    """, unsafe_allow_html=True)

    f_in = st.text_input("Enter Chemical Formula", value="CuSO4.5H2O")
    if f_in.strip():
        try:
            mw, trail = parse_formula(f_in)
            st.markdown(f"""
            <div class="result-box">
                <div style="font-size: 12px; color: #94a3b8;">CALCULATED MOLAR MASS</div>
                <div class="result-val">{mw:.4f} g/mol</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div class='section-tag' style='margin-top:10px;'>🔬 STOICHIOMETRIC BREAKDOWN</div>", unsafe_allow_html=True)
            for t in trail:
                st.markdown(f"<div class='audit-step'>• {t}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Formula Parsing Error: {e}")

# ----------------- MODULE 7: CHEMICALS & REAGENTS DATABASE -----------------
elif nav == "Chemicals Database":
    st.markdown("""
    <div class="calc-card">
        <div style="font-size: 16px; font-weight: 600;">Laboratory Chemicals Knowledge Base</div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 3px;">
            Inorganic bases, acids, salts, primary standards, and organic solvents
        </div>
    </div>
    """, unsafe_allow_html=True)

    chem_choice = st.selectbox("Select Chemical to View Details", list(LAB_DATABASE.keys()))
    c = LAB_DATABASE[chem_choice]

    st.markdown(f"""
    <div class="calc-card">
        <div style="font-size: 18px; font-weight: 700; color: #38bdf8;">{c.name}</div>
        <div style="font-size: 13px; color: #cbd5e1; margin-top: 4px;">Formula: <b>{c.formula}</b> | CAS: <b>{c.cas}</b></div>
        <div style="font-size: 13px; color: #cbd5e1; margin-top: 2px;">Category: <b>{c.category}</b></div>
    </div>
    <div class="result-box">
        <div class="audit-step">• Molecular Weight (MW): <b>{c.mw} g/mol</b></div>
        <div class="audit-step">• Equivalent Weight (Eq.Wt): <b>{c.eq_wt} g/eq</b></div>
        <div class="audit-step">• Typical Assay / Purity: <b>{c.purity} %</b></div>
        <div class="audit-step">• Liquid Density: <b>{c.density or 'Solid'} g/mL</b></div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- MODULE 8: PERIODIC ELEMENTS -----------------
elif nav == "Periodic Elements":
    st.markdown("""
    <div class="calc-card">
        <div style="font-size: 16px; font-weight: 600;">IUPAC Elements Lookup</div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 3px;">
            Atomic numbers, symbols, and standard atomic weights
        </div>
    </div>
    """, unsafe_allow_html=True)

    sym_query = st.text_input("Enter Element Symbol (e.g. H, Na, Fe, Cu)", value="Na").strip().capitalize()
    if sym_query in ELEMENTS_MAP:
        el_name, el_weight, el_z = ELEMENTS_MAP[sym_query]
        st.markdown(f"""
        <div class="result-box">
            <div style="font-size: 12px; color: #94a3b8;">ATOMIC NUMBER (Z = {el_z})</div>
            <div class="result-val">{el_name} ({sym_query})</div>
            <div class="audit-step" style="text-align:center; margin-top:6px;">Standard Atomic Weight: <b>{el_weight} g/mol</b></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"Element '{sym_query}' not found. Try symbols like H, C, O, Na, Fe, Cu, Ag.")
