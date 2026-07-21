"""
Website Listing Desa Maor — clone fungsional
Backend: Python (Flask) + SQLite
Frontend: Jinja2 + CSS custom (lihat static/css/style.css)
"""
import os
import sqlite3
import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from flask import Flask, render_template, jsonify, request, g, redirect, url_for, session
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
# Nama database disesuaikan untuk Desa Maor
DB_PATH = BASE_DIR / "maor.db"

app = Flask(__name__)

# Kunci rahasia untuk sistem login
app.secret_key = "kunci_rahasia_maor_2026"

# Pengaturan folder untuk menyimpan foto berita
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Mengatur Zona Waktu ke WIB agar perpindahan hari sesuai waktu setempat
Waktu_Lokal = ZoneInfo("Asia/Jakarta")

DESA = {
    "nama": "Desa Maor",
    "kecamatan": "Kecamatan Kembangbahu",
    "kabupaten": "Kabupaten Lamongan",
    "provinsi": "Provinsi Jawa Timur",
    "kode_wilayah": "35.24.19.2009", 
    "kode_pos": "62282",
    "alamat": "Jl. Raya Kembangbahu No.17, Maor, Kec. Kembangbahu, Kabupaten Lamongan",
    "telepon": "081234567890", # Placeholder - sesuaikan jika ada data valid
    "email": "desa.maor@gmail.com",
    "jam_layanan": "Senin – Kamis (08.00–15.00) & Jumat (08.00–11.00)",
    "sosial": {
        "facebook": "https://facebook.com/DesaMaor",
        "instagram": "https://instagram.com/DesaMaor",
        "twitter": "https://twitter.com/PemdesMaor",
        "youtube": "https://youtube.com/DesaMaor",
        "tiktok": "https://tiktok.com/@DesaMaor",
    },
    # Koordinat pusat Desa Maor, Kembangbahu, Lamongan
    "peta_pusat": {"lat": -7.2024, "lng": 112.3505, "zoom": 15},
    
    # --- DATA VISI & MISI DITAMBAHKAN DI SINI ---
    "visi": "“MENJADIKAN DESA MAOR SEMAKIN MAJU, BERKUALITAS, AMAN DAN MENUJU DESA GEMAH RIPAH LOH JINAWI SERTA BERMARTABAT”",
    "misi": [
        "Menata Aparatur Pemerintahan Desa  Maor  Kecamatan  Kembangbahu Kabupaten Lamongan sehingga dapat melaksanakan tugas sesuai dengan tugas pokok dan fungsinya masing-masing",
        "Membina dan menciptakan kerukunan masyarakat Desa  Maor Kecamatan  Kembangbahu  Kabupaten Lamongan secara netral dan mandiri",
        "Meningkatkan peran serta pemuda dan remaja dibidang pembangunan, olahraga, seni/kebudayaan dan kemasyarakatan",
        "Meningkatkan dan memotifasi kegamaan terutama kegiatan muslimat desa  Maor, dan",
        "Meningkatkan sarana dan prasarana umum sesuai dengan aspirasi masyarakat yang dituangkan dalam dokumen Rencana Pembangunan Jangka Menengah Desa (RPJM Desa)."
        ],
    "struktur": [
        {"jabatan": "Kepala Desa", "nama": "Nama Kepala Desa"},
        {"jabatan": "Sekretaris Desa", "nama": "Nama Sekdes"},
        {"jabatan": "Kaur Keuangan", "nama": "Nama"},],
}


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    
    # JURUS PAMUNGKAS: Hapus tabel 'poi' lama dan buat ulang dari nol
    conn.executescript(
        """
        DROP TABLE IF EXISTS poi;
        
        CREATE TABLE poi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            kategori TEXT NOT NULL,
            deskripsi TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS kunjungan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL UNIQUE,
            jumlah INTEGER NOT NULL DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS berita (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT NOT NULL,
            tanggal TEXT NOT NULL,
            ringkasan TEXT NOT NULL,
            isi TEXT NOT NULL,
            gambar TEXT
        );
        """
    )
    conn.commit()
    # Hapus data berita lama agar tidak menumpuk saat reset
    conn.execute("DELETE FROM berita")
    
    # Seeding data contoh Berita
    seed_berita = [
        ("Kerja Bakti Bersihkan Embung Desa", "17 Juli 2026", 
         "Warga Desa Maor bergotong royong membersihkan area embung untuk persiapan musim kemarau.", 
         "Isi berita lengkap di sini...", "default.jpg"),
        ("Penyaluran Bantuan Bibit Padi", "15 Juli 2026", 
         "Pemerintah Desa Maor menyalurkan bantuan bibit padi unggul kepada kelompok tani.", 
         "Isi berita lengkap di sini...", "default.jpg"),
        ("Posyandu Balita Bulan Juli Berjalan Lancar", "10 Juli 2026", 
         "Kegiatan posyandu rutin bulan ini dihadiri oleh puluhan balita dan ibu hamil di Polindes.", 
         "Isi berita lengkap di sini...", "default.jpg")
    ]
    conn.executemany(
        "INSERT INTO berita (judul, tanggal, ringkasan, isi, gambar) VALUES (?,?,?,?,?)",
        seed_berita,
    )
    conn.commit()

    # Masukkan data (pasti dieksekusi karena tabel baru saja di-reset)
    seed_poi = [
        ("Kantor Kepala Desa Maor", "Pemerintahan",
         "Pusat pelayanan administrasi dan pemerintahan Desa Maor.",
         -7.204406966500724, 112.35340342229905),
        ("Masjid Desa' Maor", "Peribadatan",
         "Masjid utama yang menjadi pusat kegiatan keagamaan warga setempat.",
         -7.205148801479981, 112.35316240013985),
        ("MI Maor", "Pendidikan",
         "Madrasah Ibtidaiyah yang melayani pendidikan dasar agama anak-anak.",
         -7.205347319005749, 112.35317659401258),
        ("SD Negeri Maor", "Pendidikan",
         "Sekolah dasar negeri yang memfasilitasi belajar mengajar usia dini di desa.",
         -7.204453077046238, 112.35311269110177),
        ("Embung Desa", "Pengairan",
         "Sumber penampungan air untuk irigasi persawahan, khususnya saat musim kemarau.",
         -7.208761992401299, 112.3494784965776),
        ("Polindes Desa Maor", "Kesehatan",
         "Fasilitas pondok bersalin dan layanan kesehatan dasar desa.",
         -7.204192253274142, 112.35324059733296),
        ("Tour And Travel Mujahidin", "Usaha Warga",
         "Biro perjalanan dan layanan transportasi milik warga desa.",
         -7.204244921639009, 112.35318431873094)
    ]
    
    conn.executemany(
        "INSERT INTO poi (nama, kategori, deskripsi, lat, lng) VALUES (?,?,?,?,?)",
        seed_poi,
    )
    conn.commit()
    conn.close()


