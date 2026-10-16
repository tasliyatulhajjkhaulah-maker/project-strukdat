
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


import os
import time
import tkinter as tk
from tkinter import ttk
 
from backend.m1 import (
    Array, LinkedList, muat_csv, buat_pesanan,
    I_OID, I_PELANGGAN, I_RESTO, I_MENU, I_HARGA, I_PRIORITAS,
    I_T_MASUK, I_T_SELESAI, I_STATUS,
    PRI_VIP, PRI_PRIORITAS, PRI_REGULER,
)
from backend.m2 import Queue, mesin_kasir
from backend import m3 as m3
 
JALUR_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "data", "pesanan.csv")
BATAS_NAIF = 2000      
BATAS_TAMPIL = 200    
 
 
def angka(n):
    return f"{n:,}".replace(",", ".")
 
 
def ms(detik):
    x = detik * 1000.0
    if x >= 1000:
        return ("%.2f s" % (x / 1000.0)).replace(".", ",")
    return ("%.2f ms" % x).replace(".", ",")
 
 
def jam(t):
    if t < 0:
        return "-"
    return "%02d:%02d:%02d" % ((t // 3600) % 24, (t % 3600) // 60, t % 60)
 
 
def rupiah(x):
    if isinstance(x, float) and x != int(x):
        return "Rp " + ("%.2f" % x).replace(".", ",")
    return "Rp " + angka(int(x))
 
 
def label_pri(p):
    if p == PRI_VIP:
        return "1 (VIP)"
    if p == PRI_PRIORITAS:
        return "2 (Prioritas)"
    if p == PRI_REGULER:
        return "3 (Reguler)"
    return str(p)
 
 
def detik_sekarang():
    t = time.localtime()
    return t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec
 
 
def detail(p):
    
    return [
        ["oid", p[I_OID]], ["pelanggan", p[I_PELANGGAN]], ["resto", p[I_RESTO]],
        ["menu", p[I_MENU]], ["harga", angka(p[I_HARGA])],
        ["prioritas", label_pri(p[I_PRIORITAS])], ["masuk", jam(p[I_T_MASUK])],
        ["selesai", jam(p[I_T_SELESAI])], ["status", p[I_STATUS]],
    ]
 
 
KOLOM_ANTREAN = ["#", "oid", "pelanggan", "resto", "menu", "masuk"]
 
 
def baris_antrean(daftar):
    baris = []
    for k in range(min(len(daftar), BATAS_TAMPIL)):
        p = daftar[k]
        baris.append([k + 1, p[I_OID], p[I_PELANGGAN], p[I_RESTO], p[I_MENU], jam(p[I_T_MASUK])])
    return baris
 
 
class Hasil:
    def __init__(self, pesan, kolom=None, baris=None, catatan="", modul="", waktu=0.0):
        self.pesan = pesan
        self.kolom = kolom if kolom is not None else []
        self.baris = baris if baris is not None else []
        self.catatan = catatan
        self.modul = modul
        self.waktu = waktu
 
 
class Menu:
 
    def __init__(self, label, perintah, judul, subjudul, tombol, field, aksi):
        self.label = label
        self.perintah = perintah
        self.judul = judul
        self.subjudul = subjudul
        self.tombol = tombol
        self.field = field
        self.aksi = aksi
 
 
class Sesi:
 
    def __init__(self):
        self.dimuat = False
        self.data = []                  
        self.larik = None                                   
        self.rantai = None        
        self.antrean = None       
        self.nomor_berikut = 1
        self.oid_terurut = None   
 
    def pastikan(self):
        if not self.dimuat:
            raise ValueError("Data belum dimuat. Klik menu 'Load' lebih dulu.")
 
    def muat(self, path):
        if not os.path.exists(path):
            raise ValueError("File tidak ditemukan: " + path +
                             "\nTaruh pesanan.csv di folder data/ atau jalankan: python scripts/buat_data.py")
        data = muat_csv(path)
        larik = Array()
        rantai = LinkedList()
        antre = Queue()
        maks = 0
        for p in data:
            larik.append(p)
            rantai.append(p)
            if p[I_STATUS] == "ANTRE":
                antre.muat_awal(p)
            try:
                n = int(p[I_OID][2:])
                if n > maks:
                    maks = n
            except ValueError:
                pass
        self.data, self.larik, self.rantai, self.antrean = data, larik, rantai, antre
        self.nomor_berikut = maks + 1
        self.oid_terurut = None
        self.dimuat = True
 
 
def _int(teks, nama, lo=None, hi=None):
    try:
        x = int(teks.strip().replace(".", ""))
    except ValueError:
        raise ValueError(nama + " harus berupa bilangan bulat.")
    if lo is not None and x < lo:
        raise ValueError("%s minimal %s." % (nama, angka(lo)))
    if hi is not None and x > hi:
        raise ValueError("%s maksimal %s." % (nama, angka(hi)))
    return x
 
 
def _norm_oid(teks):
    t = teks.strip().upper()
    if t.startswith("O-"):
        t = t[2:]
    if not t.isdigit():
        raise ValueError("Format oid: O-000001 atau cukup angkanya.")
    return "O-%06d" % int(t)
 
 
def aksi_load(s, v):
    t0 = time.perf_counter()
    s.muat(JALUR_DATA)
    dt = time.perf_counter() - t0
    pesan = [
        "%s baris dimuat dari data/pesanan.csv." % angka(len(s.data)),
        "Array: %s | Linked list: %s | Antrean ANTRE: naif %s, circular %s." % (
            angka(len(s.larik)), angka(len(s.rantai)),
            angka(len(s.antrean.naif)), angka(len(s.antrean.melingkar))),
        "Pesanan baru berikutnya akan bernomor " + "O-%06d." % s.nomor_berikut,
    ]
    baris = []
    for k in range(min(10, len(s.data))):
        p = s.data[k]
        baris.append([k, p[I_OID], p[I_PELANGGAN], p[I_RESTO], p[I_MENU], angka(p[I_HARGA]), p[I_STATUS]])
    return Hasil(pesan, ["#", "oid", "pelanggan", "resto", "menu", "harga", "status"], baris,
                 "Pratinjau 10 baris pertama. Data dimuat ke Array, Linked list, dan kedua antrean.",
                 "data - load", dt)
 
 
def _struktur(s, jenis):
    return s.larik if jenis == "array" else s.rantai
 
 
def _biaya(st, jenis):
    if jenis == "array":
        teks = "%s elemen digeser" % angka(st.geser_terakhir)
        if st.tumbuh_terakhir:
            teks += "; kapasitas penuh -> petak baru 2x, seluruh isi disalin"
        return teks
    return "%s simpul ditelusuri" % angka(st.langkah_terakhir)
 
 
def aksi_lihat(s, v, jenis):
    s.pastikan()
    st = _struktur(s, jenis)
    i = _int(v[0], "Indeks", 0, len(st) - 1)
    t0 = time.perf_counter()
    p = st.get(i)
    dt = time.perf_counter() - t0
    if jenis == "array":
        info = "Akses langsung lewat indeks: O(1), tanpa penelusuran."
    else:
        info = "%s simpul ditelusuri dari head: O(n)." % angka(st.langkah_terakhir)
    return Hasil(["Pesanan ke-%s (dari %s) dibuka." % (angka(i), angka(len(st))), info],
                 ["kolom", "isi"], detail(p),
                 "Bandingkan waktu menu ARRAY vs LINKEDLIST dengan indeks yang sama (coba 0 lalu 100000).",
                 "M1 - " + jenis, dt)
 
 
def aksi_tambah(s, v, jenis, tipe):
    s.pastikan()
    nama = v[0].strip()
    if nama == "":
        raise ValueError("Nama pelanggan tidak boleh kosong.")
    st = _struktur(s, jenis)
    pri = PRI_REGULER
    if tipe == "PRIORITAS":
        pri = PRI_PRIORITAS
    elif tipe == "VIP":
        pri = PRI_VIP
    p = buat_pesanan(s.nomor_berikut, nama, pri, t_masuk=detik_sekarang())
    s.nomor_berikut += 1
    t0 = time.perf_counter()
    if tipe == "REGULER":
        pos = st.tambah_reguler(p)
    elif tipe == "PRIORITAS":
        pos = st.tambah_prioritas(p)
    else:
        pos = st.tambah_vip(p)
    dt = time.perf_counter() - t0
    pesan = ["%s (%s) masuk di posisi %s dari %s." % (p[I_OID], tipe, angka(pos), angka(len(st))),
             _biaya(st, jenis)]
    mulai = max(0, pos - 3)
    baris = []
    tetangga = st.potong(mulai, 7)
    for k in range(len(tetangga)):
        q = tetangga[k]
        no = mulai + k
        tanda = "► " if no == pos else ""
        baris.append([tanda + str(no), q[I_OID], q[I_PELANGGAN], label_pri(q[I_PRIORITAS]),
                      q[I_RESTO], q[I_MENU]])
    return Hasil(pesan, ["#", "oid", "pelanggan", "prioritas", "resto", "menu"], baris,
                 "Tabel menampilkan tetangga posisi sisip (► = pesanan baru).",
                 "M1 - " + jenis, dt)
 
 
def aksi_hapus(s, v, jenis):
    s.pastikan()
    st = _struktur(s, jenis)
    i = _int(v[0], "Indeks", 0, len(st) - 1)
    t0 = time.perf_counter()
    p = st.hapus(i)
    dt = time.perf_counter() - t0
    pesan = ["%s dihapus dari posisi %s. Sisa %s pesanan." % (p[I_OID], angka(i), angka(len(st))),
             _biaya(st, jenis)]
    return Hasil(pesan, ["kolom", "isi"], detail(p),
                 "Hapus indeks 0 vs indeks besar pada ARRAY dan LINKEDLIST untuk melihat selisih biayanya.",
                 "M1 - " + jenis, dt)
 
 # M2
def aksi_postfix(s, v):
    ekspresi = v[0].strip()
    t0 = time.perf_counter()
    postfix, total, jejak = mesin_kasir(ekspresi)
    dt = time.perf_counter() - t0
    pesan = ["Struk   : " + ekspresi, "Postfix : " + " ".join(postfix), "TOTAL   : " + rupiah(total)]
    return Hasil(pesan, ["langkah", "token", "tindakan", "stack", "output"], jejak,
                 "Baris 1.x = tahap konversi, 2.x = tahap evaluasi. Tanda ( hanya mengatur stack dan "
                 "tidak pernah muncul di kolom output. Operand kanan selalu keluar lebih dulu.",
                 "M2 - stack", dt)
 
 
def _panjang(s):
    a = s.antrean
    return "Panjang antrean sekarang: naif %s, circular %s." % (angka(len(a.naif)), angka(len(a.melingkar)))
 
 
def _riwayat(s):
    return "Tumpukan undo %d, redo %d." % (len(s.antrean.undo), len(s.antrean.redo))
 
 
def aksi_enqueue(s, v):
    s.pastikan()
    nama = v[0].strip()
    if nama == "":
        raise ValueError("Nama pelanggan tidak boleh kosong.")
    p = buat_pesanan(s.nomor_berikut, nama, PRI_REGULER, t_masuk=detik_sekarang())
    s.nomor_berikut += 1
    t0 = time.perf_counter()
    s.antrean.enqueue(p)
    dt = time.perf_counter() - t0
    return Hasil([p[I_OID] + " masuk ke barisan paling belakang pada KEDUA antrean.",
                  _panjang(s) + " " + _riwayat(s)],
                 ["kolom", "isi"], detail(p),
                 "enqueue selalu menempel di belakang, jadi O(1) pada kedua versi. "
                 "Perbedaannya baru muncul saat dequeue.", "M2 - queue", dt)
 
 
def aksi_dequeue_naif(s, v):
    s.pastikan()
    k = _int(v[0], "Jumlah dequeue", 1, BATAS_NAIF)
    if k > len(s.antrean.naif):
        raise ValueError("Antrean naif hanya berisi %s pesanan." % angka(len(s.antrean.naif)))
    t0 = time.perf_counter()
    keluar, geser = s.antrean.dequeue_naif(k)
    dt = time.perf_counter() - t0
    pesan = ["%s pesanan keluar dari depan antrean naif." % angka(len(keluar)),
             "Total %s elemen digeser, rata-rata %s geseran per dequeue." % (
                 angka(geser), angka(geser // max(1, len(keluar)))),
             "Sisa antrean naif %s. %s" % (angka(len(s.antrean.naif)), _riwayat(s))]
    return Hasil(pesan, KOLOM_ANTREAN, baris_antrean(keluar),
                 "Mengambil indeks 0 memaksa seluruh sisa isi bergeser satu petak ke kiri, jadi O(n) setiap "
                 "dequeue. Bandingkan waktunya dengan DEQUEUE CIRCULAR pada jumlah yang sama.",
                 "M2 - queue naif", dt)
 
 
def aksi_dequeue_circular(s, v):
    s.pastikan()
    if len(s.antrean.melingkar) == 0:
        raise ValueError("Antrean circular kosong.")
    k = _int(v[0], "Jumlah dequeue", 1, len(s.antrean.melingkar))
    t0 = time.perf_counter()
    keluar, _ = s.antrean.dequeue_melingkar(k)
    dt = time.perf_counter() - t0
    q = s.antrean.melingkar
    pesan = ["%s pesanan keluar dari depan antrean circular." % angka(len(keluar)),
             "Tidak ada elemen yang digeser. front sekarang %s, rear %s, kapasitas %s." % (
                 angka(q.front), angka(q.rear), angka(q.kapasitas())),
             "Sisa antrean circular %s. %s" % (angka(len(q)), _riwayat(s))]
    return Hasil(pesan, KOLOM_ANTREAN, baris_antrean(keluar),
                 "Yang berpindah hanya penunjuk front (maju 1 langkah memakai modulo kapasitas); isi larik "
                 "tidak disentuh, jadi biayanya O(1) per dequeue.", "M2 - queue circular", dt)
 
 
def aksi_undo(s, v):
    s.pastikan()
    t0 = time.perf_counter()
    aksi = s.antrean.undo_last()
    dt = time.perf_counter() - t0
    if aksi is None:
        return Hasil(["Tumpukan undo kosong, tidak ada yang dibatalkan."], modul="M2 - stack", waktu=dt)
    jenis, target, daftar = aksi
    if jenis == "ENQUEUE":
        kepala = "Pembatalan enqueue: %s dikeluarkan lagi dari belakang." % daftar[0][I_OID]
        cat = "Kebalikan dari enqueue adalah membuang elemen paling belakang, pada kedua antrean."
    else:
        kepala = "Pembatalan dequeue: %s pesanan dikembalikan ke DEPAN antrean %s." % (angka(len(daftar)), target)
        cat = "Kebalikan dari dequeue: seluruh daftar dikembalikan ke DEPAN antrean (bukan ke belakang), urutan asli terjaga."
    return Hasil([kepala, _panjang(s) + " " + _riwayat(s)], KOLOM_ANTREAN, baris_antrean(daftar),
                 cat, "M2 - stack", dt)
 
 
def aksi_redo(s, v):
    s.pastikan()
    t0 = time.perf_counter()
    aksi = s.antrean.redo_last()
    dt = time.perf_counter() - t0
    if aksi is None:
        return Hasil(["Tumpukan redo kosong, tidak ada yang diulang."], modul="M2 - stack", waktu=dt)
    jenis, target, daftar = aksi
    if jenis == "ENQUEUE":
        kepala = "Enqueue dikerjakan lagi: %s masuk kembali ke belakang." % daftar[0][I_OID]
    else:
        kepala = "Dequeue dikerjakan lagi: %s pesanan keluar lagi dari antrean %s." % (angka(len(daftar)), target)
    return Hasil([kepala, _panjang(s) + " " + _riwayat(s)], KOLOM_ANTREAN, baris_antrean(daftar),
                 "Redo mengerjakan ULANG aksi aslinya, bukan kebalikannya, lalu mengembalikan catatan ke "
                 "tumpukan undo. Aksi baru apa pun mengosongkan tumpukan redo.", "M2 - stack", dt)
 

#M3 
def aksi_sort(s, v, algoritma):
    s.pastikan()
    jumlah = _int(v[0], "Jumlah baris", 1, len(s.data))
    nama_kunci = v[1]
    if algoritma == "insertion" and jumlah > m3.BATAS_INSERTION:
        raise ValueError("DITOLAK: batasnya %s baris untuk insertion sort, pakai merge sort untuk data penuh."
                         % angka(m3.BATAS_INSERTION))
    fk = m3.pilih_kunci(nama_kunci)
    A = m3.salin_awal(s.data, jumlah)
    pc = m3.Sorting()
    t0 = time.perf_counter()
    if algoritma == "insertion":
        m3.insertion_sort(A, fk, pc)
        hasil = A
    else:
        hasil = m3.merge_sort(A, fk, pc)
    dt = time.perf_counter() - t0
    baris = []
    for k in range(min(len(hasil), 100)):
        p = hasil[k]
        baris.append([k + 1, p[I_OID], angka(p[I_HARGA]), jam(p[I_T_SELESAI]), p[I_RESTO], p[I_MENU]])
    pesan = ["%s pesanan diurutkan menurut %s." % (angka(jumlah), nama_kunci),
             "%s perbandingan, %s pemindahan." % (angka(pc.banding), angka(pc.pindah))]
    if algoritma == "insertion":
        cat = ("Setiap elemen digeser mundur sampai menemukan tempatnya, jadi biayanya tumbuh kuadratik: "
               "lipat-duakan jumlah baris, perbandingan kira-kira empat kali lipat. Stabil (pakai >).")
        modul = "M3 - insertion sort"
    else:
        cat = ("Larik dibelah dua terus-menerus lalu potongan yang sudah terurut digabung (pakai <=, stabil). "
               "Kedalaman log n dan tiap tingkat O(n): perbandingan hanya ~dua kali saat n dilipatduakan.")
        modul = "M3 - merge sort"
    return Hasil(pesan, ["#", "oid", "harga", "selesai", "resto", "menu"], baris,
                 cat + " (Tabel: 100 baris pertama hasil.)", modul, dt)
 
 
def aksi_linear(s, v):
    s.pastikan()
    oid = _norm_oid(v[0])
    pc = m3.Sorting()
    t0 = time.perf_counter()
    idx = m3.linear_search(s.data, oid, m3.kunci_oid, pc)
    dt = time.perf_counter() - t0
    cat = "Setiap pesanan diperiksa satu per satu dari depan. Kasus terburuk menyentuh seluruh %s baris." % angka(len(s.data))
    if idx < 0:
        return Hasil(["%s tidak ditemukan. %s perbandingan." % (oid, angka(pc.banding))],
                     catatan=cat, modul="M3 - linear", waktu=dt)
    return Hasil(["Ditemukan pada indeks %s." % angka(idx), "%s perbandingan." % angka(pc.banding)],
                 ["kolom", "isi"], detail(s.data[idx]), cat, "M3 - linear", dt)
 
 
def aksi_binary(s, v):
    s.pastikan()
    oid = _norm_oid(v[0])
    pesan = []
    if s.oid_terurut is None:
        pb = m3.Sorting()
        tb = time.perf_counter()
        s.oid_terurut = m3.merge_sort(s.data, m3.kunci_oid, pb)
        pesan.append("Daftar terurut oid dibangun sekali dengan merge sort, %s (%s perbandingan)." % (
            ms(time.perf_counter() - tb), angka(pb.banding)))
    else:
        pesan.append("Daftar terurut oid sudah ada (dibangun sebelumnya, biaya tidak dihitung ulang).")
    pc = m3.Sorting()
    t0 = time.perf_counter()
    idx = m3.binary_search(s.oid_terurut, oid, m3.kunci_oid, pc)
    dt = time.perf_counter() - t0
    cat = ("Setiap perbandingan membuang separuh sisa daftar, jadi paling banyak ~%d langkah. "
           "Syaratnya daftar SUDAH terurut menurut kunci yang dicari (di sini terurut oid)." % (
               len(s.oid_terurut).bit_length()))
    if idx < 0:
        pesan.append("%s tidak ditemukan. %s perbandingan." % (oid, angka(pc.banding)))
        return Hasil(pesan, catatan=cat, modul="M3 - binary", waktu=dt)
    pesan.append("Ditemukan pada baris ke-%s dari %s baris." % (angka(idx + 1), angka(len(s.oid_terurut))))
    pesan.append("%s perbandingan, bandingkan dengan linear search." % angka(pc.banding))
    return Hasil(pesan, ["kolom", "isi"], detail(s.oid_terurut[idx]), cat, "M3 - binary", dt)
 
 
def _menu_m1(jenis, nama):
    ind = [("Indeks pesanan (0 = pertama)", "", "mulai dari 0 sampai panjang-1", None)]
    nm = [("Nama pelanggan", "Pelanggan Baru", "nama untuk pesanan yang akan dibuat", None)]
    p = jenis + "_"
    tipe = (("REGULER", "masuk barisan paling belakang"),
            ("PRIORITAS", "menyerobot ke tengah barisan"),
            ("VIP", "langsung ke urutan pertama"))
    hasil = [Menu(nama + " - LIHAT PESANAN", p + "get",
                  "%s: lihat pesanan ke-i" % nama.title(),
                  "Membuka detail satu pesanan. Array O(1), linked list O(n).", "LIHAT", ind,
                  lambda s, v, j=jenis: aksi_lihat(s, v, j))]
    for t, ket in tipe:
        hasil.append(Menu("%s - TAMBAH PESANAN %s" % (nama, t), p + "tambah_" + t.lower(),
                          "%s: pesanan %s, %s" % (nama.title(), t, ket),
                          "append: pesanan baru disisipkan sesuai jenisnya.", "TAMBAH", nm,
                          lambda s, v, j=jenis, tp=t: aksi_tambah(s, v, j, tp)))
    hasil.append(Menu(nama + " - HAPUS PESANAN", p + "hapus",
                      "%s: hapus pesanan ke-i" % nama.title(),
                      "Pesanan dicabut dari barisan. O(n) pada kedua struktur (geser / telusur).", "HAPUS", ind,
                      lambda s, v, j=jenis: aksi_hapus(s, v, j)))
    return hasil
 
 
def daftar_menu():
    m2 = [
        Menu("STACK - POSTFIX (MESIN KASIR)", "stack_postfix", "Stack: hitung struk lewat postfix",
             "Struk ditulis infix, lalu dihitung dua tahap dengan stack: tahap 1 infix menjadi postfix, "
             "tahap 2 postfix dievaluasi.", "HITUNG",
             [("Struk belanja (infix)", "( 3 * 12000 ) + ( 2 * 8500 ) - 5000",
               "angka, + - * / dan tanda kurung; pisahkan dengan spasi atau tidak", None)], aksi_postfix),
        Menu("STACK - UNDO", "stack_undo", "Stack: batalkan aksi antrean terakhir",
             "Mengambil catatan teratas tumpukan undo, lalu menjalankan kebalikannya. "
             "Aksi terakhirlah yang dibatalkan lebih dulu.", "UNDO", [], aksi_undo),
        Menu("STACK - REDO", "stack_redo", "Stack: kerjakan lagi aksi yang dibatalkan",
             "Mengambil catatan teratas tumpukan redo, lalu mengerjakan ulang aksi aslinya. "
             "Aksi baru apa pun mengosongkan tumpukan ini.", "REDO", [], aksi_redo),
        Menu("QUEUE - ENQUEUE", "queue_enqueue", "Queue: pesanan baru masuk ke belakang",
             "Menambah pesanan di ujung belakang kedua antrean sekaligus, yang naif maupun yang circular.",
             "ENQUEUE", [("Nama pelanggan", "Pelanggan Baru", "untuk pesanan yang akan dibuat", None)],
             aksi_enqueue),
        Menu("QUEUE - DEQUEUE NAIF", "queue_dequeue_naive", "Queue naif: ambil dari depan dengan menggeser isi",
             "Mengambil indeks 0 lalu menggeser seluruh sisa isi satu petak ke kiri. Biayanya O(n) setiap dequeue.",
             "DEQUEUE", [("Berapa kali dequeue", "1",
                          "sampai panjang antrean (maks %s); coba 1 lalu 100 untuk melihat bedanya" % angka(BATAS_NAIF), None)],
             aksi_dequeue_naif),
        Menu("QUEUE - DEQUEUE CIRCULAR", "queue_dequeue_circular", "Queue circular: ambil dari depan dengan memajukan penunjuk",
             "Hanya penunjuk front yang maju, memakai sisa bagi terhadap kapasitas. Isi larik tidak digeser sama sekali.",
             "DEQUEUE", [("Berapa kali dequeue", "1", "sampai panjang antrean; coba 1 lalu 100 untuk melihat bedanya", None)],
             aksi_dequeue_circular),
    ]
    m3_ = [
        Menu("SORT - INSERTION SORT", "insertion_sort", "Sort: insertion sort, O(n²)",
             "Setiap elemen digeser mundur sampai menemukan tempatnya. Sederhana, tetapi kerjanya tumbuh kuadratik.",
             "URUTKAN",
             [("Jumlah baris diurutkan", "1000",
               "diambil dari awal data; coba 1.000 lalu 2.000 lalu 4.000 (maks %s)" % angka(m3.BATAS_INSERTION), None),
              ("Diurutkan menurut", "harga", "oid (teks), harga (angka), selesai (waktu selesai)", list(m3.NAMA_KUNCI))],
             lambda s, v: aksi_sort(s, v, "insertion")),
        Menu("SORT - MERGE SORT", "merge_sort", "Sort: merge sort, O(n log n)",
             "Larik dibelah terus-menerus, lalu potongan yang sudah terurut disatukan kembali.", "URUTKAN",
             [("Jumlah baris diurutkan", "4000", "diambil dari awal data; boleh sampai seluruh data", None),
              ("Diurutkan menurut", "oid", "oid (teks), harga (angka), selesai (waktu selesai)", list(m3.NAMA_KUNCI))],
             lambda s, v: aksi_sort(s, v, "merge")),
        Menu("SEARCH - LINEAR SEARCH", "linear_search", "Search: linear search, O(n)",
             "Memeriksa pesanan satu per satu dari depan. Tidak menuntut data terurut.", "CARI",
             [("Nomor pesanan (oid)", "O-137442", "format O-000001 sampai O-200000", None)], aksi_linear),
        Menu("SEARCH - BINARY SEARCH", "binary_search", "Search: binary search, O(log n)",
             "Membuang separuh sisa daftar pada setiap perbandingan. Menuntut daftar yang sudah terurut menurut oid.",
             "CARI", [("Nomor pesanan (oid)", "O-137442", "format O-000001 sampai O-200000", None)], aksi_binary),
    ]
    return [
        ("DATA", [Menu("Load", "load", "Muat data", "Membaca data/pesanan.csv ke Array, Linked list, dan antrean.",
                       "LOAD", [], aksi_load)]),
        ("M1 - DATA PESANAN", _menu_m1("array", "ARRAY") + _menu_m1("linkedlist", "LINKEDLIST")),
        ("M2 - STACK DAN QUEUE", m2),
        ("M3 - SORT DAN SEARCH", m3_),
    ]
 
 
WARNA_HEADER = "#036060"
 
 
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("2EZ4U Food Delivery")
        self.geometry("1220x800")
        self.minsize(1000, 640)
        self.sesi = Sesi()
        self.grup = daftar_menu()
        self.semua = []
        for _, isi in self.grup:
            for m in isi:
                self.semua.append(m)
        self.aktif = None
        self.vars = []
        self.tombol_menu = []
        self.var_status = tk.StringVar(value="[siap]  klik Load untuk memuat data")
        self._gaya()
        self._bangun()
        self.pilih(0)
 
    #  gaya
    def _gaya(self):
        st = ttk.Style(self)
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        st.configure("Menu.TButton", anchor="w", padding=(6, 3), relief="flat", background="#f4f6fa")
        st.map("Menu.TButton", background=[("active", "#e3eaf6")])
        st.configure("Aktif.Menu.TButton", anchor="w", padding=(6, 3), background="#cfdcf2",
                     font=("TkDefaultFont", 9, "bold"))
        st.configure("Aksi.TButton", background=WARNA_HEADER, foreground="white", padding=(18, 6),
                     font=("TkDefaultFont", 9, "bold"))
        st.map("Aksi.TButton", background=[("active", "#3f5580")])
        st.configure("Treeview", rowheight=21, font=("TkFixedFont", 9))
        st.configure("Treeview.Heading", font=("TkDefaultFont", 9, "bold"))
 
    # susunan jendela
    def _bangun(self):
        header = tk.Frame(self, bg=WARNA_HEADER)
        header.pack(side="top", fill="x")
        tk.Label(header, text="2EZ4U Food Delivery", bg=WARNA_HEADER, fg="white",
                 font=("TkDefaultFont", 14, "bold"), padx=12, pady=8).pack(side="left")
 
        tk.Label(self, textvariable=self.var_status, anchor="w", bg=WARNA_HEADER, fg="white",
                 font=("TkFixedFont", 9), padx=10, pady=3).pack(side="bottom", fill="x")
 
        body = tk.Frame(self)
        body.pack(side="top", fill="both", expand=True)
 
        # menu kiri bisa di-scroll
        kiri = tk.Frame(body, width=275)
        kiri.pack(side="left", fill="y")
        kiri.pack_propagate(False)
        self.canvas = tk.Canvas(kiri, highlightthickness=0, bg="#f4f6fa")
        sb = ttk.Scrollbar(kiri, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        isi = tk.Frame(self.canvas, bg="#f4f6fa")
        self.canvas.create_window((0, 0), window=isi, anchor="nw", width=252)
        isi.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Enter>", lambda e: self._ikat_roda())
        self.canvas.bind("<Leave>", lambda e: self._lepas_roda())
 
        idx = 0
        for judul, daftar in self.grup:
            tk.Label(isi, text=judul, bg="#f4f6fa", fg="#34506e", anchor="w",
                     font=("TkDefaultFont", 8, "bold")).pack(fill="x", padx=6, pady=(10, 2))
            for m in daftar:
                b = ttk.Button(isi, text=m.label, style="Menu.TButton",
                               command=lambda i=idx: self.pilih(i))
                b.pack(fill="x", padx=6, pady=1)
                self.tombol_menu.append(b)
                idx += 1
 
        # sisi kanan
        kanan = ttk.Frame(body, padding=(12, 8))
        kanan.pack(side="left", fill="both", expand=True)
 
        self.lbl_judul = ttk.Label(kanan, text="", font=("TkDefaultFont", 11, "bold"))
        self.lbl_judul.pack(anchor="w")
        self.lbl_sub = tk.Label(kanan, text="", fg="#666666", justify="left", anchor="w",
                                font=("TkDefaultFont", 8), wraplength=800)
        self.lbl_sub.pack(fill="x", pady=(0, 6))
 
        self.form = ttk.Frame(kanan)
        self.form.pack(fill="x")
 
        ttk.Separator(kanan).pack(fill="x", pady=8)
 
        self.lbl_pesan = tk.Label(kanan, text="", justify="left", anchor="w", wraplength=800,
                                  font=("TkDefaultFont", 10))
        self.lbl_pesan.pack(fill="x")
 
        # tabel hasil
        kt = ttk.Frame(kanan)
        kt.pack(fill="both", expand=True, pady=(6, 4))
        self.tree = ttk.Treeview(kt, show="headings", height=10)
        vsb = ttk.Scrollbar(kt, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(kt, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)
 
        # catatan + COMMAND
        ttk.Label(kanan, text="COMMAND", font=("TkDefaultFont", 8, "bold")).pack(anchor="w")
        kc = ttk.Frame(kanan)
        kc.pack(fill="x")
        self.log = tk.Text(kc, height=6, font=("TkFixedFont", 9), state="disabled", wrap="none",
                           bg="#fbfbfb")
        lsb = ttk.Scrollbar(kc, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=lsb.set)
        lsb.pack(side="right", fill="y")
        self.log.pack(side="left", fill="x", expand=True)
 
        self.lbl_catatan = tk.Label(kanan, text="", bg="#fff8dc", fg="#444444", justify="left",
                                    anchor="w", wraplength=800, font=("TkDefaultFont", 8), padx=6, pady=4)
        self.lbl_catatan.pack(fill="x", pady=(6, 0))
 
        kanan.bind("<Configure>", self._atur_lebar)
 
    def _atur_lebar(self, e):
        w = max(300, e.width - 40)
        self.lbl_pesan.configure(wraplength=w)
        self.lbl_sub.configure(wraplength=w)
        self.lbl_catatan.configure(wraplength=w)
 
    #  scroll menu kiri
    def _ikat_roda(self):
        self.bind_all("<MouseWheel>", self._roda)
        self.bind_all("<Button-4>", self._roda)
        self.bind_all("<Button-5>", self._roda)
 
    def _lepas_roda(self):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")
 
    def _roda(self, e):
        if getattr(e, "num", 0) == 4:
            arah = -1
        elif getattr(e, "num", 0) == 5:
            arah = 1
        else:
            arah = -1 if e.delta > 0 else 1
        self.canvas.yview_scroll(arah * 2, "units")
 
    # pilih menu
    def pilih(self, i):
        m = self.semua[i]
        self.aktif = m
        for k, b in enumerate(self.tombol_menu):
            b.configure(style="Aktif.Menu.TButton" if k == i else "Menu.TButton")
        self.lbl_judul.configure(text=m.judul)
        self.lbl_sub.configure(text=m.subjudul)
        for w in self.form.winfo_children():
            w.destroy()
        self.vars = []
        for k, (label, default, hint, pilihan) in enumerate(m.field):
            kol = ttk.Frame(self.form)
            kol.grid(row=0, column=k, padx=(0, 16), sticky="nw")
            ttk.Label(kol, text=label, font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
            var = tk.StringVar(value=default)
            if pilihan:
                w = ttk.Combobox(kol, textvariable=var, values=pilihan, state="readonly", width=16)
            else:
                w = ttk.Entry(kol, textvariable=var, width=34 if k == 0 and len(default) > 14 else 22)
                w.bind("<Return>", lambda e: self.jalankan())
            w.pack(anchor="w")
            if hint:
                tk.Label(kol, text=hint, fg="#777777", font=("TkDefaultFont", 8), justify="left",
                         wraplength=250, anchor="w").pack(anchor="w")
            self.vars.append(var)
        ttk.Button(self.form, text=m.tombol, style="Aksi.TButton",
                   command=self.jalankan).grid(row=0, column=len(m.field), sticky="n", padx=8, pady=(16, 0))
        self._tampil_kosong()
 
    def _tampil_kosong(self):
        self.lbl_pesan.configure(text="", fg="black")
        self.lbl_catatan.configure(text="")
        self.tree.delete(*self.tree.get_children())
        self.tree.configure(columns=())
 
    # ---- menjalankan
    def jalankan(self):
        m = self.aktif
        nilai = [v.get() for v in self.vars]
        self.configure(cursor="watch")
        self.lbl_pesan.configure(text="Memproses...", fg="#555555")
        self.update_idletasks()
        try:
            h = m.aksi(self.sesi, nilai)
        except (ValueError, IndexError) as e:
            self.configure(cursor="")
            self.lbl_pesan.configure(text=str(e), fg="#b00020")
            self.tree.delete(*self.tree.get_children())
            return
        self.configure(cursor="")
        self._tampil(h)
        modul = h.modul if h.modul else m.perintah
        self.var_status.set("[%s]  %s" % (modul, ms(h.waktu)))
        self._catat(m.perintah, modul, h.waktu)
 
    def _tampil(self, h):
        self.lbl_pesan.configure(text="\n".join(h.pesan), fg="black")
        self.lbl_catatan.configure(text=h.catatan)
        self.tree.delete(*self.tree.get_children())
        kolom = tuple(h.kolom)
        self.tree.configure(columns=kolom)
        lebar = max(60, 760 // max(1, len(kolom)))
        for k in kolom:
            kecil = k in ("#", "langkah", "token")
            self.tree.heading(k, text=k)
            self.tree.column(k, width=60 if kecil else lebar, minwidth=40, anchor="w", stretch=not kecil)
        if "tindakan" in kolom:
            self.tree.column("tindakan", width=300, stretch=True)
        for r in h.baris:
            self.tree.insert("", "end", values=r)
 
    def _catat(self, perintah, modul, waktu):
        self.log.configure(state="normal")
        self.log.insert("1.0", "%-24s-> %-22s %s\n" % (perintah, modul, ms(waktu)))
        self.log.configure(state="disabled")
 
 
def jalankan():
    App().mainloop()
 
