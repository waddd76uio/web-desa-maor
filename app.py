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
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    g,
    redirect,
    url_for,
    session,
)
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
# Nama database disesuaikan untuk Desa Maor
DB_PATH = BASE_DIR / "maor.db"

app = Flask(__name__)

# Kunci rahasia untuk sistem login
app.secret_key = "kunci_rahasia_maor_2026"

# Pengaturan folder untuk menyimpan foto berita
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
    "telepon": "081234567890",  # Placeholder - sesuaikan jika ada data valid
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
        "Meningkatkan sarana dan prasarana umum sesuai dengan aspirasi masyarakat yang dituangkan dalam dokumen Rencana Pembangunan Jangka Menengah Desa (RPJM Desa).",
    ],
    "struktur": [
        {"jabatan": "Kepala Desa", "nama": "Nama Kepala Desa"},
        {"jabatan": "Sekretaris Desa", "nama": "Nama Sekdes"},
        {"jabatan": "Kaur Keuangan", "nama": "Nama"},
    ],
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
    conn.executescript("""
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
        """)
    conn.commit()
    # Hapus data berita lama agar tidak menumpuk saat reset
    conn.execute("DELETE FROM berita")

    # Seeding data contoh Berita
    seed_berita = [
        (
            "Kerja Bakti Bersihkan Embung Desa",
            "17 Juli 2026",
            "Warga Desa Maor bergotong royong membersihkan area embung untuk persiapan musim kemarau.",
            "Isi berita lengkap di sini...",
            "default.jpg",
        ),
        (
            "Penyaluran Bantuan Bibit Padi",
            "15 Juli 2026",
            "Pemerintah Desa Maor menyalurkan bantuan bibit padi unggul kepada kelompok tani.",
            "Isi berita lengkap di sini...",
            "default.jpg",
        ),
        (
            "Posyandu Balita Bulan Juli Berjalan Lancar",
            "10 Juli 2026",
            "Kegiatan posyandu rutin bulan ini dihadiri oleh puluhan balita dan ibu hamil di Polindes.",
            "Isi berita lengkap di sini...",
            "default.jpg",
        ),
    ]
    conn.executemany(
        "INSERT INTO berita (judul, tanggal, ringkasan, isi, gambar) VALUES (?,?,?,?,?)",
        seed_berita,
    )
    conn.commit()

    # Masukkan data (pasti dieksekusi karena tabel baru saja di-reset)
    seed_poi = [
        (
            "Kantor Kepala Desa Maor",
            "Pemerintahan",
            "Pusat pelayanan administrasi dan pemerintahan Desa Maor.",
            -7.204406966500724,
            112.35340342229905,
        ),
        (
            "Masjid Desa' Maor",
            "Peribadatan",
            "Masjid utama yang menjadi pusat kegiatan keagamaan warga setempat.",
            -7.205148801479981,
            112.35316240013985,
        ),
        (
            "MI Maor",
            "Pendidikan",
            "Madrasah Ibtidaiyah yang melayani pendidikan dasar agama anak-anak.",
            -7.205347319005749,
            112.35317659401258,
        ),
        (
            "SD Negeri Maor",
            "Pendidikan",
            "Sekolah dasar negeri yang memfasilitasi belajar mengajar usia dini di desa.",
            -7.204453077046238,
            112.35311269110177,
        ),
        (
            "Embung Desa",
            "Pengairan",
            "Sumber penampungan air untuk irigasi persawahan, khususnya saat musim kemarau.",
            -7.208761992401299,
            112.3494784965776,
        ),
        (
            "Polindes Desa Maor",
            "Kesehatan",
            "Fasilitas pondok bersalin dan layanan kesehatan dasar desa.",
            -7.204192253274142,
            112.35324059733296,
        ),
        (
            "Tour And Travel Mujahidin",
            "Usaha Warga",
            "Biro perjalanan dan layanan transportasi milik warga desa.",
            -7.204244921639009,
            112.35318431873094,
        ),
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

    total_row = db.execute(
        "SELECT COALESCE(SUM(jumlah),0) AS total FROM kunjungan"
    ).fetchone()

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
    db.execute(
        "CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, judul TEXT, tanggal TEXT, waktu TEXT, lokasi TEXT)"
    )
    db.commit()

    # Ambil data agenda, urutkan dari tanggal terdekat
    agenda_raw = db.execute("SELECT * FROM agenda ORDER BY tanggal ASC").fetchall()

    # Proses konversi format tanggal (Misal: 2026-08-17 menjadi "17" dan "Agu")
    daftar_agenda = []
    bulan_indo = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "Mei",
        "Jun",
        "Jul",
        "Agu",
        "Sep",
        "Okt",
        "Nov",
        "Des",
    ]

    for a in agenda_raw:
        try:
            dt = datetime.datetime.strptime(a["tanggal"], "%Y-%m-%d")
            tgl_angka = dt.strftime("%d")
            bln_teks = bulan_indo[dt.month - 1]
        except:
            tgl_angka = "--"
            bln_teks = "--"

        daftar_agenda.append(
            {
                "judul": a["judul"],
                "waktu": a["waktu"],
                "lokasi": a["lokasi"],
                "tgl_angka": tgl_angka,
                "bln_teks": bln_teks,
            }
        )

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

    # Mengambil berita dari database,
    # diurutkan dari yang terbaru
    daftar_berita = db.execute("SELECT * FROM berita ORDER BY id DESC").fetchall()

    return render_template(
        "berita.html",
        desa=DESA,
        berita=daftar_berita,
    )


