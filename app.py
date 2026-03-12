import streamlit as st
import pandas as pd
import os
import math

# 1. Page Configuration
ICON_PATH = "assets/iconlogo.png"
LOGO_PATH = "assets/ylogo.png"

st.set_page_config(
    page_title="AL-YOUSR HUB", 
    layout="wide", 
    page_icon=ICON_PATH if os.path.exists(ICON_PATH) else "⚙️"
)

# 2. International Professional Styling (CSS)
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    .stMetric { background-color: #1e293b; padding: 20px; border-radius: 12px; border-bottom: 4px solid #38bdf8; }
    [data-testid="stMetricValue"] { color: #38bdf8 !important; font-size: 28px !important; font-family: 'Courier New', monospace; }
    .section-header { 
        color: #f8fafc; background: linear-gradient(90deg, #0369a1 0%, #0f172a 100%); 
        padding: 12px; border-radius: 8px; margin-top: 30px; font-weight: bold; font-size: 20px; letter-spacing: 1px;
    }
    .price-card { 
        background-color: #0f172a; padding: 25px; border-radius: 15px; border: 1px solid #10b981; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background: linear-gradient(90deg, #38bdf8 0%, #1d4ed8 100%);
        color: white; border: none; padding: 15px; font-weight: bold; border-radius: 8px; height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Technical Constants
WRENCH_SIZES = {
    16: 24, 20: 30, 24: 36, 27: 41, 30: 46, 33: 50, 36: 55, 39: 60, 
    42: 65, 45: 70, 48: 75, 52: 80, 56: 85, 60: 90, 64: 95
}

# 4. State Management
if 'process_ready' not in st.session_state:
    st.session_state.process_ready = False

def activate_report():
    st.session_state.process_ready = True

# 5. Home Header with Your Logo
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=350) 
else:
    st.title("AL-YOUSR HUB ⚙️")

st.caption("Precision Engineering & Steel Fabrication Hub")

# 6. Data Engine
FILE_NAME = "flanges data.xlsx"
if os.path.exists(FILE_NAME):
    df = pd.read_excel(FILE_NAME)
    
    # --- STEP 1: SPECIFICATION SELECTION ---
    st.markdown('<div class="section-header">01. GLOBAL SPECIFICATIONS</div>', unsafe_allow_html=True)
    sel_col1, sel_col2 = st.columns(2)
    with sel_col1:
        pn_val = st.selectbox("PRESSURE RATING (PN)", sorted(df['PN'].unique()))
    with sel_col2:
        dn_list = sorted(df[df['PN'] == pn_val]['DN'].unique())
        dn_val = st.selectbox("NOMINAL DIAMETER (DN)", dn_list)

    res = df[(df['PN'] == pn_val) & (df['DN'] == dn_val)].iloc[0]
    
    # Technical Mapping
    D, DN_int, C, b, f, d_rf, K, Holes_N = float(res['D']), float(res['DN']), float(res['C']), float(res['b']), float(res['f']), float(res['d']), float(res['K']), float(res['Holes Num'])
    M_str = str(res['Screw M'])
    try: m_num = int(''.join(filter(str.isdigit, M_str)))
    except: m_num = 0

    st.button("GENERATE TECHNICAL DATA", on_click=activate_report, use_container_width=True)

    if st.session_state.process_ready:
        # GEOMETRIC CALCULATIONS
        density = 0.00000785
        vol_body = (math.pi / 4) * (D**2 - DN_int**2) * b
        vol_rf = (math.pi / 4) * (d_rf**2 - DN_int**2) * f
        hole_dia = m_num + 2 
        vol_holes = (math.pi / 4) * (hole_dia**2) * b * Holes_N
        net_weight = (vol_body + vol_rf - vol_holes) * density
        
        wrench = WRENCH_SIZES.get(m_num, "N/A")
        chord_K = K * math.sin(math.radians(180 / Holes_N))

        # --- SECTION 1: MAIN DIMENSIONS ---
        st.markdown('<div class="section-header">02. MAIN DIMENSIONS & BOLTING REFERENCE</div>', unsafe_allow_html=True)
        if os.path.exists("assets/flange.png"):
            st.image("assets/flange.png", use_container_width=True)

        m_main1, m_main2 = st.columns(2)
        m_main1.metric("KEY SIZE (WRENCH)", f"{wrench} mm")
        m_main2.metric("CHORD FOR K (PITCH)", f"{chord_K:.2f} mm")

        grid1, grid2, grid3 = st.columns(3)
        with grid1:
            st.metric("D (Outer)", f"{D}")
            st.metric("DN (Internal)", f"{DN_int}")
            st.metric("NET WEIGHT", f"{net_weight:.2f} Kg")
        with grid2:
            st.metric("C (Full Height)", f"{C}")
            st.metric("b (Body Thickness)", f"{b}")
            st.metric("f (RF Thickness)", f"{f}")
        with grid3:
            st.metric("d (RF Diameter)", f"{d_rf}")
            st.metric("HOLES COUNT", int(Holes_N))
            st.metric("SCREW SIZE", M_str)

        # --- SECTION 2: SEGMENTS ---
        st.markdown('<div class="section-header">03. SEGMENTS & FABRICATION GUIDE</div>', unsafe_allow_html=True)
        if os.path.exists("assets/segments model.png"):
            st.image("assets/segments model.png", use_container_width=True)
            
        seg_col1, seg_col2 = st.columns([1, 2])
        with seg_col1:
            n_seg = st.number_input("INPUT SEGMENT COUNT (n):", min_value=1, value=4)
        
        W_on_D = D * math.sin(math.radians(180 / n_seg))
        seg_weight = ((math.pi / 4) * (D**2 - DN_int**2) * (C + 2)) * density / n_seg
        
        with seg_col2:
            s_m1, s_m2 = st.columns(2)
            s_m1.metric("CHORD LENGTH (W)", f"{W_on_D:.2f} mm")
            s_m2.metric("SEGMENT WEIGHT (C+2)", f"{seg_weight:.2f} Kg")

        # --- SECTION 3: COMMERCIAL ---
        st.markdown('<div class="section-header">04. COMMERCIAL DATA & PRICING ANALYSIS</div>', unsafe_allow_html=True)
        
        raw_weight_total = ((math.pi / 4) * (D**2 - DN_int**2) * (C + 2)) * density
        scrap_ratio = ((raw_weight_total - net_weight) / raw_weight_total) * 100

        p_col1, p_col2 = st.columns(2)
        with p_col1:
            p_raw = st.number_input("RAW MATERIAL PRICE (EGP/Kg):", value=0.0)
            st.markdown(f"""
            <div class="price-card">
                <h4 style="color:#94a3b8; margin:0;">RAW MATERIAL STATUS</h4>
                <p style="margin:5px 0;">RAW WEIGHT: <b>{raw_weight_total:.2f} Kg</b></p>
                <h2 style="color:#38bdf8; margin:0;">COST: {(raw_weight_total * p_raw):,.2f} EGP</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with p_col2:
            p_fin = st.number_input("FINISHED PRODUCT PRICE (EGP/Kg):", value=0.0)
            st.markdown(f"""
            <div class="price-card">
                <h4 style="color:#94a3b8; margin:0;">FINISHED PRODUCT STATUS</h4>
                <p style="margin:5px 0;">NET WEIGHT: <b>{net_weight:.2f} Kg</b></p>
                <h2 style="color:#10b981; margin:0;">VALUE: {(net_weight * p_fin):,.2f} EGP</h2>
            </div>
            """, unsafe_allow_html=True)

        st.info(f"📊 **MATERIAL SCRAP RATIO:** {scrap_ratio:.1f}%")

else:
    st.error("DATABASE ERROR: 'flanges data.xlsx' not found.")