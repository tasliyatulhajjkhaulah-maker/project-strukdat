
import sys
from pathlib import Path

# Menambahkan folder utama proyek ke jalur pencarian Python
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


import time
import tkinter as tk
from tkinter import ttk

from backend.m1 import (array, Linkedlist, muat, buat_pesanan,
                                teks, detail_pesanan, jam,
                                KATEGORI_VIP, KATEGORI_PRIORITAS, KATEGORI_REGULER,
                                T_MASUK_DETIK, HARGA, OID)
from backend.m2 import (Queue, Stack, isi_antrean,
                                lanjut, catat, hapus,
                                undo, redo, hitung)
from backend.m3 import (laporan, urutkan, linear_search, cari_semua,teks_ringkasan)

BATAS_SORT = 15000      # sort O(n^2): lebih dari ini terlalu lama untuk satu klik
TAMPIL_MAKS = 20        # jumlah baris yang ditampilkan di panel hasil
DAFTAR_RESTO = ("semua", "bakso-pak-yon", "kafe-teknik", "kantin-asrama",
                "kantin-pusat", "kedai-kopi", "warung-bu-ida")
DAFTAR_STATUS = ("semua", "DONE", "CANCEL", "ANTRE")

# ================================================================ helper

def ms_sejak(t0):
    return (time.perf_counter() - t0) * 1000

def detik_sekarang():
    t = time.localtime()
    return t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec

def ke_int(teks, nama):
    try:
        return int(teks.strip())
    except ValueError:
        raise ValueError(nama + " harus berupa bilangan bulat, bukan '" + teks + "'.")

def ke_detik(teks, akhir=False):
    """'11:00' / '11:00:30' / '39600' -> detik. akhir=True: 'HH:MM' dihitung sampai detik ke-59."""
    teks = teks.strip()
    bagian = teks.split(":")
    try:
        if len(bagian) == 1:
            return int(bagian[0])
        detik = int(bagian[0]) * 3600 + int(bagian[1]) * 60
        if len(bagian) >= 3:
            detik += int(bagian[2])
        elif akhir:
            detik += 59
        return detik
    except ValueError:
        raise ValueError("Format waktu salah: '" + teks + "' (pakai HH:MM, HH:MM:SS, atau detik).")

# ================================================================ keadaan

class Keadaan:
    def __init__(pesan, path_csv):
        pesan.path_csv = path_csv
        pesan.reset()
    def reset(pesan):
        pesan.arr = array()
        pesan.ll = Linkedlist()
        pesan.antrean = Queue()
        pesan.riwayat = Stack()          # tumpukan undo
        pesan.redo_riwayat = Stack()
        pesan.laporan = None
        pesan.laporan_kolom = T_MASUK_DETIK
        pesan.nomor_oid = 1                 # oid berikutnya
        pesan.dimuat = False

# ================================================================ logika menu

