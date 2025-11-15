from flask import Flask, request, render_template, send_file
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import os

app = Flask(__name__)

# إنشاء مجلد التقارير لو مو موجود
if not os.path.exists("reports"):
    os.makedirs("reports")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan():
    url = request.form.get("url")

    # جلب HTML من الموقع
    try:
        r = requests.get(url, timeout=10)
        html = r.text
    except:
        return {"error": "فشل الوصول للموقع"}, 400

    soup = BeautifulSoup(html, "html.parser")

    # استخراج السكربتات
    scripts = [s.get("src") for s in soup.find_all("script") if s.get("src")]

    # فحص التتبع
    known = ["google", "facebook", "meta", "hotjar", "tiktok", "doubleclick"]
    trackers = [s for s in scripts if any(k in s.lower() for k in known)]

    # حساب درجة الخصوصية
    score = max(10, 100 - len(trackers) * 15)

    # إنشاء PDF
    pdf_path = "reports/report.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "Privacy Report", ln=1)
    pdf.cell(0, 10, f"Website: {url}", ln=1)
    pdf.cell(0, 10, f"Privacy Score: {score}", ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, "Trackers Detected:", ln=1)

    for t in trackers:
        pdf.multi_cell(0, 8, f"- {t}")

    pdf.output(pdf_path)

    return {
        "url": url,
        "privacy_score": score,
        "scripts_found": len(scripts),
        "trackers": trackers,
        "pdf": "/download"
    }

@app.route("/download")
def download():
    return send_file("reports/report.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
