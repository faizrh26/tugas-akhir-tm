# app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from pipeline import process_cv  

# --- Konfigurasi dasar Flask ---
app = Flask(__name__)
app.secret_key = "dev-secret-key"  # bebas, hanya untuk flash message

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Route utama: halaman upload ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "cvfile" not in request.files:
            flash("No file part in request.")
            return redirect(request.url)

        file = request.files["cvfile"]

        if file.filename == "":
            flash("Please choose a file.")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Unsupported file type. Allowed: .pdf, .docx, .txt")
            return redirect(request.url)

        # Simpan file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Jalankan pipeline proses CV
        result = process_cv(filepath)

        # Kirim hasil ke template result.html
        return render_template(
            "result.html",
            best_role=result["best_role"],
            score=result["score_result"],
            keywords=result["keywords"],
            entities=result["entities"],
            filename=filename,
        )

    return render_template("index.html")


if __name__ == "__main__":
    # Jalanin langsung: python app.py
    app.run(debug=True)