def catat_kunjungan():
    """Tambah 1 kunjungan untuk hari ini sesuai waktu setempat (WIB)."""
    today = datetime.datetime.now(Waktu_Lokal).date().isoformat()
    db = get_db()
    db.execute(
        """INSERT INTO kunjungan (tanggal, jumlah) VALUES (?, 1)
           ON CONFLICT(tanggal) DO UPDATE SET jumlah = jumlah + 1""",
        (today,),
    )
    db.commit()


def hitung_statistik():
    db = get_db()
    today = datetime.datetime.now(Waktu_Lokal).date()

    def jumlah_pada(tanggal):
        row = db.execute(
            "SELECT jumlah FROM kunjungan WHERE tanggal = ?", (tanggal.isoformat(),)
        ).fetchone()
        return row["jumlah"] if row else 0

    def jumlah_rentang(start, end):
        row = db.execute(
            "SELECT COALESCE(SUM(jumlah),0) AS total FROM kunjungan WHERE tanggal BETWEEN ? AND ?",
            (start.isoformat(), end.isoformat()),
        ).fetchone()
        return row["total"]

    minggu_ini_mulai = today - datetime.timedelta(days=today.weekday())
    minggu_lalu_mulai = minggu_ini_mulai - datetime.timedelta(days=7)
    minggu_lalu_akhir = minggu_ini_mulai - datetime.timedelta(days=1)
    bulan_ini_mulai = today.replace(day=1)
    bulan_lalu_akhir = bulan_ini_mulai - datetime.timedelta(days=1)
    bulan_lalu_mulai = bulan_lalu_akhir.replace(day=1)

    total_row = db.execute("SELECT COALESCE(SUM(jumlah),0) AS total FROM kunjungan").fetchone()

    return {
        "hari_ini": jumlah_pada(today),
        "kemarin": jumlah_pada(today - datetime.timedelta(days=1)),
        "minggu_ini": jumlah_rentang(minggu_ini_mulai, today),
        "minggu_lalu": jumlah_rentang(minggu_lalu_mulai, minggu_lalu_akhir),
        "bulan_ini": jumlah_rentang(bulan_ini_mulai, today),
        "bulan_lalu": jumlah_rentang(bulan_lalu_mulai, bulan_lalu_akhir),
        "total": total_row["total"],
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    # Langsung diarahkan ke routing listing agar kunjungan tercatat
    return redirect(url_for("listing"))


@app.route("/listing")
def listing():
    catat_kunjungan()
    stats = hitung_statistik()
    
    db = get_db()
    # Pastikan tabel agenda ada
    db.execute('CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, judul TEXT, tanggal TEXT, waktu TEXT, lokasi TEXT)')
    db.commit()
    
    # Ambil data agenda, urutkan dari tanggal terdekat
    agenda_raw = db.execute("SELECT * FROM agenda ORDER BY tanggal ASC").fetchall()
    
    # Proses konversi format tanggal (Misal: 2026-08-17 menjadi "17" dan "Agu")
    daftar_agenda = []
    bulan_indo = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    
    for a in agenda_raw:
        try:
            dt = datetime.datetime.strptime(a["tanggal"], "%Y-%m-%d")
            tgl_angka = dt.strftime("%d")
            bln_teks = bulan_indo[dt.month - 1]
        except:
            tgl_angka = "--"
            bln_teks = "--"
            
        daftar_agenda.append({
            "judul": a["judul"],
            "waktu": a["waktu"],
            "lokasi": a["lokasi"],
            "tgl_angka": tgl_angka,
            "bln_teks": bln_teks
        })
        
    return render_template("listing.html", desa=DESA, stats=stats, agenda=daftar_agenda)

# --- RUTE BARU UNTUK HALAMAN PROFIL (TERPISAH) ---
@app.route("/profil")
def profil():
    return render_template("profil.html", desa=DESA)

# --- RUTE UNTUK HALAMAN STRUKTUR ORGANISASI ---
@app.route("/struktur")
def struktur():
    return render_template("struktur.html", desa=DESA)

@app.route("/berita")
def berita():
    db = get_db()
    # Mengambil berita dari database, diurutkan dari yang terbaru (ID terbesar)
    daftar_berita = db.execute("SELECT * FROM berita ORDER BY id DESC").fetchall()
    return render_template("berita.html", desa=DESA, berita=daftar_berita)

@app.route("/api/poi")
def api_poi():
    db = get_db()
    rows = db.execute("SELECT * FROM poi ORDER BY id").fetchall()
    
    # Kategori warna disesuaikan dengan geografi wilayah pertanian
    kategori_warna = {
        "Pemerintahan": "#c0572a",
        "Pertanian": "#4caf50",    # Hijau untuk area persawahan
        "Pengairan": "#2196f3",    # Biru untuk waduk/embung
        "Peribadatan": "#8a6d3b",
        "Pendidikan": "#3f6fa8",
        "Kesehatan": "#a4383a",
    }
    
    data = []
    for r in rows:
        data.append(
            {
                "id": r["id"],
                "nama": r["nama"],
                "kategori": r["kategori"],
                "deskripsi": r["deskripsi"],
                "lat": r["lat"],
                "lng": r["lng"],
                "warna": kategori_warna.get(r["kategori"], "#607d8b"), # Default warna Abu-abu kebiruan
            }
        )
    return jsonify({"pusat": DESA["peta_pusat"], "titik": data})


@app.route("/api/poi", methods=["POST"])
def api_poi_create():
    """Tambah titik lokasi baru (dipakai oleh admin/panel input)."""
    # Proteksi ringan agar endpoint tidak di-spam sembarang orang
    if request.headers.get("X-API-KEY") != "admin_maor_2026":
        return jsonify({"error": "Akses ditolak. Header X-API-KEY tidak valid."}), 401

    payload = request.get_json(force=True, silent=True) or {}
    required = ["nama", "kategori", "deskripsi", "lat", "lng"]
    if not all(k in payload for k in required):
        return jsonify({"error": "Field wajib: " + ", ".join(required)}), 400
    
    db = get_db()
    cur = db.execute(
        "INSERT INTO poi (nama, kategori, deskripsi, lat, lng) VALUES (?,?,?,?,?)",
        (payload["nama"], payload["kategori"], payload["deskripsi"],
         float(payload["lat"]), float(payload["lng"])),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid, "status": "tersimpan"}), 201


