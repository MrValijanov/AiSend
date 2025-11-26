// api/rates.js
// USD bazasi orqali istalgan FROM -> TO kursini hisoblaymiz

export default async function handler(req, res) {
  const { from, to } = req.query;

  if (!from || !to) {
    return res.status(400).json({
      ok: false,
      error: "from va to parametrlarini yuboring"
    });
  }

  const base = from.toUpperCase();
  const targets = to
    .split(",")
    .map((t) => t.trim().toUpperCase())
    .filter((t) => t && t !== base);

  try {
    // 1 USD ga nisbatan hamma kurslar
    const apiRes = await fetch("https://open.er-api.com/v6/latest/USD");
    if (!apiRes.ok) {
      throw new Error("Upstream API HTTP error");
    }

    const data = await apiRes.json();

    if (data.result !== "success" || !data.rates) {
      throw new Error(data["error-type"] || "Upstream API response error");
    }

    const usdRates = data.rates;

    if (!usdRates[base]) {
      return res.status(400).json({
        ok: false,
        error: `Valyuta qo'llab-quvvatlanmaydi: ${base}`
      });
    }

    const resultRates = {};

    // Formula: rate(FROM -> TO) = rate(USD->TO) / rate(USD->FROM)
    for (const t of targets) {
      if (!usdRates[t]) continue;
      const rate = usdRates[t] / usdRates[base];
      resultRates[t] = rate;
    }

    if (Object.keys(resultRates).length === 0) {
      return res.status(400).json({
        ok: false,
        error: "So'ralgan yo'nalishlar uchun kurs topilmadi"
      });
    }

    return res.status(200).json({
      ok: true,
      base,
      rates: resultRates
    });
  } catch (err) {
    console.error("Rates API error:", err);
    return res.status(500).json({
      ok: false,
      error: "Server xatosi yoki tashqi API muammosi",
      details: err.message
    });
  }
}