class Aksi:
    def __init__(pesan, keadaan):
       pesan.k = keadaan

    def _perlu_data(pesan):
        if not pesan.k.dimuat:
            raise ValueError("Data belum dimuat. Klik menu Load dulu.")
    # ------------------------------------------------------------ DATA
    def load(pesan, nilai):
        k = pesan.k
        path = nilai[0].strip()
        if path == "":
            path = k.path_csv
        k.reset()
        t0 = time.perf_counter()
        jumlah = muat(path, k.arr, k.ll)
        ms = ms_sejak(t0)
        k.dimuat = True
        k.path_csv = path
        k.nomor_oid = jumlah + 1
        teks = ("Berhasil memuat " + str(jumlah) + " baris dari\n" + path + "\n\n"
                + "array      : size " + str(k.arr.size) + ", kapasitas " + str(k.arr.cap) + "\n"
                + "linkedlist : size " + str(k.ll.size) + "\n\n"
                + "oid pesanan baru berikutnya: O-" + str(k.nomor_oid).zfill(6))
        return ("M1 - larik+rantai", ms, teks)
    # ------------------------------------------------------------ M1
    def lihat(pesan, struktur, modul, nilai):
        pesan._perlu_data()
        indeks = ke_int(nilai[0], "Indeks")
        t0 = time.perf_counter()
        p = struktur.get(indeks)
        ms = ms_sejak(t0)
        teks = ("Pesanan ke-" + str(indeks) + " dari " + str(struktur.size) + " pesanan\n\n"
                + detail_pesanan(p))
        return (modul, ms, teks)

    def _hapus_redo(pesan):
        pesan.k.redo_riwayat = Stack()
    
    def tambah_pesanan(pesan, struktur, modul, jenis, nilai):
        pesan._perlu_data()
        k = pesan.k
        nama = nilai[0].strip()
        if nama == "":
            raise ValueError("Nama pelanggan tidak boleh kosong.")
        p = buat_pesanan(nama, jenis, k.nomor_oid, detik_sekarang())
        t0 = time.perf_counter()
        posisi = catat(k.riwayat, struktur, p)
        ms = ms_sejak(t0)
        k.nomor_oid += 1
        pesan._hapus_redo()
        teks = ("Pesanan ditambahkan\n\n" + detail_pesanan(p) + "\n\n"
                + "posisi sisip : " + str(posisi) + " (dari " + str(struktur.size) + " pesanan)\n"
                + "aksi dicatat ke tumpukan undo (" + str(k.riwayat.ukuran()) + " aksi)")
        return (modul, ms, teks)

    def hapus_pesanan(pesan, struktur, modul, nilai):
        pesan._perlu_data()
        k = pesan.k
        indeks = ke_int(nilai[0], "Indeks")
        t0 = time.perf_counter()
        p = hapus(k.riwayat, struktur, indeks)
        ms = ms_sejak(t0)
        pesan._hapus_redo()
        teks = ("Pesanan ke-" + str(indeks) + " dihapus\n\n" + detail_pesanan(p) + "\n\n"
                + "sisa " + str(struktur.size) + " pesanan\n"
                + "aksi dicatat ke tumpukan undo (" + str(k.riwayat.ukuran()) + " aksi)")
        return (modul,  ms, teks)
    # ------------------------------------------------------------ M2
    def isi_fifo(pesan, nilai):
        pesan._perlu_data()
        k = pesan.k

        k.antrean = Queue()

        t0 = time.perf_counter()
        jumlah = isi_antrean(k.arr, k.antrean)
        ms = ms_sejak(t0)

        hasil_teks = (
            "Antrean berhasil diisi\n\n"
            + "Jumlah pesanan : " + str(jumlah) + "\n"
            + "Kapasitas      : " + str(k.antrean.cap) + "\n\n"
            + "Isi antrean:\n" )
        
        for i in range(min(10, k.antrean.size)):
            hasil_teks += (
                str(i + 1) + ". "
                + detail_pesanan(k.antrean.get(i)) + "\n")
        return ("M2 - antrean", ms, hasil_teks)
        
    def layani(pesan, nilai):
        pesan._perlu_data()
        k = pesan.k
        t0 = time.perf_counter()
        p = lanjut(k.antrean, k.riwayat)
        ms = ms_sejak(t0)
        if p is None:
            return ("M2 - antrean", ms, "Antrean kosong. Jalankan 'Isi antrean FIFO' dulu.")
        pesan._hapus_redo()
        teks = ("Melayani pesanan terdepan\n\n" + detail_pesanan(p) + "\n\n"
                + "sisa antrean : " + str(k.antrean.size) + "\n"
                + "aksi dicatat ke tumpukan undo (" + str(k.riwayat.ukuran()) + " aksi)")
        return ("M2 - antrean", ms, teks)
    
    def batalkan(pesan, nilai):
        pesan._perlu_data()
        k = pesan.k

        t0 = time.perf_counter()
        hasil = undo(k.riwayat, k.antrean, k.redo_riwayat)
        ms = ms_sejak(t0)

        if hasil is None:
            return ( "M2 - tumpukan", ms , "Tidak ada aksi yang bisa di-undo.")

        hasil_teks = (
            hasil + "\n\n"
            + "Tumpukan undo : " + str(k.riwayat.ukuran()) + " aksi\n"
            + "Tumpukan redo : " + str(k.redo_riwayat.ukuran()) + " aksi\n"
            + "Antrean       : " + str(k.antrean.size) + " pesanan")

        return ("M2 - tumpukan", ms, hasil_teks)

    def ulangi(pesan, nilai):
       pesan._perlu_data()
       k = pesan.k

       t0 = time.perf_counter()
       hasil = redo(k.riwayat, k.antrean, k.redo_riwayat)
       ms = ms_sejak(t0)

       if hasil is None:
            return (
                "M2 - tumpukan",
                ms,
                "Tidak ada aksi yang bisa di-redo."
            )

       teks_hasil = ( hasil + "\n\n"
                    + "sisa tumpukan undo : " + str(k.riwayat.ukuran()) + " aksi\n"
                    + "sisa tumpukan redo : " + str(k.redo_riwayat.ukuran()) + " aksi")
       return ("M2 - tumpukan", ms, teks_hasil)

    def redo(self, nilai):
         return (
        "M2 - TUMPUKAN",
        0,
        "Fungsi Redo belum dihubungkan ke stack riwayat."
    )

    
    def kasir(self, nilai):
        ekspresi = nilai[0].strip()

        if not ekspresi:
            raise ValueError("Ekspresi perhitungan tidak boleh kosong.")

        t0 = time.perf_counter()
        postfix, total = hitung(ekspresi)
        waktu = ms_sejak(t0)

        teks = (
            "KASIR - INFIX KE POSTFIX\n"
            "========================================\n\n"
            + "Ekspresi infix : " + ekspresi + "\n"
            + "Hasil postfix  : " + postfix + "\n"
            + "Total           : " + str(total) + "\n\n"
            + "========================================\n"
            + "Prioritas operator:\n"
            + "* dan / lebih tinggi daripada + dan -.\n"
            + "Perhitungan menggunakan Stack."
        )

        return "M2 - KASIR / STACK", waktu, teks

    # ------------------------------------------------------------ M3
    def laporan_harian(pesan, nilai):
        pesan._perlu_data()
        k = pesan.k
        resto = nilai[0]
        if resto == "semua":
            resto = ""
        status = nilai[1]
        if status == "semua":
            status = ""
        t_awal = ke_detik(nilai[2])
        t_akhir = ke_detik(nilai[3], True)
        if nilai[4] == "harga":
            kolom = HARGA
        else:
            kolom = T_MASUK_DETIK
        metode = nilai[5]
        t0 = time.perf_counter()
        lap = laporan(k.arr, resto, status, t_awal, t_akhir)
        ms_bangun = ms_sejak(t0)
        if lap.size > BATAS_SORT:
            raise ValueError("Laporan berisi " + str(lap.size) + " baris (batas " + str(BATAS_SORT)
                             + "). Sort O(n^2) akan sangat lama.\nPersempit filter: pilih satu resto, "
                             + "status, atau rentang jam yang lebih pendek.")
        t1 = time.perf_counter()
        urutkan(lap, kolom, metode)
        ms_sort = ms_sejak(t1)
        k.laporan = lap
        k.laporan_kolom = kolom
        teks = ("Laporan terurut menurut " + nilai[4] + " (" + metode + " sort)\n"
                + "filter  : resto=" + nilai[0] + ", status=" + nilai[1]
                + ", jam " + nilai[2] + " - " + nilai[3] + "\n"
                + "waktu   : saring " + ("%.2f" % ms_bangun) + " ms, urut " + ("%.2f" % ms_sort) + " ms\n"
                + teks_ringkasan(lap) + "\n\n"
                + str(min(TAMPIL_MAKS, lap.size)) + " baris pertama:\n")
        for i in range(min(TAMPIL_MAKS, lap.size)):
            teks += "  " + teks(lap.data[i]) + "\n"
        return ("M3 - " + metode, ms_sort, teks)
    def cari_laporan(pesan, nilai):
        pesan._perlu_data()
        k = pesan.k
        if k.laporan is None:
            raise ValueError("Belum ada laporan. Jalankan 'Laporan harian' dulu.")
        if k.laporan_kolom == T_MASUK_DETIK:
            target = ke_detik(nilai[0])
        else:
            target = ke_int(nilai[0], "Harga")
        t0 = time.perf_counter()
        hasil = cari_semua(k.laporan, target, k.laporan_kolom)
        ms = ms_sejak(t0)
        if hasil.size == 0:
            return ("M3 - binary search", ms, "Tidak ditemukan di laporan (" + str(k.laporan.size) + " baris).")
        teks = ("Ditemukan " + str(hasil.size) + " pesanan (binary search di " + str(k.laporan.size) + " baris)\n\n")
        for i in range(min(TAMPIL_MAKS, hasil.size)):
            teks += "  " + teks(hasil.data[i]) + "\n"
        if hasil.size > TAMPIL_MAKS:
            teks += "  ... dan " + str(hasil.size - TAMPIL_MAKS) + " lainnya\n"
        return ("M3 - binary search", ms, teks)

