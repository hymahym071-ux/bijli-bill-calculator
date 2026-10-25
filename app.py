import pandas as pd
import streamlit as st
from models import (DomesticCustomer, CommercialCustomer, Bill,
                    InvalidReadingError, save_customers, load_customers)

MONTH = "October 2026"

st.set_page_config(page_title="Bijli Bill Calculator", page_icon="⚡", layout="centered")

st.markdown("""
<style>
#MainMenu, footer { visibility: hidden; }
.stApp { background: #f1f5f9; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.5rem; max-width: 980px; }

/* Sidebar */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a, #1e293b); }
.side-logo { font-size: 1.5rem; font-weight: 800; color: #fbbf24; margin-bottom: 2px; }
.side-sub { color: #94a3b8; font-size: 0.85rem; margin-bottom: 18px; }
.side-title { color: #e2e8f0; font-weight: 700; margin: 16px 0 6px 0; }
.side-row { display: flex; justify-content: space-between; color: #cbd5e1;
            font-size: 0.88rem; padding: 3px 0; }
.side-row b { color: #fbbf24; }
.side-note { color: #64748b; font-size: 0.75rem; margin-top: 14px; }

/* Hero banner */
.hero { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #2563eb 100%);
        border-radius: 20px; padding: 30px 28px; margin-bottom: 22px;
        box-shadow: 0 8px 24px rgba(30, 58, 138, 0.35); }
.hero h1 { margin: 0; font-size: 2.3rem; color: #ffffff; }
.hero h1 span { color: #fbbf24; }
.hero p { margin: 6px 0 12px 0; color: #bfdbfe; }
.pill { display: inline-block; background: #fbbf24; color: #0f172a; font-weight: 700;
        border-radius: 999px; padding: 4px 14px; font-size: 0.82rem; }

/* Labels / tabs */
[data-testid="stWidgetLabel"] p, [data-testid="stRadio"] label p { color: #1e293b !important; font-weight: 600; }
button[data-baseweb="tab"] p { color: #334155; font-weight: 700; font-size: 1rem; }

/* Form card */
[data-testid="stForm"] { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px;
                         padding: 24px; box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08); }
[data-testid="stFormSubmitButton"] button { width: 100%; background: linear-gradient(135deg, #f59e0b, #ef4444);
        border: none; padding: 0.7rem; border-radius: 12px; }
[data-testid="stFormSubmitButton"] button p { color: #ffffff !important; font-weight: 800; font-size: 1.05rem; }

/* Metric cards */
[data-testid="stMetric"] { background: #ffffff; border: 1px solid #e2e8f0; border-left: 6px solid #f59e0b;
                           border-radius: 14px; padding: 14px 18px; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06); }
[data-testid="stMetric"] * { color: #0f172a !important; }

/* Bill receipt */
.receipt { background: #ffffff; border-radius: 18px; overflow: hidden; margin-top: 16px;
           box-shadow: 0 6px 22px rgba(15, 23, 42, 0.14); }
.receipt-head { background: linear-gradient(135deg, #f59e0b, #ef4444); padding: 18px 24px; color: #ffffff; }
.receipt-head h3 { margin: 0; font-size: 1.2rem; color: #ffffff; }
.receipt-head div { opacity: 0.95; font-size: 0.9rem; margin-top: 2px; }
.receipt-body { padding: 18px 24px 22px 24px; color: #1e293b; }
.r-row { display: flex; justify-content: space-between; padding: 6px 0; }
.r-line { border-top: 2px dashed #cbd5e1; margin: 10px 0; }
.r-total { font-size: 1.35rem; font-weight: 800; color: #15803d; }
.r-late { font-weight: 700; color: #b91c1c; }
.stack { display: flex; height: 14px; border-radius: 999px; overflow: hidden; margin: 6px 0 8px 0; background: #e2e8f0; }
.legend { display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.8rem; color: #475569; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }

/* Customer cards */
.cust-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; margin: 14px 0 22px 0; }
.cust { background: #ffffff; border-radius: 16px; padding: 16px 18px; border: 1px solid #e2e8f0;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.07); }
.cust-top { display: flex; align-items: center; gap: 12px; }
.avatar { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
          background: linear-gradient(135deg, #2563eb, #7c3aed); color: #ffffff; font-weight: 800; }
.cust-name { font-weight: 700; color: #0f172a; }
.cust-ref { color: #64748b; font-size: 0.82rem; }
.badge { margin-left: auto; font-size: 0.72rem; font-weight: 700; border-radius: 999px; padding: 3px 10px; }
.b-dom { background: #dcfce7; color: #166534; }
.b-com { background: #dbeafe; color: #1e40af; }
.cust-bottom { display: flex; justify-content: space-between; margin-top: 14px; color: #475569; font-size: 0.85rem; }
.cust-bottom b { color: #0f172a; font-size: 1.05rem; }
</style>
""", unsafe_allow_html=True)


