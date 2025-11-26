// api/rates.js
// AiSend uchun jonli kurslar (open.er-api.com orqali)

export default async function handler(req, res) {
  try {
    const { from, to } = req.query;

    if (!from || !to) {
      return res.status(400).json({
        ok: false,
        error: "INVALID_PARAMS",
        message: "from va to parametrlarini yuboring (masalan: from=UZS&to=KZT).",
      });
    }

    const base = String(from).toUpperCase();
    const target = String(to).toUpperCase();

    // Bepul va ochiq API
    const url = `https://open.er-api.com/v6/latest/${base}`;

    const apiRes = await fetch(url);
    if (!apiRes.ok) {
      throw new Error(`Upstream API error: ${apiRes.status}`);
    }

    const data = await apiRes.json();

    const rate = data?.rates?.[target];

    if (typeof rate !== "number") {
      throw new Error("RATE_NOT_FOUND");
    }

    // Frontend SHUNI kutyapti: { ok: true, rate }
    return res.status(200).json({
      ok: true,
      rate,
    });
  } catch (err) {
    console.error("Rates API error:", err);
    return res.status(500).json({
      ok: false,
      error: "RATE_FETCH_FAILED",
      message: err.message,
    });
  }
}
