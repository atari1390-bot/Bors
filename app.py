import streamlit as st
from data.tsetmc import TSETMC
from data.validator import validate_snapshot
from analysis.technical import technical_analysis
from analysis.orderbook import orderbook_analysis
from analysis.money_flow import money_flow_analysis
from analysis.scoring import score_stock
from analysis.signal import build_signal

st.set_page_config(page_title="Iran Stock AI", page_icon="📈", layout="wide")

st.title("Iran Stock AI")
st.caption("TSETMC محور | داده، تکنیکال، دفتر سفارش، جریان پول و سیگنال")

symbols_text = st.text_input(
    "نمادها را با فاصله یا ویرگول وارد کنید",
    "فولاد وبملت فزر فملی وپاسار",
)

st.info("این ابزار موتور تحلیل است؛ داده روز و شرایط بازار را قبل از معامله دوباره بررسی کنید.")

if st.button("تحلیل نمادها", type="primary"):
    symbols = [s.strip() for s in symbols_text.replace(",", " ").split() if s.strip()]
    if not symbols:
        st.warning("حداقل یک نماد وارد کنید.")
        st.stop()

    api = TSETMC()
    results = []

    with st.spinner("دریافت و تحلیل داده‌ها..."):
        for symbol in symbols:
            try:
                snap = api.snapshot(symbol)
                validation = validate_snapshot(snap)
                tech = technical_analysis(snap.get("history"))
                book = orderbook_analysis(snap.get("orderbook"))
                flow = money_flow_analysis(snap.get("client_type"))
                score = score_stock(tech, book, flow, validation)
                signal = build_signal(snap, tech, book, flow, score)

                results.append({
                    "symbol": symbol,
                    **signal,
                    "data_status": validation.get("status"),
                    "technical_score": score.get("technical_score"),
                    "orderbook_score": score.get("orderbook_score"),
                    "money_flow_score": score.get("money_flow_score"),
                })
            except Exception as exc:
                results.append({
                    "symbol": symbol,
                    "status": "DATA_ERROR",
                    "decision": "خطای داده",
                    "error": str(exc),
                })

    st.subheader("خلاصه")
    st.dataframe(results, use_container_width=True, hide_index=True)

    for result in results:
        st.markdown("---")
        st.subheader(result["symbol"])
        if result.get("status") == "DATA_ERROR":
            st.error(result.get("error", "خطای نامشخص"))
            continue

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("امتیاز", result.get("score", "-"))
        c2.metric("تصمیم", result.get("decision", "-"))
        c3.metric("ورود اول", result.get("entry_1", "-"))
        c4.metric("حد ضرر", result.get("stop", "-"))

        left, right = st.columns(2)
        with left:
            st.write("حمایت:", result.get("support", "-"))
            st.write("مقاومت:", result.get("resistance", "-"))
            st.write("ورود دوم:", result.get("entry_2", "-"))
        with right:
            st.write("هدف ۱:", result.get("target_1", "-"))
            st.write("هدف ۲:", result.get("target_2", "-"))
            st.write("نسبت R/R:", result.get("risk_reward", "-"))

        warnings = result.get("warnings", [])
        if warnings:
            st.warning(" | ".join(warnings))

        st.caption(f"وضعیت داده: {result.get('data_status', '-')}")