def bill_receipt(bill):
    c = bill.customer
    parts = [
        ("Energy", bill.energy, "#2563eb"),
        ("Fixed", bill.fixed, "#7c3aed"),
        ("GST", bill.gst, "#f59e0b"),
        ("TV fee", bill.tv_fee, "#10b981"),
    ]
    bar = "".join(
        f'<div style="width:{v / bill.total * 100:.2f}%;background:{col}"></div>'
        for _, v, col in parts if v > 0
    )
    legend = "".join(
        f'<span><span class="dot" style="background:{col}"></span>{n}</span>'
        for n, v, col in parts if v > 0
    )
    return (
        '<div class="receipt">'
        '<div class="receipt-head">'
        f'<h3>⚡ BIJLI BILL - {bill.month}</h3>'
        f'<div>{c.name} | Ref {c.ref_no} | {c.CATEGORY}</div>'
        '</div>'
        '<div class="receipt-body">'
        f'<div class="r-row"><span>Reading</span><span>{c.previous} → {c.current}</span></div>'
        f'<div class="r-row"><span>Units</span><b>{c.units}</b></div>'
        '<div class="r-line"></div>'
        f'<div class="r-row"><span>Energy charges</span><span>Rs {bill.energy:,.2f}</span></div>'
        f'<div class="r-row"><span>Fixed charges</span><span>Rs {bill.fixed:,.2f}</span></div>'
        f'<div class="r-row"><span>GST (17%)</span><span>Rs {bill.gst:,.2f}</span></div>'
        f'<div class="r-row"><span>TV fee</span><span>Rs {bill.tv_fee:,.2f}</span></div>'
        f'<div class="stack">{bar}</div>'
        f'<div class="legend">{legend}</div>'
        '<div class="r-line"></div>'
        f'<div class="r-row r-total"><span>TOTAL</span><span>Rs {bill.total:,.2f}</span></div>'
        f'<div class="r-row r-late"><span>Due date ke baad</span><span>Rs {bill.late_total:,.2f}</span></div>'
        '</div></div>'
    )


def customer_card(c, bill):
    initials = "".join(w[0] for w in c.name.split()[:2]).upper()
    badge = "b-dom" if c.CATEGORY == "Domestic" else "b-com"
    return (
        '<div class="cust">'
        '<div class="cust-top">'
        f'<div class="avatar">{initials}</div>'
        f'<div><div class="cust-name">{c.name}</div><div class="cust-ref">Ref {c.ref_no}</div></div>'
        f'<span class="badge {badge}">{c.CATEGORY}</span>'
        '</div>'
        '<div class="cust-bottom">'
        f'<span>Units<br><b>{c.units}</b></span>'
        f'<span style="text-align:right">Total<br><b>Rs {bill.total:,.0f}</b></span>'
        '</div></div>'
    )


