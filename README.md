# Iran Stock AI — Clean Build

TSETMC محور برای تحلیل چندنماد.

## اجرا
```bash
pip install -r requirements.txt
streamlit run app.py
```

## ساختار
- `data/tsetmc.py`: اتصال به TSETMC
- `data/validator.py`: اعتبارسنجی snapshot
- `analysis/technical.py`: RSI، MACD، SMA20/50/100/200، حجم، حمایت و مقاومت
- `analysis/orderbook.py`: دفتر سفارش و نسبت خرید/فروش
- `analysis/money_flow.py`: استخراج جریان پول حقیقی/حقوقی با چند الگوی کلید
- `analysis/scoring.py`: امتیاز ۰ تا ۱۰۰
- `analysis/signal.py`: ورود، حد ضرر، اهداف و R/R
- `app.py`: رابط Streamlit

این نسخه هنگام نبود داده، به‌جای ساختن سیگنال قطعی، وضعیت بررسی داده را نشان می‌دهد.