@app.route("/api/stats")
def api_stats():
    return jsonify(hitung_statistik())

# --- SISTEM ADMIN BERITA ---
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        # Password rahasianya adalah: adminmaor123
        if password == "adminmaor123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("login.html", desa=DESA, error="Password Salah!")
    return render_template("login.html", desa=DESA)

@app.route("/admin/dashboard", methods=["GET", "POST"])
def admin_dashboard():
    # Cek apakah sudah login
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    
    if request.method == "POST":
        jenis_form = request.form.get("jenis_form")
        db = get_db()
        
        # JIKA YANG DIKIRIM ADALAH FORM BERITA
        if jenis_form == "berita":
            judul = request.form.get("judul")
            ringkasan = request.form.get("ringkasan")
            isi = request.form.get("isi")
            gambar = request.files.get("gambar")
            
            tanggal = datetime.datetime.now(Waktu_Lokal).strftime("%d %B %Y")
            filename = "default.jpg"

            if gambar and gambar.filename:
                filename = secure_filename(gambar.filename)
                gambar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            db.execute(
                "INSERT INTO berita (judul, tanggal, ringkasan, isi, gambar) VALUES (?,?,?,?,?)",
                (judul, tanggal, ringkasan, isi, filename)
            )
            db.commit()
            return redirect(url_for("berita"))
            
        # JIKA YANG DIKIRIM ADALAH FORM TITIK PETA (POI)
        elif jenis_form == "poi":
            nama = request.form.get("nama")
            kategori = request.form.get("kategori")
            deskripsi = request.form.get("deskripsi")
            lat = request.form.get("lat")
            lng = request.form.get("lng")
            
            db.execute(
                "INSERT INTO poi (nama, kategori, deskripsi, lat, lng) VALUES (?,?,?,?,?)",
                (nama, kategori, deskripsi, float(lat), float(lng))
            )
            db.commit()
            return redirect(url_for("peta")) # <-- UBAH KE "peta" DI SINI
        
        # JIKA YANG DIKIRIM ADALAH FORM INFOGRAFIS
        elif jenis_form == "infografis":
            judul = request.form.get("judul")
            gambar = request.files.get("gambar")
            tanggal = datetime.datetime.now(Waktu_Lokal).strftime("%d %B %Y")
            
            filename = "default.jpg"
            if gambar and gambar.filename:
                filename = secure_filename(gambar.filename)
                gambar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            db.execute(
                "INSERT INTO infografis (judul, gambar, tanggal) VALUES (?,?,?)",
                (judul, filename, tanggal)
            )
            db.commit()
            return redirect(url_for("infografis")) # Arahkan ke halaman infografis setelah sukses
       
        # JIKA YANG DIKIRIM ADALAH FORM AGENDA KEGIATAN
        elif jenis_form == "agenda":
            judul = request.form.get("judul")
            tanggal = request.form.get("tanggal")
            waktu = request.form.get("waktu")
            lokasi = request.form.get("lokasi")
            
            db.execute('CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, judul TEXT, tanggal TEXT, waktu TEXT, lokasi TEXT)')
            db.execute(
                "INSERT INTO agenda (judul, tanggal, waktu, lokasi) VALUES (?,?,?,?)",
                (judul, tanggal, waktu, lokasi)
            )
            db.commit()
            return redirect(url_for("listing"))
            
    return render_template("admin.html", desa=DESA)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