# ==========================================
# HALAMAN PUBLIK UMKM
# ==========================================
@app.route("/umkm")
def umkm():
    db = get_db()

    # Memastikan tabel UMKM tersedia
    db.execute("""
        CREATE TABLE IF NOT EXISTS umkm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_produk TEXT NOT NULL,
            nama_usaha TEXT NOT NULL,
            kategori TEXT NOT NULL,
            harga INTEGER NOT NULL,
            satuan TEXT NOT NULL,
            deskripsi TEXT,
            nomor_wa TEXT NOT NULL,
            alamat TEXT NOT NULL,
            maps_url TEXT NOT NULL,
            gambar TEXT,
            status TEXT NOT NULL DEFAULT 'aktif',
            tanggal TEXT NOT NULL
        )
    """)

    db.commit()

    # Hanya menampilkan produk yang statusnya aktif
    daftar_umkm = db.execute("""
        SELECT *
        FROM umkm
        WHERE status = 'aktif'
        ORDER BY id DESC
    """).fetchall()

    return render_template(
        "umkm.html",
        desa=DESA,
        daftar_umkm=daftar_umkm,
    )


@app.route("/api/poi")
def api_poi():
    db = get_db()
    rows = db.execute("SELECT * FROM poi ORDER BY id").fetchall()

    # Kategori warna disesuaikan dengan geografi wilayah pertanian
    kategori_warna = {
        "Pemerintahan": "#c0572a",
        "Pertanian": "#4caf50",  # Hijau untuk area persawahan
        "Pengairan": "#2196f3",  # Biru untuk waduk/embung
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
                "warna": kategori_warna.get(
                    r["kategori"], "#607d8b"
                ),  # Default warna Abu-abu kebiruan
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
        (
            payload["nama"],
            payload["kategori"],
            payload["deskripsi"],
            float(payload["lat"]),
            float(payload["lng"]),
        ),
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
    # Mengecek apakah admin sudah login
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    # Membuka koneksi database
    db = get_db()

    # Memastikan tabel infografis tersedia
    db.execute("""
        CREATE TABLE IF NOT EXISTS infografis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT NOT NULL,
            gambar TEXT,
            tanggal TEXT NOT NULL
        )
        """)

    # Memastikan tabel agenda tersedia
    db.execute("""
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT NOT NULL,
            tanggal TEXT NOT NULL,
            waktu TEXT NOT NULL,
            lokasi TEXT NOT NULL
        )
        """)

    # Memastikan tabel titik peta tersedia
    db.execute("""
        CREATE TABLE IF NOT EXISTS poi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            kategori TEXT NOT NULL,
            deskripsi TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL
        )
        """)

    # Memastikan tabel UMKM tersedia
    db.execute("""
        CREATE TABLE IF NOT EXISTS umkm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_produk TEXT NOT NULL,
            nama_usaha TEXT NOT NULL,
            kategori TEXT NOT NULL,
            harga INTEGER NOT NULL,
            satuan TEXT NOT NULL,
            deskripsi TEXT,
            nomor_wa TEXT NOT NULL,
            alamat TEXT NOT NULL,
            maps_url TEXT NOT NULL,
            gambar TEXT,
            status TEXT NOT NULL DEFAULT 'aktif',
            tanggal TEXT NOT NULL
        )
        """)

    db.commit()

    # Bagian ini dijalankan ketika admin mengirim formulir
    if request.method == "POST":
        jenis_form = request.form.get("jenis_form")

        # ==========================================
        # FORM TAMBAH BERITA
        # ==========================================
        if jenis_form == "berita":
            judul = request.form.get("judul")
            ringkasan = request.form.get("ringkasan")
            isi = request.form.get("isi")
            gambar = request.files.get("gambar")

            tanggal = datetime.datetime.now(Waktu_Lokal).strftime("%d %B %Y")

            filename = "default.jpg"

            if gambar and gambar.filename:
                filename = secure_filename(gambar.filename)

                gambar.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            db.execute(
                """
                INSERT INTO berita
                (judul, tanggal, ringkasan, isi, gambar)
                VALUES (?, ?, ?, ?, ?)
                """,
                (judul, tanggal, ringkasan, isi, filename),
            )

            db.commit()

            return redirect(url_for("admin_dashboard"))

        # ==========================================
        # FORM TAMBAH TITIK PETA
        # ==========================================
        elif jenis_form == "poi":
            nama = request.form.get("nama")
            kategori = request.form.get("kategori")
            deskripsi = request.form.get("deskripsi")
            lat = request.form.get("lat")
            lng = request.form.get("lng")

            db.execute(
                """
                INSERT INTO poi
                (nama, kategori, deskripsi, lat, lng)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nama, kategori, deskripsi, float(lat), float(lng)),
            )

            db.commit()

            return redirect(url_for("admin_dashboard"))

        # ==========================================
        # FORM TAMBAH INFOGRAFIS
        # ==========================================
        elif jenis_form == "infografis":
            judul = request.form.get("judul")
            gambar = request.files.get("gambar")

            tanggal = datetime.datetime.now(Waktu_Lokal).strftime("%d %B %Y")

            filename = "default.jpg"

            if gambar and gambar.filename:
                filename = secure_filename(gambar.filename)

                gambar.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            db.execute(
                """
                INSERT INTO infografis
                (judul, gambar, tanggal)
                VALUES (?, ?, ?)
                """,
                (judul, filename, tanggal),
            )

            db.commit()

            return redirect(url_for("admin_dashboard"))

        # ==========================================
        # FORM TAMBAH AGENDA
        # ==========================================
        elif jenis_form == "agenda":
            judul = request.form.get("judul")
            tanggal = request.form.get("tanggal")
            waktu = request.form.get("waktu")
            lokasi = request.form.get("lokasi")

            db.execute("""
                CREATE TABLE IF NOT EXISTS agenda (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    judul TEXT,
                    tanggal TEXT,
                    waktu TEXT,
                    lokasi TEXT
                )
                """)

            db.execute(
                """
                INSERT INTO agenda
                (judul, tanggal, waktu, lokasi)
                VALUES (?, ?, ?, ?)
                """,
                (judul, tanggal, waktu, lokasi),
            )

            db.commit()

            return redirect(url_for("admin_dashboard"))

        # ==========================================
        # FORM TAMBAH PRODUK UMKM
        # ==========================================
        elif jenis_form == "umkm":
            nama_produk = request.form.get("nama_produk", "").strip()
            nama_usaha = request.form.get("nama_usaha", "").strip()
            kategori = request.form.get("kategori", "").strip()
            harga = request.form.get("harga", "").strip()
            satuan = request.form.get("satuan", "").strip()
            deskripsi = request.form.get("deskripsi", "").strip()
            nomor_wa = request.form.get("nomor_wa", "").strip()
            alamat = request.form.get("alamat", "").strip()
            maps_url = request.form.get("maps_url", "").strip()
            status = request.form.get("status", "aktif").strip()
            gambar = request.files.get("gambar")

            # Memastikan data wajib telah diisi
            if (
                not nama_produk
                or not nama_usaha
                or not kategori
                or not harga
                or not satuan
                or not nomor_wa
                or not alamat
                or not maps_url
            ):
                return "Data produk UMKM belum lengkap.", 400

            # Memastikan harga berupa angka
            try:
                harga_angka = int(harga)
            except ValueError:
                return "Harga produk harus berupa angka.", 400

            # Mengubah nomor 08 menjadi 628 secara otomatis
            nomor_wa = nomor_wa.replace(" ", "").replace("-", "")

            if nomor_wa.startswith("08"):
                nomor_wa = "62" + nomor_wa[1:]
            elif nomor_wa.startswith("+62"):
                nomor_wa = nomor_wa[1:]

            tanggal = datetime.datetime.now(Waktu_Lokal).strftime("%d %B %Y")

            filename = "default.jpg"

            # Menyimpan gambar produk
            if gambar and gambar.filename:
                nama_asli = secure_filename(gambar.filename)

                kode_waktu = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

                filename = f"umkm_{kode_waktu}_{nama_asli}"

                gambar.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename,
                    )
                )

            # Menyimpan data UMKM ke database
            db.execute(
                """
                INSERT INTO umkm (
                    nama_produk,
                    nama_usaha,
                    kategori,
                    harga,
                    satuan,
                    deskripsi,
                    nomor_wa,
                    alamat,
                    maps_url,
                    gambar,
                    status,
                    tanggal
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    nama_produk,
                    nama_usaha,
                    kategori,
                    harga_angka,
                    satuan,
                    deskripsi,
                    nomor_wa,
                    alamat,
                    maps_url,
                    filename,
                    status,
                    tanggal,
                ),
            )

            db.commit()

            return redirect(url_for("admin_dashboard"))

    # ==========================================
    # MENAMPILKAN HALAMAN ADMIN
    # ==========================================

    daftar_berita = db.execute("""
        SELECT *
        FROM berita
        ORDER BY id DESC
        """).fetchall()

    daftar_infografis = db.execute("""
        SELECT *
        FROM infografis
        ORDER BY id DESC
        """).fetchall()

    daftar_agenda = db.execute("""
        SELECT *
        FROM agenda
        ORDER BY tanggal ASC, id ASC
        """).fetchall()

    daftar_poi = db.execute("""
        SELECT *
        FROM poi
        ORDER BY id ASC
        """).fetchall()

    daftar_umkm = db.execute("""
        SELECT *
        FROM umkm
        ORDER BY id DESC
        """).fetchall()

    return render_template(
        "admin.html",
        desa=DESA,
        daftar_berita=daftar_berita,
        daftar_infografis=daftar_infografis,
        daftar_agenda=daftar_agenda,
        daftar_poi=daftar_poi,
        daftar_umkm=daftar_umkm,
    )


# ==========================================
# EDIT TITIK PETA
# ==========================================
@app.route(
    "/admin/poi/<int:id_poi>/edit",
    methods=["GET", "POST"],
)
def admin_edit_poi(id_poi):
    # Memastikan admin sudah login
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    db = get_db()

    # Mengambil data titik peta berdasarkan ID
    item = db.execute(
        "SELECT * FROM poi WHERE id = ?",
        (id_poi,),
    ).fetchone()

    # Jika titik peta tidak ditemukan
    if item is None:
        return "Titik peta tidak ditemukan", 404

    # Dijalankan ketika tombol Simpan Perubahan ditekan
    if request.method == "POST":
        nama = request.form.get("nama", "").strip()
        kategori = request.form.get("kategori", "").strip()
        deskripsi = request.form.get("deskripsi", "").strip()
        lat = request.form.get("lat", "").strip()
        lng = request.form.get("lng", "").strip()

        # Memastikan seluruh kolom terisi
        if not nama or not kategori or not deskripsi or not lat or not lng:
            return render_template(
                "admin_edit_poi.html",
                desa=DESA,
                item=item,
                error="Nama, kategori, deskripsi, latitude, dan longitude wajib diisi.",
            )

        # Memastikan latitude dan longitude berupa angka
        try:
            lat_angka = float(lat)
            lng_angka = float(lng)
        except ValueError:
            return render_template(
                "admin_edit_poi.html",
                desa=DESA,
                item=item,
                error="Latitude dan longitude harus berupa angka.",
            )

        # Memperbarui data titik peta
        db.execute(
            """
            UPDATE poi
            SET nama = ?,
                kategori = ?,
                deskripsi = ?,
                lat = ?,
                lng = ?
            WHERE id = ?
            """,
            (
                nama,
                kategori,
                deskripsi,
                lat_angka,
                lng_angka,
                id_poi,
            ),
        )

        db.commit()

        return redirect(url_for("admin_dashboard"))

    # Menampilkan halaman edit titik peta
    return render_template(
        "admin_edit_poi.html",
        desa=DESA,
        item=item,
    )


# ==========================================
# HAPUS TITIK PETA
# ==========================================
@app.route("/admin/poi/<int:id_poi>/hapus", methods=["POST"])
def admin_hapus_poi(id_poi):
    # Memastikan admin sudah login
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    db = get_db()

    # Memastikan titik peta benar-benar tersedia
    item = db.execute(
        "SELECT id FROM poi WHERE id = ?",
        (id_poi,),
    ).fetchone()

    if item is None:
        return "Titik peta tidak ditemukan", 404

    # Menghapus titik peta berdasarkan ID
    db.execute(
        "DELETE FROM poi WHERE id = ?",
        (id_poi,),
    )

    db.commit()

    return redirect(url_for("admin_dashboard"))


# ==========================================
# EDIT AGENDA
# ==========================================
@app.route(
    "/admin/agenda/<int:id_agenda>/edit",
    methods=["GET", "POST"],
)
def admin_edit_agenda(id_agenda):
    # Memastikan admin sudah login
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    db = get_db()

    # Mengambil data agenda berdasarkan ID
    item = db.execute(
        "SELECT * FROM agenda WHERE id = ?",
        (id_agenda,),
    ).fetchone()

    # Jika agenda tidak ditemukan
    if item is None:
        return "Agenda tidak ditemukan", 404

    # Dijalankan ketika tombol Simpan Perubahan ditekan
    if request.method == "POST":
        judul = request.form.get("judul", "").strip()
        tanggal = request.form.get("tanggal", "").strip()
        waktu = request.form.get("waktu", "").strip()
        lokasi = request.form.get("lokasi", "").strip()

        # Memastikan semua kolom telah diisi
        if not judul or not tanggal or not waktu or not lokasi:
            return render_template(
                "admin_edit_agenda.html",
                desa=DESA,
                item=item,
                error="Nama kegiatan, tanggal, waktu, dan lokasi wajib diisi.",
            )

        # Memperbarui data agenda
        db.execute(
            """
            UPDATE agenda
            SET judul = ?,
                tanggal = ?,
                waktu = ?,
                lokasi = ?
            WHERE id = ?
            """,
            (
                judul,
                tanggal,
                waktu,
                lokasi,
                id_agenda,
            ),
        )

        db.commit()

        return redirect(url_for("admin_dashboard"))

    # Menampilkan halaman edit agenda
    return render_template(
        "admin_edit_agenda.html",
        desa=DESA,
        item=item,
    )


# ==========================================
# HAPUS AGENDA
# ==========================================
@app.route("/admin/agenda/<int:id_agenda>/hapus", methods=["POST"])
def admin_hapus_agenda(id_agenda):
    # Memastikan admin sudah login
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    db = get_db()

    # Memastikan data agenda benar-benar tersedia
    item = db.execute(
        "SELECT id FROM agenda WHERE id = ?",
        (id_agenda,),
    ).fetchone()

    if item is None:
        return "Agenda tidak ditemukan", 404

    # Menghapus agenda berdasarkan ID
    db.execute(
        "DELETE FROM agenda WHERE id = ?",
        (id_agenda,),
    )

    db.commit()

    return redirect(url_for("admin_dashboard"))


# ==========================================
# EDIT INFOGRAFIS
# ==========================================


@app.route("/admin/infografis/<int:id_infografis>/edit", methods=["GET", "POST"])
def admin_edit_infografis(id_infografis):
    # Memastikan admin sudah login
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    db = get_db()

    # Mengambil data infografis berdasarkan ID
    item = db.execute(
        "SELECT * FROM infografis WHERE id = ?", (id_infografis,)
    ).fetchone()

    # Jika data tidak ditemukan
    if item is None:
        return "Infografis tidak ditemukan", 404

    # Dijalankan ketika tombol Simpan ditekan
    if request.method == "POST":
        judul = request.form.get("judul", "").strip()
        tanggal = request.form.get("tanggal", "").strip()
        gambar = request.files.get("gambar")

        # Validasi sederhana
        if not judul or not tanggal:
            return render_template(
                "admin_edit_infografis.html",
                desa=DESA,
                item=item,
                error="Judul dan tanggal wajib diisi.",
            )

        # Tetap menggunakan gambar lama
        filename = item["gambar"]

        # Jika admin memilih gambar baru
        if gambar and gambar.filename:
            nama_asli = secure_filename(gambar.filename)

            kode_waktu = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            filename = f"{kode_waktu}_{nama_asli}"

            gambar.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        # Memperbarui data infografis
        db.execute(
            """
            UPDATE infografis
            SET judul = ?,
                tanggal = ?,
                gambar = ?
            WHERE id = ?
            """,
            (judul, tanggal, filename, id_infografis),
        )

        db.commit()

        return redirect(url_for("admin_dashboard"))

    # Menampilkan halaman edit
    return render_template("admin_edit_infografis.html", desa=DESA, item=item)


# ==========================================
# HAPUS INFOGRAFIS
# ==========================================
@app.route("/admin/infografis/<int:id_infografis>/hapus", methods=["POST"])
def admin_hapus_infografis(id_infografis):
    # Memastikan admin sudah login
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    db = get_db()

    # Memastikan data infografis tersedia
    item = db.execute(
        "SELECT id FROM infografis WHERE id = ?", (id_infografis,)
    ).fetchone()

    if item is None:
        return "Infografis tidak ditemukan", 404

    # Menghapus data infografis dari database
    db.execute("DELETE FROM infografis WHERE id = ?", (id_infografis,))

    db.commit()

    return redirect(url_for("admin_dashboard"))


# ==========================================
# EDIT BERITA
# ==========================================
@app.route("/admin/berita/<int:id_berita>/edit", methods=["GET", "POST"])
def admin_edit_berita(id_berita):
    # Memastikan admin sudah login
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    db = get_db()

    # Mengambil berita berdasarkan ID
    item = db.execute("SELECT * FROM berita WHERE id = ?", (id_berita,)).fetchone()

    # Jika berita tidak ditemukan
    if item is None:
        return "Berita tidak ditemukan", 404

    # Bagian ini dijalankan saat tombol Simpan ditekan
    if request.method == "POST":
        judul = request.form.get("judul", "").strip()
        tanggal = request.form.get("tanggal", "").strip()
        ringkasan = request.form.get("ringkasan", "").strip()
        isi = request.form.get("isi", "").strip()
        gambar = request.files.get("gambar")

        # Validasi sederhana
        if not judul or not tanggal or not ringkasan or not isi:
            return render_template(
                "admin_edit_berita.html",
                desa=DESA,
                item=item,
                error="Judul, tanggal, ringkasan, dan isi wajib diisi.",
            )

        # Tetap memakai gambar lama
        filename = item["gambar"]

        # Jika admin memilih gambar baru
        if gambar and gambar.filename:
            nama_asli = secure_filename(gambar.filename)

            # Menambahkan waktu agar nama gambar tidak sama
            kode_waktu = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            filename = f"{kode_waktu}_{nama_asli}"

            gambar.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        # Memperbarui data berita
        db.execute(
            """
            UPDATE berita
            SET judul = ?,
                tanggal = ?,
                ringkasan = ?,
                isi = ?,
                gambar = ?
            WHERE id = ?
            """,
            (judul, tanggal, ringkasan, isi, filename, id_berita),
        )

        db.commit()

        return redirect(url_for("admin_dashboard"))

    # Menampilkan halaman edit
    return render_template("admin_edit_berita.html", desa=DESA, item=item)


# ==========================================
# EDIT PRODUK UMKM
# ==========================================
@app.route(
    "/admin/umkm/<int:id_umkm>/edit",
    methods=["GET", "POST"],
)
def admin_edit_umkm(id_umkm):
    # Memastikan admin sudah login
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    db = get_db()

    # Mengambil produk UMKM berdasarkan ID
    item = db.execute(
        "SELECT * FROM umkm WHERE id = ?",
        (id_umkm,),
    ).fetchone()

    # Jika produk tidak ditemukan
    if item is None:
        return "Produk UMKM tidak ditemukan", 404

    # Dijalankan saat tombol Simpan Perubahan ditekan
    if request.method == "POST":
        nama_produk = request.form.get("nama_produk", "").strip()

        nama_usaha = request.form.get("nama_usaha", "").strip()

        kategori = request.form.get("kategori", "").strip()

        harga = request.form.get("harga", "").strip()

        satuan = request.form.get("satuan", "").strip()

        deskripsi = request.form.get("deskripsi", "").strip()

        nomor_wa = request.form.get("nomor_wa", "").strip()

        alamat = request.form.get("alamat", "").strip()

        maps_url = request.form.get("maps_url", "").strip()

        status = request.form.get("status", "aktif").strip()

        gambar = request.files.get("gambar")

        # Validasi kolom wajib
        if (
            not nama_produk
            or not nama_usaha
            or not kategori
            or not harga
            or not satuan
            or not nomor_wa
            or not alamat
            or not maps_url
        ):
            return render_template(
                "admin_edit_umkm.html",
                desa=DESA,
                item=item,
                error="Semua data wajib harus diisi.",
            )

        # Memastikan harga berupa angka
        try:
            harga_angka = int(harga)
        except ValueError:
            return render_template(
                "admin_edit_umkm.html",
                desa=DESA,
                item=item,
                error="Harga produk harus berupa angka.",
            )

        # Merapikan nomor WhatsApp
        nomor_wa = nomor_wa.replace(" ", "").replace("-", "")

        if nomor_wa.startswith("08"):
            nomor_wa = "62" + nomor_wa[1:]

        elif nomor_wa.startswith("+62"):
            nomor_wa = nomor_wa[1:]

        # Tetap menggunakan gambar lama
        filename = item["gambar"]

        # Jika admin memilih gambar baru
        if gambar and gambar.filename:
            nama_asli = secure_filename(gambar.filename)

            kode_waktu = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            filename_baru = f"umkm_{kode_waktu}_{nama_asli}"

            gambar.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename_baru,
                )
            )

            # Hapus gambar lama jika tersedia
            if filename and filename != "default.jpg":
                lokasi_gambar_lama = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename,
                )

                if os.path.exists(lokasi_gambar_lama):
                    os.remove(lokasi_gambar_lama)

            filename = filename_baru

        # Memperbarui data UMKM
        db.execute(
            """
            UPDATE umkm
            SET nama_produk = ?,
                nama_usaha = ?,
                kategori = ?,
                harga = ?,
                satuan = ?,
                deskripsi = ?,
                nomor_wa = ?,
                alamat = ?,
                maps_url = ?,
                gambar = ?,
                status = ?
            WHERE id = ?
            """,
            (
                nama_produk,
                nama_usaha,
                kategori,
                harga_angka,
                satuan,
                deskripsi,
                nomor_wa,
                alamat,
                maps_url,
                filename,
                status,
                id_umkm,
            ),
        )

        db.commit()

        return redirect(url_for("admin_dashboard"))

    return render_template(
        "admin_edit_umkm.html",
        desa=DESA,
        item=item,
    )


