
import csv
 
# Satu pesanan = tuple 9 kolom 
I_OID = 0
I_PELANGGAN = 1
I_RESTO = 2
I_MENU = 3
I_HARGA = 4
I_PRIORITAS = 5
I_T_MASUK = 6
I_T_SELESAI = 7  
I_STATUS = 8
 
PRI_VIP = 1
PRI_PRIORITAS = 2
PRI_REGULER = 3
 
 
def format_oid(nomor):
    return  f"o-{nomor : 06d}"  #"O-%06d" % nomor
 
#buat pesanan baru
def buat_pesanan(nomor, pelanggan, prioritas=PRI_REGULER,
                 resto="kafe-teknik", menu="roti-bakar", harga=12000, t_masuk=0):
    
    #kalau pesanan baru brari masuk ke status nya antre
    return (format_oid(nomor), pelanggan, resto, menu, harga, prioritas,
            t_masuk, -1, "ANTRE")
 
 #baca file csv
def muat_csv(path):
    hasil = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.reader(f):
            if len(r) < 9 or r[0].strip().lower() == "oid":
                continue  # header / baris rusak
            t_selesai = int(r[7]) if r[7].strip() != "" else -1
            hasil.append((r[0].strip(), r[1], r[2], r[3], int(r[4]), int(r[5]),
                          int(r[6]), t_selesai, r[8].strip()))
    return hasil
 
 
class Array:

    #default isi arry nya 
    def __init__(pesan, kapasitas=4):
        if kapasitas < 1:
            kapasitas = 1
        pesan._data = [None] * kapasitas
        pesan._n = 0
       # total elemen pesannya yang disalin pas kapasitanya digandakna
        pesan.salin = 0             
       # total elemen yang digeser (insert/hapus)
        pesan.geser = 0             
        pesan.geser_terakhir = 0
        pesan.tumbuh_terakhir = False
 
    def __len__(pesan):
        return pesan._n
 
    def kapasitas(pesan):
        return len(pesan._data)
 
    def __getitem__(pesan, i):
        return pesan._data[i]
 
    def __setitem__(pesan, i, v):
        pesan._data[i] = v
 
    def _cek(pesan, i):
        if i < 0 or i >= pesan._n:
            raise IndexError("indeks %d di luar rentang 0..%d" % (i, pesan._n - 1))


    #buat lipat gandaikapasitas kalau kapasitas awal udah penuh
    def _grow(pesan):
        baru = [None] * (len(pesan._data) * 2)
        for i in range(pesan._n):
            baru[i] = pesan._data[i]
        pesan.salin += pesan._n
        pesan._data = baru
        pesan.tumbuh_terakhir = True
 
    def _mulai_op(pesan):
        pesan.geser_terakhir = 0
        pesan.tumbuh_terakhir = False
 
   # TAMBAH DAN KURANG PESANANNYA
   # nambah pesanan di belakang
    def append(pesan, v):
        pesan._mulai_op()
        if pesan._n == len(pesan._data):
            pesan._grow()
        pesan._data[pesan._n] = v
        pesan._n += 1
 
    # nambah pesanan sesuai indeks yang di input   
    def insert(pesan, i, v):
        if i < 0 or i > pesan._n:
            raise IndexError("posisi insert %d di luar rentang 0..%d" % (i, pesan._n))
      
        pesan._mulai_op()
        if pesan._n == len(pesan._data):
            pesan._grow()
     
        g = 0
        for j in range(pesan._n, i, -1):
            pesan._data[j] = pesan._data[j - 1]
            g += 1
        pesan._data[i] = v
        pesan._n += 1
        pesan.geser_terakhir = g
        pesan.geser += g

    #baca pesanan yang di i
    def get(pesan, i):
        pesan._cek(i)
        return pesan._data[i]

    #hapus pesanan berdasarkan indeks
    def remove_i(pesan, i):
        pesan._cek(i)
        pesan._mulai_op()
        v = pesan._data[i]

        g = 0
        for j in range(i, pesan._n - 1):
            pesan._data[j] = pesan._data[j + 1]
            g += 1
        pesan._data[pesan._n - 1] = None
        pesan._n -= 1
        pesan.geser_terakhir = g
        pesan.geser += g
        return v

    #buat hapus pesanan terakhir
    def pop(pesan):
        if pesan._n == 0:
            raise IndexError("larik kosong")
        pesan._mulai_op()
        pesan._n -= 1
        v = pesan._data[pesan._n]
        pesan._data[pesan._n] = None
        return v

    #nambahin pesanan beberapa sekaligus di depan
    def sisip_depan(pesan, daftar):
        k = len(daftar)
        if k == 0:
            return
        pesan._mulai_op()
        while pesan._n + k > len(pesan._data):
            pesan._grow()
        for j in range(pesan._n - 1, -1, -1):
            pesan._data[j + k] = pesan._data[j]
        for t in range(k):
            pesan._data[t] = daftar[t]
        pesan.geser_terakhir = pesan._n
        pesan.geser += pesan._n
        pesan._n += k
 
    # nambahin pesanan reguler ke paling belakang
    def tambah_reguler(pesan, p):
        pesan.append(p)
        return pesan._n - 1

    #nambahin pesanan prioritas ke antrean tengah
    def tambah_prioritas(pesan, p):
        pos = pesan._n // 2
        pesan.insert(pos, p)
        return pos

    #nambahin pesanan VIP ke paling depan antrean
    def tambah_vip(pesan, p):
        pesan.insert(0, p)
        return 0

    # hapus pesanan, jadi manggil remove_i buat ngapus 
    def hapus(pesan, i):
        return pesan.remove_i(i)

    #manggil sebagian pesanan buat di tampilin
    def potong(pesan, mulai, jumlah):
        hasil = []
        akhir = mulai + jumlah
        if akhir > pesan._n:
            akhir = pesan._n
        for i in range(mulai, akhir):
            hasil.append(pesan._data[i])
        return hasil
 
 
