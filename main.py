@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_message(message):
    text = message.text.strip().lower()
    chat_id = message.chat.id

    # START–END history input
    if text.startswith("start") and text.endswith("end"):
        try:
            nums = list(map(int, text.split()[1:-1]))
        except ValueError:
            bot.reply_to(message, "❌ Sirf numbers do: `start 2 3 4 … end`", parse_mode="Markdown")
            return

        # Save user history
        user_data[chat_id] = {
            "history": nums,
            "feedback": [],
        }

        bot.reply_to(message, f"✅ {len(nums)} numbers store ho gaye!\nAb har prediction ke baad mujhe sirf ek number bhejna (feedback)", parse_mode="Markdown")
        return

    # Single Number Feedback (e.g., 5)
    if text.isdigit() and chat_id in user_data:
        feedback_num = int(text)
        data = user_data[chat_id]
        history = data["history"]
        feedback = data["feedback"]

        # Update history
        history.append(feedback_num)
        feedback.append(feedback_num)

        # 🔮 ANALYSIS START
        counts = {i: 0 for i in range(10)}
        for n in history:
            counts[n] += 1
        total = sum(counts.values())
        probs = {n: round((c / total) * 100, 2) for n, c in counts.items()}
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)

        # 🎯 Top number predictions
        top3 = sorted_probs[:3]
        top_number, top_conf = top3[0]

        # 📈 Big/Small
        big_chance = sum(probs[n] for n in range(5, 10))
        small_chance = sum(probs[n] for n in range(0, 5))
        bs_suggestion = "Big" if big_chance > small_chance else "Small"
        bs_conf = max(big_chance, small_chance)

        # 📉 Red/Green
        red_chance = sum(probs[n] for n in [0,2,4,6,8])
        green_chance = sum(probs[n] for n in [1,3,5,7,9])
        rg_suggestion = "Red" if red_chance > green_chance else "Green"
        rg_conf = max(red_chance, green_chance)

        # 🎯 Final Tier
        if top_conf >= 90:
            tier = "💣 Killer Trade"
        elif top_conf >= 85:
            tier = "🔥 High Probability"
        elif top_conf >= 80:
            tier = "🎯 Sniper Entry"
        elif top_conf >= 75:
            tier = "🚀 Best Trade"
        elif top_conf >= 70:
            tier = "👍 Good Trade"
        else:
            tier = "⚠️ Danger – Avoid"

        msg = (
            f"🔮 *Next Market Prediction*\n"
            f"📦 Total Data: {len(history)} numbers\n"
            f"✅ Feedbacks: {len(feedback)}\n\n"

            f"🎯 *Top Probable Numbers:*\n"
            f"1️⃣ {top3[0][0]} → {top3[0][1]}%\n"
            f"2️⃣ {top3[1][0]} → {top3[1][1]}%\n"
            f"3️⃣ {top3[2][0]} → {top3[2][1]}%\n\n"

            f"📈 *Big/Small:* {bs_suggestion} ({bs_conf}%)\n"
            f"📉 *Red/Green:* {rg_suggestion} ({rg_conf}%)\n\n"

            f"🧠 *Trade Suggestion:* {tier}"
        )
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❓ Pehle history do: `start 2 3 4 … end`\nPhir feedback ke liye sirf ek number bhejna.", parse_mode="Markdown")
