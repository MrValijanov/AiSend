// api/rates.js
export default async function handler(req, res) {
  const { from, to } = req.query;

  if (!from || !to) {
    return res.status(400).json({
      ok: false,
      error: "from va to parametrlarini yuboring"
    });
  }

  const base = from.toUpperCase();
  const targets = to.split(",").map(t => t.trim().toUpperCase());

  try {
    // 1️⃣ API dan base valyutaga asoslangan kurslar
    const api1 = `https://open.er-api.com/v6/latest/${base}`;
    const r1 = await fetch(api1);
    const d1 = await r1.json();

    if (d1.result === "error") {
      throw new Error(d1["error-type"] || "API 1 error");
    }

    let rates = {};

    // 2️⃣ Agar to valyuta d1.rates da bo'lsa — to‘g‘ridan-to‘g‘ri ishlatamiz
    for (const t of targets) {
      if (d1.rates[t]) {
        rates[t] = d1.rates[t];
      }
    }

    // 3️⃣ Agar KGS yo‘q bo‘lsa — USD orqali hisoblaymiz
    if (targets.includes("KGS") && !rates["KGS"]) {
      const api2 = `https://open.er-api.com/v6/latest/USD`;
      const r2 = await fetch(api2);
      const d2 = await r2.json();

      if (d2.result !== "success") {
        throw new Error("API USD error");
      }

      // UZS → USD → KGS formulasi
      if (d1.rates["USD"] && d2.rates["KGS"]) {
        const uzsToUsd = d1.rates["USD"];
        const usdToKgs = d2.rates["KGS"];
        rates["KGS"] = uzsToUsd * usdToKgs;
      }
    }

    return res.status(200).json({
      ok: true,
      base,
      rates
    });

  } catch (err) {
    return res.status(500).json({
      ok: false,
      error: err.message
    });
  }
}
