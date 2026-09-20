import os
import json
from flask import Flask, request
import requests

app = Flask(__name__)

# بيانات البوت والملفات
TELEGRAM_BOT_TOKEN = "8989095746:AAHOl9g15Yt-n8x9R0YgZEPdjhsZjhsKLw8"
BALANCE_FILE = "balance_state.json"

def get_current_balance():
    if not os.path.exists(BALANCE_FILE):
        return 0
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("balance", 0)
    except:
        return 0

def update_balance(amount_to_add):
    current = get_current_balance()
    new_balance = current + amount_to_add
    data = {
        "balance": new_balance,
        "last_updated": "2026-09-20"
    }
    with open(BALANCE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return new_balance

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Error sending message:", e)

@app.route("/", methods=["POST"])
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        update = request.get_json()
        if not update:
            return "OK", 200

        # الاستجابة للرسائل النصية المباشرة بدلاً من الأزرار
        if "message" in update and "text" in update["message"]:
            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message["text"].strip()

            # 1. إذا كتبت "موافقة" أو "+100" أو "/approve"
            if text in ["موافقة", "+100", "/approve"]:
                new_bal = update_balance(100)
                response_text = f"✨ <b>تمت الموافقة يدوياً!</b>\n➕ أُضيفت 100 عملة.\n💰 الرصيد الحالي: <b>{new_bal}</b>"

            # 2. إذا أردت إضافة مبلغ محدد يدوياً (مثال: إضافة 250 أو /add 250)
            elif text.startswith("إضافة") or text.startswith("/add"):
                parts = text.split()
                if len(parts) > 1 and parts[1].isdigit():
                    amount = int(parts[1])
                    new_bal = update_balance(amount)
                    response_text = f"✅ <b>تمت الإضافة بنجاح!</b>\n➕ أُضيفت {amount} عملة.\n💰 الرصيد الحالي: <b>{new_bal}</b>"
                else:
                    response_text = "⚠️ يرجى تحديد المبلغ، مثال: <code>إضافة 150</code>"

            # 3. إذا كتبت "الرصيد" أو "/balance"
            elif text in ["الرصيد", "/balance"]:
                current_bal = get_current_balance()
                response_text = f"📊 <b>الرصيد الحالي في النظام:</b> <b>{current_bal}</b>"

            # 4. إذا كتبت "رفض"
            elif text in ["رفض", "/reject"]:
                response_text = "❌ <b>تم رفض المعاملة يدوياً.</b>"

            # 5. أمر البداية أو تعليمات الأوامر
            elif text in ["/start", "/help", "التعليمات"]:
                response_text = (
                    "<b>مرحباً بك في نظام إدارة الرصيد اليدوي!</b>\n\n"
                    "يمكنك التحكم واكتساب العملات عبر كتابة النص المباشر للبوت:\n"
                    "• اكتب <code>موافقة</code> أو <code>+100</code> لإضافة 100 عملة فوراً.\n"
                    "• اكتب <code>إضافة 500</code> لإضافة أي كمية تختارها.\n"
                    "• اكتب <code>الرصيد</code> للتحقق من الرصيد الحقيقي.\n"
                    "• اكتب <code>رفض</code> لتسجيل الرفض."
                )
            else:
                response_text = f"مرحباً! أرسلت: <i>{text}</i>\nلإضافة 100 عملة اكتب: <code>موافقة</code>"

            send_telegram_message(chat_id, response_text)

    except Exception as e:
        print("Error processing message:", str(e))

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
