# # ---- styles.py ----
# import streamlit as st
# from config import CFG

# def inject_css():
#     st.markdown(
#         f"""
#     <style>
#         @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

#         html, body, [class*="css"]  {{
#             font-family: 'Poppins', sans-serif !important;
#             background: linear-gradient(135deg, #f5f7fa 0%, #dfe9f3 100%) !important;
#         }}

#         /* ---- CARD (Glassmorphism) ---- */
#         .card {{
#             background: rgba(255, 255, 255, 0.65);
#             backdrop-filter: blur(12px);
#             border-radius: 20px;
#             padding: 22px;
#             box-shadow: 0 15px 35px rgba(0,0,0,0.08);
#             border: 1px solid rgba(255,255,255,0.4);
#             margin-bottom: 22px;
#             transition: transform .2s ease, box-shadow .2s ease;
#         }}
#         .card:hover {{
#             transform: translateY(-4px);
#             box-shadow: 0 20px 45px rgba(0,0,0,0.12);
#         }}

#         /* ---- HEADER ---- */
#         .header {{
#             background: linear-gradient(90deg,#6d28d9,#8b5cf6,#a78bfa);
#             padding: 26px;
#             border-radius: 18px;
#             color: white !important;
#             box-shadow: 0 12px 30px rgba(109,40,217,0.25);
#             margin-bottom: 20px;
#         }}

#         /* KPI Title */
#         .kpi-title {{
#             color: #6b7280;
#             font-size: 12px;
#             text-transform: uppercase;
#             letter-spacing: 1px;
#             margin-bottom: 4px;
#         }}

#         /* KPI Metric */
#         .big-metric {{
#             font-size: 26px;
#             font-weight: 700;
#             background: linear-gradient(90deg,#6d28d9,#8b5cf6,#a78bfa);
#             -webkit-background-clip: text;
#             -webkit-text-fill-color: transparent;
#         }}

#         /* Buttons */
#         .stButton>button {{
#             background: linear-gradient(135deg,#6d28d9,#8b5cf6,#c084fc);
#             color: white;
#             border-radius: 12px;
#             padding: 10px 20px;
#             font-size: 15px;
#             font-weight: 600;
#             box-shadow: 0 8px 20px rgba(124,58,237,0.45);
#             transition: transform .15s ease;
#             border: none;
#         }}
#         .stButton>button:hover {{
#             transform: translateY(-3px);
#             box-shadow: 0 12px 30px rgba(124,58,237,0.6);
#         }}

#         /* Tables */
#         thead tr th {{
#             background: #6d28d9 !important;
#             color: white !important;
#             font-weight: 600;
#         }}

#         /* Sidebar Styling */
#         section[data-testid="stSidebar"] {{
#             background: linear-gradient(180deg,#6d28d9,#7c3aed,#8b5cf6);
#         }}
#         section[data-testid="stSidebar"] * {{
#             color: white !important;
#         }}
#     </style>
#     """,
#         unsafe_allow_html=True,
#     )
# ---- styles.py ----
import streamlit as st

def inject_css():
    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* -------------------------------------------------- */
    /* GLOBAL STYLING                                      */
    /* -------------------------------------------------- */

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background: #f4f6fb !important;
        color: #1f2937 !important;
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* -------------------------------------------------- */
    /* PREMIUM HEADER BANNER                               */
    /* -------------------------------------------------- */

    .header {
        background: linear-gradient(135deg, #6d28d9 0%, #7c3aed 40%, #c084fc 100%);
        padding: 35px 40px;
        border-radius: 22px;
        box-shadow: 0px 20px 40px rgba(109,40,217,0.25);
        color: #ffffff !important;
        margin-bottom: 35px;
    }

    .header h1 {
        font-size: 40px !important;
        font-weight: 800 !important;
        margin: 0;
        color: #fff !important;
        letter-spacing: -0.5px;
        text-shadow: 0px 4px 12px rgba(0,0,0,0.25) !important;
    }

    .header .subtitle {
        margin-top: 12px;
        font-size: 19px;
        opacity: 0.95;
        font-weight: 500;
        color: #fefefe !important;
        text-shadow: 0px 2px 8px rgba(0,0,0,0.28);
    }

    /* -------------------------------------------------- */
    /* KPI CARDS (Floating premium style)                 */
    /* -------------------------------------------------- */

    .kpi-card {
        background: #ffffff;
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0px 10px 28px rgba(0,0,0,0.06);
        transition: all 0.25s ease;
        border: 1px solid rgba(0,0,0,0.05);
    }

    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0px 16px 35px rgba(0,0,0,0.10);
    }

    .kpi-title {
        font-size: 13px;
        text-transform: uppercase;
        color: #6b7280;
        margin-bottom: 5px;
        font-weight: 600;
        letter-spacing: 1px;
    }

    .kpi-value {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(90deg,#6d28d9,#9333ea,#c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* -------------------------------------------------- */
    /* TABLES (premium rounded & striped)                 */
    /* -------------------------------------------------- */

    thead tr th {
        background: #6d28d9 !important;
        color: white !important;
        padding: 10px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        border-bottom: none !important;
    }

    tbody tr:nth-child(odd) {
        background: #f4ecff !important;
    }

    tbody tr td {
        padding: 10px 14px !important;
        font-size: 14px !important;
    }

    /* -------------------------------------------------- */
    /* BUTTONS (modern pill style)                        */
    /* -------------------------------------------------- */

    .stButton > button {
        background: linear-gradient(135deg,#6d28d9,#8b5cf6,#c084fc);
        color: white !important;
        padding: 12px 26px;
        border-radius: 14px !important;
        border: none !important;
        font-size: 15px;
        font-weight: 600;
        box-shadow: 0px 12px 25px rgba(109,40,217,0.35);
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0px 18px 32px rgba(109,40,217,0.45);
    }

    /* -------------------------------------------------- */
    /* SIDEBAR (premium vertical nav)                     */
    /* -------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg,#6d28d9,#7c3aed,#8b5cf6);
        padding-top: 25px;
        color: white !important;
        border-right: 1px solid rgba(255,255,255,0.25);
    }

    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* Sidebar titles */
    .css-1d391kg, .css-1n76uvr, .css-qrbaxs {
        font-size: 20px !important;
        font-weight: 700 !important;
    }

    /* Sidebar radio buttons */
    div[role="radiogroup"] > label {
        background: rgba(255,255,255,0.12) !important;
        padding: 10px 14px !important;
        border-radius: 12px !important;
        margin-bottom: 6px !important;
        transition: all 0.2s ease;
    }
    div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.22) !important;
        cursor: pointer;
    }

    /* -------------------------------------------------- */
    /* HIDE FOOTER + MENU                                  */
    /* -------------------------------------------------- */

    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}

    </style>
    """, unsafe_allow_html=True)
