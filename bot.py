@app.route("/", methods=["POST"])
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    print("Received update:", update)  # طباعة البيانات في السجلات للمتابعة

    if not update:
        return "OK", 200

    if "callback_query" in update:
        callback = update["callback_query"]
        callback_data = callback.get("data")
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]

        if callback_data == "approve_100_coins":
            new_bal = update_balance(100)
            answer_text = f"✨ تمت العملية بنجاح! إضافة 100 عملة. الرصيد الحالي: {new_bal}"
        elif callback_data == "reject_order":
            answer_text = "❌ تم رفض المعاملة."
        else:
            answer_text = "⚠️ إجراء غير معروف."

        # إيقاف دائرة التحميل للزر
        requests.post(
            f"https://api.telegram.org/bot8989095746:AAHOl9g15Yt-n8x9R0YgZEPdjhsZjhsKLw8/answerCallbackQuery",
            json={"callback_query_id": callback.get("id"), "text": answer_text}
        )

        # تحديث نص الرسالة
        original_caption = callback["message"].get("caption", "")
        updated_caption = original_caption + f"\n\n<b>[تمت المعاملة بواسطة الإدارة]</b>"

        edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageCaption"
        requests.post(edit_url, json={
            "chat_id": chat_id,
            "message_id": message_id,
            "caption": updated_caption,
            "parse_mode": "HTML"
        })

    return "OK", 200
