# ---- utils/email_utils.py ----
import yagmail
from config import CFG

def send_email_alert(product_name, current_price, predicted_price, pct_change):

    if not (CFG.EMAIL_FROM and CFG.EMAIL_PASSWORD and CFG.EMAIL_TO):
        return False, "Environment variables for Yagmail not set."

    subject = f"📉 Price Alert — {product_name} ({pct_change:+.2f}%)"
    
    body = f"""
    <h2>Price Alert — {product_name}</h2>
    <p><b>Current Price:</b> ₹{current_price:,.2f}</p>
    <p><b>Predicted Price:</b> ₹{predicted_price:,.2f}</p>
    <p><b>Change:</b> {pct_change:+.2f}%</p>
    """

    try:
        yag = yagmail.SMTP(CFG.EMAIL_FROM, CFG.EMAIL_PASSWORD)
        yag.send(
            to=CFG.EMAIL_TO,
            subject=subject,
            contents=body
        )
        return True, "Email sent via Yagmail"
    except Exception as e:
        return False, str(e)