# ================================================================ definisi menu

class Menu:
    """fields: list tuple (label, default, pilihan, hint); pilihan = tuple isi combobox atau None."""
    def __init__(pesan, kode, judul, modul, deskripsi, tombol, fields, handler):
        pesan.kode = kode
        pesan.judul = judul
        pesan.modul = modul
        pesan.deskripsi = deskripsi
        pesan.tombol = tombol
        pesan.fields = fields
        pesan.handler = handler

def menu_m1(aksi, nama, kode, ambil):
    """Lima menu M1 untuk satu struktur. ambil() mengembalikan objek struktur saat ini."""
    modul = "M1 - " + kode
    f_indeks = [("Indeks pesanan", "0", None, "mulai dari 0")]
    f_nama = [("Nama pelanggan", "Pelanggan Baru", None, "nama untuk pesanan yang akan dibuat")]
    return [
        Menu(kode + "_get", nama + " - LIHAT PESANAN", modul,
             "get(i): buka detail satu pesanan. Array O(1), linked list O(n).",
             "LIHAT", f_indeks,
             lambda v: aksi.lihat(ambil(), modul, v)),
        Menu(kode + "_reguler", nama + " - TAMBAH PESANAN REGULER", modul,
             "Pesanan reguler mengantre di barisan paling belakang.",
             "TAMBAH", f_nama,
             lambda v: aksi.tambah_pesanan(ambil(), modul, KATEGORI_REGULER, v)),
        Menu(kode + "_prioritas", nama + " - TAMBAH PESANAN PRIORITAS", modul,
             "Pesanan prioritas menyerobot ke tengah barisan (size // 2).",
             "TAMBAH", f_nama,
             lambda v: aksi.tambah_pesanan(ambil(), modul, KATEGORI_PRIORITAS, v)),
        Menu(kode + "_vip", nama + " - TAMBAH PESANAN VIP", modul,
             "Pesanan VIP langsung ke urutan pertama.",
             "TAMBAH", f_nama,
             lambda v: aksi.tambah_pesanan(ambil(), modul, KATEGORI_VIP, v)),
        Menu(kode + "_hapus", nama + " - HAPUS PESANAN", modul,
             "Pesanan ke-i dicabut dari barisan. Aksi bisa di-undo.",
             "HAPUS", f_indeks,
             lambda v: aksi.hapus_pesanan(ambil(), modul, v)),
    ]

