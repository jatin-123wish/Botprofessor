# chain_feedback.py

import statistics
from typing import List, Dict, Any, Tuple

class ChainPredictor:
    """
    🧠 Intelligent PRNG Prediction & Feedback Chain System
    Handles:
      - History + feedback chain analysis
      - Number, Big/Small, Red/Green probability calc
      - Trade advice logic
      - Learning & adaptive confidence adjustments
    """

    def __init__(self, history: List[int], feedbacks: List[bool]):
        """
        :param history: List of past 100–300 PRNG numbers (0–9)
        :param feedbacks: List of feedback booleans matching previous predictions (True=✅, False=❌)
        """
        self.history = history
        self.feedbacks = feedbacks
        self.accuracy = self._compute_accuracy()
        self.chain_data: List[Tuple[int, bool]] = list(zip(history[-len(feedbacks):], feedbacks))

    def _compute_accuracy(self) -> float:
        """Overall accuracy % from feedbacks"""
        if not self.feedbacks:
            return 0.0
        return round(100 * sum(self.feedbacks) / len(self.feedbacks), 2)

    def _chain_analysis(self) -> None:
        """STEP 1 – Chain jaisa data update & pattern detect"""
        # Example: maintain runs, recent breaks, etc.
        pass

    def _number_probabilities(self) -> Dict[int, float]:
        """STEP 2 – Har number (0–9) ki probability nikaalo"""
        freq = {i: 0 for i in range(10)}
        total = len(self.history)
        for n in self.history:
            freq[n] += 1
        # Base probabilities
        probs = {n: round(100 * freq[n] / total, 2) for n in range(10)}
        # Adjust with feedback chain (heavier weight for recent corrects/fails)
        # ... tu logic daal
        return probs

    def _bs_chance(self, probs: Dict[int, float]) -> Tuple[float, float]:
        """STEP 3 – Big/Small total % calculate"""
        big = sum(probs[n] for n in range(5, 10))
        small = sum(probs[n] for n in range(0, 5))
        return round(big, 2), round(small, 2)

    def _rg_chance(self, probs: Dict[int, float]) -> Tuple[float, float]:
        """STEP 4 – Red/Green total % calculate"""
        red = sum(probs[n] for n in [0,2,4,6,8])
        green = sum(probs[n] for n in [1,3,5,7,9])
        return round(red, 2), round(green, 2)

    def _trade_tier(self, pct: float) -> str:
        """DECIDE Trade Tier label based on %"""
        if pct < 70:
            return "⚠️ Danger Zone – Skip Trade"
        if pct < 75:
            return "👍 Good Trade Opportunity"
        if pct < 80:
            return "🚀 Best Trade – Strong Signal"
        if pct < 85:
            return "🎯 Sniper Trade – High Precision"
        if pct < 90:
            return "🔥 High-Probability Trade"
        return "💣 Killer Trade – Ultra-High Confidence"

    def predict(self) -> Dict[str, Any]:
        """
        Full pipeline:
          - Chain analysis
          - Number & group probabilities
          - Top-3 numbers + Killer
          - Big/Small & Red/Green chances + suggestions
          - Final confidence & risk tier
          - Learning log summary
        """
        # 1️⃣ Chain Analysis
        self._chain_analysis()

        # 2️⃣ Number probabilities
        probs = self._number_probabilities()
        top3 = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]
        killer_num, killer_conf = top3[0]

        # 3️⃣ Big/Small
        big_pct, small_pct = self._bs_chance(probs)
        bs_sugg = "Big" if big_pct > small_pct else "Small"
        bs_conf = max(big_pct, small_pct)

        # 4️⃣ Red/Green
        red_pct, green_pct = self._rg_chance(probs)
        rg_sugg = "Red" if red_pct > green_pct else "Green"
        rg_conf = max(red_pct, green_pct)

        # 5️⃣ Final confidence (example avg of top3)
        final_conf = round(statistics.mean([p for _, p in top3]), 2)
        trade_tier = self._trade_tier(final_conf)

        # 6️⃣ Learning Log
        last_num, last_fb = (self.chain_data[-1] if self.chain_data else (None, None))
        learning_enabled = bool(self.feedbacks)

        # Assemble output
        return {
            "history_length": len(self.history),
            "feedback_count": len(self.feedbacks),
            "accuracy_score": self.accuracy,
            "top3": top3,
            "killer": (killer_num, killer_conf),
            "big_small": {"Big": big_pct, "Small": small_pct, "suggestion": bs_sugg, "confidence": bs_conf},
            "red_green": {"Red": red_pct, "Green": green_pct, "suggestion": rg_sugg, "confidence": rg_conf},
            "final_confidence": final_conf,
            "trade_tier": trade_tier,
            "last_prediction": last_num,
            "last_feedback": "✅" if last_fb else "❌",
            "learning_enabled": learning_enabled,
        }

    def format_output(self, results: Dict[str, Any]) -> str:
        """📤 OUTPUT FORMAT string bana ke return karega"""
        top3 = results["top3"]
        killer = results["killer"]
        bs = results["big_small"]
        rg = results["red_green"]

        msg = f"""
🔁 Round Analysis: #{len(self.history)}
🧠 Feedback Learning Enabled: {'✅' if results['learning_enabled'] else '❌'}
📦 Data Used:
- History Length: {results['history_length']}
- Feedback Count: {results['feedback_count']}
- Accuracy So Far: {results['accuracy_score']}%

📊 Number Prediction:
🎯 Top 3 Probable:
1️⃣ {top3[0][0]} → {top3[0][1]}%
2️⃣ {top3[1][0]} → {top3[1][1]}%
3️⃣ {top3[2][0]} → {top3[2][1]}%
🔥 Killer Prediction: {killer[0]} ({killer[1]}% Confidence)

📈 Big/Small Prediction:
- Big Chance: {bs['Big']}% → {self._trade_tier(bs['Big'])}
- Small Chance: {bs['Small']}% → {self._trade_tier(bs['Small'])}
📌 Suggested: {bs['suggestion']} → Confidence: {bs['confidence']}%

📉 Red/Green Prediction:
- Red Chance: {rg['Red']}% → {self._trade_tier(rg['Red'])}
- Green Chance: {rg['Green']}% → {self._trade_tier(rg['Green'])}
📌 Suggested: {rg['suggestion']} → Confidence: {rg['confidence']}%

🔐 Final Advice:
{bs['suggestion']} + {rg['suggestion']} pe trade karo ✌️
"""
        return msg.strip()