customers = load_customers()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(
        '<div class="side-logo">⚡ Bijli Bill</div>'
        '<div class="side-sub">ALCI | Project 2 (OOP)</div>'
        '<div class="side-title">Domestic rates</div>'
        '<div class="side-row"><span>Pehle 100 units</span><b>Rs 10</b></div>'
        '<div class="side-row"><span>101 - 200 units</span><b>Rs 15</b></div>'
        '<div class="side-row"><span>201 - 300 units</span><b>Rs 20</b></div>'
        '<div class="side-row"><span>300 se upar</span><b>Rs 30</b></div>'
        '<div class="side-title">Commercial rate</div>'
        '<div class="side-row"><span>Har unit</span><b>Rs 40</b></div>'
        '<div class="side-row"><span>Fixed charges</span><b>Rs 500</b></div>'
        '<div class="side-title">Baqi charges</div>'
        '<div class="side-row"><span>GST</span><b>17%</b></div>'
        '<div class="side-row"><span>TV fee</span><b>Rs 35</b></div>'
        '<div class="side-row"><span>Late payment</span><b>+10%</b></div>'
        '<div class="side-note">Rates sirf practice ke liye hain.</div>',
        unsafe_allow_html=True,
    )

# ---------- Hero ----------
st.markdown(
    '<div class="hero"><h1>⚡ Bijli Bill <span>Calculator</span></h1>'
    '<p>Meter reading likhein, bill foran tayyar.</p>'
    f'<span class="pill">{MONTH}</span></div>',
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["⚡ Naya Bill", "👥 Saare Customers"])

# ---------- Tab 1: Naya bill ----------
with tab1:
    with st.form("new_customer"):
        col1, col2 = st.columns(2)
        ref_no = col1.text_input("Reference no")
        name = col2.text_input("Naam")
        kind = st.radio("Type", ["Domestic", "Commercial"], horizontal=True)
        col3, col4 = st.columns(2)
        previous = col3.number_input("Previous reading", min_value=0, step=1)
        current = col4.number_input("Current reading", min_value=0, step=1)
        submitted = st.form_submit_button("⚡ Bill banayein")

    if submitted:
        cls = DomesticCustomer if kind == "Domestic" else CommercialCustomer
        try:
            if not ref_no or not name:
                st.warning("Reference no aur naam dono likhein.")
            elif any(c.ref_no == ref_no for c in customers):
                st.warning("Ye reference no pehle se mojood hai.")
            else:
                customer = cls(ref_no, name, int(previous), int(current))
                customers.append(customer)
                save_customers(customers)
                bill = Bill(customer, MONTH)
                st.success(f"{customer.name} ka bill ban gaya.")
                m1, m2, m3 = st.columns(3)
                m1.metric("Units", customer.units)
                m2.metric("Total", f"Rs {bill.total:,.0f}")
                m3.metric("Due date ke baad", f"Rs {bill.late_total:,.0f}")
                st.markdown(bill_receipt(bill), unsafe_allow_html=True)
        except InvalidReadingError as e:
            st.error(str(e))

# ---------- Tab 2: Saare customers ----------
with tab2:
    if customers:
        bills = [Bill(c, MONTH) for c in customers]
        k1, k2, k3 = st.columns(3)
        k1.metric("Kul customers", len(customers))
        k2.metric("Kul units", sum(c.units for c in customers))
        k3.metric("Kul raqam", f"Rs {sum(b.total for b in bills):,.0f}")

        cards = "".join(customer_card(c, b) for c, b in zip(customers, bills))
        st.markdown(f'<div class="cust-grid">{cards}</div>', unsafe_allow_html=True)

        rows = [{"Ref": c.ref_no, "Naam": c.name, "Type": c.CATEGORY,
                 "Units": c.units, "Total (Rs)": b.total}
                for c, b in zip(customers, bills)]
        st.subheader("Table")
        st.dataframe(rows, hide_index=True)

        st.subheader("Customers ka bill")
        chart_data = pd.DataFrame(rows).set_index("Naam")[["Total (Rs)"]]
        st.bar_chart(chart_data, color="#f59e0b")
    else:
        st.info("Abhi koi customer nahi.")