# ==========================================
# HAPUS PRODUK UMKM
# ==========================================
@app.route("/admin/umkm/<int:id_umkm>/hapus", methods=["POST"])
def admin_hapus_umkm(id_umkm):
    # Memastikan admin sudah login
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    db = get_db()

    # Mengambil produk UMKM berdasarkan ID
    item = db.execute(
        "SELECT * FROM umkm WHERE id = ?",
        (id_umkm,),
    ).fetchone()

    # Jika produk tidak ditemukan
    if item is None:
        return "Produk UMKM tidak ditemukan", 404

    # Menyimpan nama gambar sebelum data dihapus
    nama_gambar = item["gambar"]

    # Menghapus data produk dari database
    db.execute(
        "DELETE FROM umkm WHERE id = ?",
        (id_umkm,),
    )

    db.commit()

    # Menghapus file gambar produk dari folder uploads
    if nama_gambar and nama_gambar != "default.jpg":
        lokasi_gambar = os.path.join(
            app.config["UPLOAD_FOLDER"],
            nama_gambar,
        )

        if os.path.exists(lokasi_gambar):
            os.remove(lokasi_gambar)

    return redirect(url_for("admin_dashboard"))


# ==========================================
# HAPUS BERITA
# ==========================================
@app.route("/admin/berita/<int:id_berita>/hapus", methods=["POST"])
def admin_hapus_berita(id_berita):
    # Pastikan hanya admin yang sudah login
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    db = get_db()

    # Memastikan berita benar-benar ada
    item = db.execute("SELECT id FROM berita WHERE id = ?", (id_berita,)).fetchone()

    if item is None:
        return "Berita tidak ditemukan", 404

    # Menghapus berita berdasarkan ID
    db.execute("DELETE FROM berita WHERE id = ?", (id_berita,))

    db.commit()

    return redirect(url_for("admin_dashboard"))


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
    db.execute(
        "CREATE TABLE IF NOT EXISTS infografis (id INTEGER PRIMARY KEY AUTOINCREMENT, judul TEXT, gambar TEXT, tanggal TEXT)"
    )
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
    # init_db()
    app.run(debug=True, host="0.0.0.0", port=5001)