def buat_menu(aksi):
    k = aksi.k
    daftar = []
    daftar.append("DATA")
    daftar.append(Menu("load", "Load", "M1 - larik+rantai",
                       "Muat pesanan.csv ke array dan linked list sekaligus.",
                       "LOAD",
                       [("Path CSV", k.path_csv, None, "kosongkan untuk memakai path bawaan")],
                       aksi.load))
    daftar.append("M1 - DATA PESANAN")
    for m in menu_m1(aksi, "ARRAY", "array", lambda: aksi.k.arr):
        daftar.append(m)
    for m in menu_m1(aksi, "LINKEDLIST", "linkedlist", lambda: aksi.k.ll):
        daftar.append(m)
    
    daftar.append("M2 - ANTREAN DAN UNDO")
    daftar.append(Menu("kasir",
                        "STACK - POSTFIX (MESIN KASIR)",
                        "M2 - KASIR / STACK",
                        "Konversi infix menjadi postfix dan hitung hasilnya.",
                        "HITUNG TOTAL",
                        [
                            ("Ekspresi infix", "10 + 5 * 2", None,
                            "Contoh: (10 + 5) * 2")
                        ],
                        aksi.kasir))

    daftar.append(Menu("undo",
                        "STACK - UNDO",
                        "M2 - TUMPUKAN",
                        "Batalkan aksi terakhir.",
                        "UNDO",
                        [],
                        aksi.batalkan))

    daftar.append(Menu("redo",
                        "STACK - REDO",
                        "M2 - TUMPUKAN",
                        "Ulangi aksi yang sebelumnya dibatalkan.",
                        "REDO", [], aksi.ulangi))

    daftar.append(Menu("antrean_isi",
                        "QUEUE - ENQUEUE",
                        "M2 - ANTREAN",
                        "Masukkan pesanan berstatus ANTRE ke dalam antrean.",
                        "ENQUEUE",
                        [],
                        aksi.isi_fifo))

    daftar.append(Menu("antrean_layani",
                        "QUEUE - DEQUEUE FIFO",
                        "M2 - ANTREAN",
                        "Layani pesanan terdepan berdasarkan prinsip FIFO.",
                        "DEQUEUE FIFO",
                        [],
                        aksi.layani))

    daftar.append(Menu( "antrean_circular",
                        "QUEUE - DEQUEUE CIRCULAR",
                        "M2 - ANTREAN",
                        "Layani pesanan terdepan dari queue circular.",
                        "DEQUEUE CIRCULAR",
                        [],
                        aksi.layani))

                    
    
    daftar.append("M3 - LAPORAN TERURUT")
    daftar.append(Menu("laporan", "Laporan harian", "M3 - sort",
                       "Saring pesanan lalu urutkan. Sort O(n^2): persempit filter (maks "
                       + str(BATAS_SORT) + " baris).",
                       "BUAT LAPORAN",
                       [("Resto", "kedai-kopi", DAFTAR_RESTO, ""),
                        ("Status", "DONE", DAFTAR_STATUS, ""),
                        ("Jam awal", "11:00", None, "HH:MM atau HH:MM:SS"),
                        ("Jam akhir", "12:00", None, "HH:MM dihitung sampai detik ke-59"),
                        ("Urut menurut", "t_masuk", ("t_masuk", "harga"), ""),
                        ("Metode", "insertion", ("insertion", "selection", "bubble"), "")],
                       aksi.laporan_harian))
    daftar.append(Menu("laporan_cari", "Cari di laporan", "M3 - binary search",
                       "Binary search (kemunculan pertama) di laporan yang sudah terurut.",
                       "CARI",
                       [("Nilai dicari", "41376", None,
                         "t_masuk: detik atau HH:MM:SS | harga: angka")],
                       aksi.cari_laporan))
    return daftar

