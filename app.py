from flask import (
    Flask,
    send_from_directory,
    jsonify,
    request,
    redirect,
    url_for,
    render_template_string,
    session,
)
import requests

app = Flask(__name__)

# !!! Muhim: bu yerga o'zing xohlagan random sirli matn yozib qo'yishingiz mumkin
app.secret_key = "aisend_super_secret_key_123"

# Admin paroli (xohlasang o'zgartir): /admin ga kirish uchun
ADMIN_PASSWORD = "aisend123"

# Marjalar (foyda) foiz ko'rinishida emas, nisbiy: 0.01 = 1%
margin_kzt = 0.01  # 1% foyda
margin_kgs = 0.01  # 1% foyda


def get_raw_rates():
    """
    Bozor kurslarini API'dan olib kelamiz (marjasiz).
    """
    kzt_api = "https://api.exchangerate-api.com/v4/latest/KZT"
    kgs_api = "https://api.exchangerate-api.com/v4/latest/KGS"

    kzt_data = requests.get(kzt_api).json()
    kgs_data = requests.get(kgs_api).json()

    kzt_to_uzs = kzt_data["rates"]["UZS"]
    kgs_to_uzs = kgs_data["rates"]["UZS"]

    return kzt_to_uzs, kgs_to_uzs


def get_rates():
    """
    Aisend uchun kurslar: bozor kursi + marja.
    Frontend faqat shuni ishlatadi.
    """
    global margin_kzt, margin_kgs

    kzt_to_uzs_raw, kgs_to_uzs_raw = get_raw_rates()

    kzt_to_uzs = kzt_to_uzs_raw * (1 + margin_kzt)
    kgs_to_uzs = kgs_to_uzs_raw * (1 + margin_kgs)

    return {
        "KZT_UZS": kzt_to_uzs,
        "KGS_UZS": kgs_to_uzs,
        "KZT_RAW": kzt_to_uzs_raw,
        "KGS_RAW": kgs_to_uzs_raw,
        "MARGIN_KZT": margin_kzt,
        "MARGIN_KGS": margin_kgs,
    }


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/api/rates")
def rates():
    """
    Frontend shu endpointdan Aisend kurslarini oladi.
    """
    data = get_rates()
    # faqat kerakli qismini qaytaramiz
    return jsonify(
        {
            "KZT_UZS": data["KZT_UZS"],
            "KGS_UZS": data["KGS_UZS"],
        }
    )


# --- ADMIN PANEL --- #

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
  <meta charset="UTF-8">
  <title>Aisend Admin</title>
  <style>
    body {
      font-family: system-ui, sans-serif;
      background: #0f172a;
      color: #e5e7eb;
      padding: 20px;
    }
    .card {
      background: #111827;
      padding: 20px;
      border-radius: 16px;
      max-width: 420px;
      margin: 0 auto;
      box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }
    input {
      width: 100%;
      padding: 10px;
      border-radius: 10px;
      border: none;
      margin-top: 8px;
      margin-bottom: 12px;
      font-size: 14px;
    }
    button {
      padding: 10px 16px;
      border-radius: 999px;
      border: none;
      background: #4f46e5;
      color: white;
      font-weight: 600;
      cursor: pointer;
    }
    button:hover {
      background: #6366f1;
    }
    .label {
      font-size: 13px;
      opacity: 0.9;
    }
    .error {
      color: #f97373;
      font-size: 13px;
    }
    .small {
      font-size: 12px;
      opacity: 0.8;
    }
  </style>
</head>
<body>
  <div class="card">
    {% if not logged_in %}
      <h2>Aisend Admin — Kirish</h2>
      <form method="post">
        <div class="label">Parol:</div>
        <input type="password" name="password" placeholder="Admin parol">
        {% if error %}
          <div class="error">{{ error }}</div>
        {% endif %}
        <button type="submit">Kirish</button>
      </form>
      <p class="small">Default parol: <b>aisend123</b> (app.py ichidan o'zgartirishingiz mumkin)</p>
    {% else %}
      <h2>Aisend Admin — Marja sozlamalari</h2>
      <p class="small">
        Bozor kursi (taxminiy):<br>
        1 KZT ≈ {{ kzt_raw }} UZS<br>
        1 KGS ≈ {{ kgs_raw }} UZS
      </p>
      <p class="small">
        Hozirgi Aisend marjasi:<br>
        KZT: {{ (margin_kzt * 100) | round(2) }}%<br>
        KGS: {{ (margin_kgs * 100) | round(2) }}%
      </p>
      <form method="post" action="{{ url_for('update_margin') }}">
        <div class="label">KZT marja (%)</div>
        <input type="number" step="0.01" name="margin_kzt" value="{{ (margin_kzt * 100) | round(2) }}">
        <div class="label">KGS marja (%)</div>
        <input type="number" step="0.01" name="margin_kgs" value="{{ (margin_kgs * 100) | round(2) }}">
        <button type="submit">Saqlash</button>
      </form>
      <form method="post" action="{{ url_for('admin_logout') }}" style="margin-top:10px;">
        <button type="submit" style="background:#6b7280;">Chiqish</button>
      </form>
      <p class="small">
        Diqqat: Ushbu marja foydalanuvchiga ko'rinadigan kurslarga avtomatik qo'llanadi.
      </p>
    {% endif %}
  </div>
</body>
</html>
"""


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """
    /admin — parol bilan kiriladigan sahifa.
    """
    global margin_kzt, margin_kgs

    if request.method == "POST" and not session.get("logged_in"):
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin"))
        else:
            return render_template_string(
                ADMIN_TEMPLATE,
                logged_in=False,
                error="Noto'g'ri parol",
            )

    if not session.get("logged_in"):
        return render_template_string(
            ADMIN_TEMPLATE,
            logged_in=False,
            error=None,
        )

    # logged_in bo'lsa:
    try:
        kzt_raw, kgs_raw = get_raw_rates()
    except Exception:
        kzt_raw, kgs_raw = 0, 0

    return render_template_string(
        ADMIN_TEMPLATE,
        logged_in=True,
        margin_kzt=margin_kzt,
        margin_kgs=margin_kgs,
        kzt_raw=kzt_raw,
        kgs_raw=kgs_raw,
    )


@app.route("/admin/margin", methods=["POST"])
def update_margin():
    global margin_kzt, margin_kgs

    if not session.get("logged_in"):
        return redirect(url_for("admin"))

    try:
        mkzt = float(request.form.get("margin_kzt", "1")) / 100.0
        mkgs = float(request.form.get("margin_kgs", "1")) / 100.0
        margin_kzt = mkzt
        margin_kgs = mkgs
    except ValueError:
        pass

    return redirect(url_for("admin"))


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