# LINKEDLIST

# node buat si linkedlist biar mudah
class Node:
    __slots__ = ("nilai", "next")
 
    def __init__(pesan, nilai):
        pesan.nilai = nilai
        pesan.next = None
 
 
class LinkedList:
 
    def __init__(pesan):
        pesan.head = None
        pesan.tail = None
        pesan._n = 0
        pesan.langkah = 0           
        pesan.langkah_terakhir = 0
 
    def __len__(pesan):
        return pesan._n
 
    def _cek(pesan, i):
        if i < 0 or i >= pesan._n:
            raise IndexError("indeks %d di luar rentang 0..%d" % (i, pesan._n - 1))
 
    def _node_ke(pesan, i):
        cur = pesan.head
        for _ in range(i):
            cur = cur.next
        pesan.langkah_terakhir += i
        pesan.langkah += i
        return cur

    # tambah pesanan di paling belakang, ini buat reguler
    def append(pesan, v):
        pesan.langkah_terakhir = 0
        baru = Node(v)
        if pesan.tail is None:
            pesan.head = baru
        else:
            pesan.tail.next = baru
        pesan.tail = baru
        pesan._n += 1

    # nambah pesanan di depan
    def prepend(pesan, v):
        pesan.langkah_terakhir = 0
        baru = Node(v)
        baru.next = pesan.head
        pesan.head = baru
        if pesan.tail is None:
            pesan.tail = baru
        pesan._n += 1

    #nambah pesanan sesuai indeks yang di input
    def insert(pesan, i, v):
        if i < 0 or i > pesan._n:
            raise IndexError("posisi sisip %d di luar rentang 0..%d" % (i, pesan._n))
       
        if i == 0:
            pesan.prepend(v)
            return
       
        if i == pesan._n:
            pesan.append(v)
            return
       
        pesan.langkah_terakhir = 0
        sebelum = pesan._node_ke(i - 1)
        baru = Node(v)
        baru.next = sebelum.next
        sebelum.next = baru
        pesan._n += 1
 
    def get(pesan, i):
        pesan._cek(i)
        pesan.langkah_terakhir = 0
        return pesan._node_ke(i).nilai

    # hapus pesanannya
    def remove_i(pesan, i):
        pesan._cek(i)
        pesan.langkah_terakhir = 0
        if i == 0:
            target = pesan.head
            pesan.head = target.next
            if pesan.head is None:
                pesan.tail = None
        else:
            sebelum = pesan._node_ke(i - 1)
            target = sebelum.next
            sebelum.next = target.next
            if target is pesan.tail:
                pesan.tail = sebelum
        pesan._n -= 1
        return target.nilai
 
    #tambah pesanan reguler ke paling belakang
    def tambah_reguler(pesan, p):
        pesan.append(p)
        return pesan._n - 1

    #tambah pesanan priotitas ke antrian tengah
    def tambah_prioritas(pesan, p):
        pos = pesan._n // 2
        pesan.insert(pos, p)
        return pos

    #tambah pesanan VIP ke paling depan
    def tambah_vip(pesan, p):
        pesan.prepend(p)
        return 0
 
    def hapus(pesan, i):
        return pesan.remove_i(i)

    # tampilin sebagian pesanan
    def potong(pesan, mulai, jumlah):
        hasil = []
        cur = pesan.head
        for _ in range(mulai):
            if cur is None:
                break
            cur = cur.next
      
        k = 0
        while cur is not None and k < jumlah:
            hasil.append(cur.nilai)
            cur = cur.next
            k += 1
        return hasil











    