# ================================================================ widget

class Aplikasi:
    def __init__(pesan, root, daftar):
        pesan.root = root
        pesan.daftar = daftar
        pesan.menu_aktif = None
        pesan.vars = []
        pesan.tombol_menu = []
        root.title("2EZ4U Food Delivery")
        root.geometry("1140x740")
        root.minsize(900, 600)
        tk.Label(root, text="2EZ4U Food Delivery", bg="#1f3a5f", fg="white",
                 font=("Helvetica", 14, "bold"), anchor="w", padx=12, pady=8).pack(fill="x")
        # ---- bawah dipasang dulu supaya selalu terlihat
        bawah = tk.Frame(root)
        bawah.pack(side="bottom", fill="x", padx=8, pady=6)
        tk.Label(bawah, text="COMMAND", font=("Helvetica", 8, "bold"), anchor="w").pack(fill="x")
        kotak_log = tk.Frame(bawah)
        kotak_log.pack(fill="x")
        pesan.log = tk.Text(kotak_log, height=7, font=("Courier", 9), bg="#f6f6f6")
        sb_log = tk.Scrollbar(kotak_log, command=pesan.log.yview)
        pesan.log.configure(yscrollcommand=sb_log.set)
        sb_log.pack(side="right", fill="y")
        pesan.log.pack(side="left", fill="x", expand=True)
        tk.Button(bawah, text="Tutup", command=root.destroy).pack(anchor="w", pady=(6, 0))
        body = tk.Frame(root)
        body.pack(fill="both", expand=True, padx=8, pady=6)
        # ---- kiri: daftar menu (bisa digulir)
        kiri = tk.Frame(body, width=360)
        kiri.pack(side="left", fill="y")
        kiri.pack_propagate(False)
        kanvas = tk.Canvas(kiri, highlightthickness=0)
        sb = tk.Scrollbar(kiri, orient="vertical", command=kanvas.yview)
        isi = tk.Frame(kanvas)
        isi.bind("<Configure>", lambda e: kanvas.configure(scrollregion=kanvas.bbox("all")))
        kanvas.create_window((0, 0), window=isi, anchor="nw")
        kanvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        kanvas.pack(side="left", fill="both", expand=True)
        pesan._kanvas = kanvas
        kanvas.bind_all("<MouseWheel>", pesan._gulir)
        kanvas.bind_all("<Button-4>", pesan._gulir)
        kanvas.bind_all("<Button-5>", pesan._gulir)
        for item in daftar:
            if isinstance(item, str):
                tk.Label(isi, text=item, font=("Helvetica", 8, "bold"), fg="#555555",
                         anchor="w").pack(fill="x", pady=(10, 2))
            else:
                b = tk.Button(isi, text=item.judul, anchor="w", width=42,
                              command=lambda m=item: pesan.pilih(m))
                b.pack(fill="x", pady=1)
                pesan.tombol_menu.append(b)
        # ---- kanan: judul, form, hasil
        kanan = tk.Frame(body)
        kanan.pack(side="left", fill="both", expand=True, padx=(10, 0))
        pesan.lbl_judul = tk.Label(kanan, text="", font=("Helvetica", 12, "bold"), anchor="w")
        pesan.lbl_judul.pack(fill="x")
        pesan.lbl_desk = tk.Label(kanan, text="", fg="#666666", anchor="w", justify="left",
                                  wraplength=700)
        pesan.lbl_desk.pack(fill="x", pady=(0, 6))
        pesan.form = tk.Frame(kanan)
        pesan.form.pack(fill="x")
        pesan.btn_jalan = tk.Button(kanan, text="JALANKAN", command=pesan.jalankan_menu,
                                    bg="#1f3a5f", fg="white", padx=14)
        pesan.btn_jalan.pack(anchor="w", pady=8)
        kotak = tk.Frame(kanan)
        kotak.pack(fill="both", expand=True)
        pesan.hasil = tk.Text(kotak, font=("Courier", 10), wrap="none")
        sb_y = tk.Scrollbar(kotak, command=pesan.hasil.yview)
        sb_x = tk.Scrollbar(kanan, orient="horizontal", command=pesan.hasil.xview)
        pesan.hasil.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        sb_y.pack(side="right", fill="y")
        pesan.hasil.pack(side="left", fill="both", expand=True)
        sb_x.pack(fill="x")
        pesan.catat_log("siap. klik Load untuk memuat data.")
        for item in daftar:
            if not isinstance(item, str):
                pesan.pilih(item)
                break
    # ------------------------------------------------------------
    def _gulir(pesan, e):
        if e.num == 4:
            pesan._kanvas.yview_scroll(-1, "units")
        elif e.num == 5:
            pesan._kanvas.yview_scroll(1, "units")
        else:
            pesan._kanvas.yview_scroll(int(-1 * (e.delta / 120)) or -1, "units")
    def catat_log(pesan, teks):
        pesan.log.insert("end", teks + "\n")
        pesan.log.see("end")
    def set_hasil(pesan, teks):
        pesan.hasil.delete("1.0", "end")
        pesan.hasil.insert("1.0", teks)
    def pilih(pesan, menu):
        pesan.menu_aktif = menu
        pesan.lbl_judul.configure(text=menu.judul)
        pesan.lbl_desk.configure(text=menu.deskripsi)
        pesan.btn_jalan.configure(text=menu.tombol)
        for w in pesan.form.winfo_children():
            w.destroy()
        pesan.vars = []
        baris = 0
        for label, default, pilihan, hint in menu.fields:
            tk.Label(pesan.form, text=label, anchor="w").grid(row=baris, column=0, sticky="w", pady=2)
            var = tk.StringVar(value=default)
            if pilihan is not None:
                w = ttk.Combobox(pesan.form, textvariable=var, values=pilihan,
                                 state="readonly", width=24)
            else:
                w = tk.Entry(pesan.form, textvariable=var, width=40)
                w.bind("<Return>", lambda e: pesan.jalankan_menu())
            w.grid(row=baris, column=1, sticky="w", padx=8, pady=2)
            if hint != "":
                tk.Label(pesan.form, text=hint, fg="#888888", font=("Helvetica", 8),
                         anchor="w").grid(row=baris, column=2, sticky="w")
            pesan.vars.append(var)
            baris += 1
        pesan.set_hasil("")
    def jalankan_menu(pesan):
        menu = pesan.menu_aktif
        if menu is None:
            return
        nilai = []
        for v in pesan.vars:
            nilai.append(v.get())
        pesan.set_hasil("memproses ...")
        pesan.root.update_idletasks()
        try:
            modul, ms, teks = menu.handler(nilai)
        except Exception as galat:
            pesan.set_hasil("Error: " + str(galat))
            pesan.catat_log("%-18s -> %-22s %s" % (menu.kode, "error", str(galat).split("\n")[0]))
            return
        pesan.set_hasil(teks)
        pesan.catat_log("%-18s -> %-22s %9.2f ms" % (menu.kode, modul, ms))

# ================================================================ titik masuk

def jalankan(path_csv):
    root = tk.Tk()
    keadaan = Keadaan(path_csv)
    aksi = Aksi(keadaan)
    Aplikasi(root, buat_menu(aksi))
    root.mainloop()
if __name__ == "__main__":
    jalankan("data/pesanan.csv")