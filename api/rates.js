// api/rates.js

// Vercel serverless function: /api/rates
// Foydalanish: /api/rates?from=UZS&to=KZT

export default async function handler(req, res) {
  const { from = "UZS", to = "KZT" } = req.query;

  const base = String(from).toUpperCase();
  const target = String(to).toUpperCase();

  try {
    // Exchangerate.host – bepul API, auth shart emas
    const url = `https://api.exchangerate.host/latest?base=${base}&symbols=${target}`;

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error("Third-party API error");
    }

    const data = await response.json();
    const rate = data?.rates?.[target];

    if (!rate) {
      throw new Error("Rate not found");
    }

    return res.status(200).json({
      ok: true,
      base,
      target,
      rate,
      provider: "exchangerate.host",
      date: data.date,
    });
  } catch (err) {
    console.error("RATE API ERROR:", err);
    return res.status(500).json({
      ok: false,
      error: "RATE_FETCH_FAILED",
      message: "Could not load live rates",
    });
  }
}