@app.route("/berita/<int:id_berita>")
def berita_detail(id_berita):
    db = get_db()
    # Mengambil 1 berita spesifik berdasarkan ID yang diklik
    item = db.execute("SELECT * FROM berita WHERE id = ?", (id_berita,)).fetchone()
    
    if item is None:
        return "Berita tidak ditemukan", 404
        
    return render_template("berita_detail.html", desa=DESA, item=item)

@app.route("/infografis")
def infografis():
    db = get_db()
    
    # --- TAMBAHKAN DUA BARIS INI (Memaksa Flask membuat tabel jika belum ada) ---
    db.execute('CREATE TABLE IF NOT EXISTS infografis (id INTEGER PRIMARY KEY AUTOINCREMENT, judul TEXT, gambar TEXT, tanggal TEXT)')
    db.commit()
    # -------------------------------------------------------------------------
    
    # Mengambil semua data infografis dari terbaru ke terlama
    data_infografis = db.execute("SELECT * FROM infografis ORDER BY id DESC").fetchall()
    return render_template("infografis.html", desa=DESA, infografis=data_infografis)

@app.route("/peta")
def peta():
    db = get_db()
    # Mengambil data titik peta (POI) jika diperlukan di halaman peta
    poi_data = db.execute("SELECT * FROM poi").fetchall()
    return render_template("peta.html", desa=DESA, poi=poi_data)

if __name__ == "__main__":
    #init_db()
    app.run(debug=True, host="0.0.0.0", port=5001)

