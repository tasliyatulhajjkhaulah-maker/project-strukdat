import csv
OID, PELANGGAN,RESTO, MENU, HARGA, PRIORITAS, T_MASUK_DETIK, T_SELESAI_DETIK, STATUS = range (9)

KATEGORI_VIP = 0
KATEGORI_PRIORITAS = 1
KATEGORI_REGULER = 2

def baris (path) : 
    with open ( path, newline ="", encoding="utf-8") as file :
        r = csv.reader (file)
        next (r,None)                  # skip header

        for p in r :
            yield (p[0], p[1], p[2], p[3], int(p[4]), int(p[5]), int(p[6]) if p[6] else None, int(p[7]) if p[7] else None, p[8] )

def jam (detik) :
    h = detik // 3600
    m = (detik % 3600) // 60
    s = detik % 60
    return str(h).zfill(2) + ":" + str(m).zfill(2) + ":" + str(s).zfill(2)

def jenis_pesanan(jenis) :
    if jenis == KATEGORI_VIP :
        return "KATEGORI_VIP"
    if jenis == PRIORITAS :
        return "PRIORITAS"
    return "REGULER"

def teks(pesanan) :
    return (pesanan[OID], + "|" + pesanan[PELANGGAN], + "|" + pesanan[RESTO], + "|" + pesanan[MENU], + "| Rp" +
            str(pesanan[HARGA]), + "|" + jenis_pesanan(pesanan[PRIORITAS]), + "|" + jam(pesanan[T_MASUK_DETIK]), + 
            + "|" + pesanan[STATUS])


def detail_pesanan(pesanan):
    selesai = "-"
    if pesanan[T_SELESAI_DETIK] is not None:
        selesai = jam(pesanan[T_SELESAI_DETIK])
    return ("oid        : " + pesanan[OID] + "\n"
            + "pelanggan  : " + pesanan[PELANGGAN] + "\n"
            + "resto      : " + pesanan[RESTO] + "\n"
            + "menu       : " + pesanan[MENU] + "\n"
            + "harga      : Rp" + str(pesanan[HARGA]) + "\n"
            + "prioritas  : " + jenis_pesanan(pesanan[PRIORITAS]) + "\n"
            + "masuk      : " + jam(pesanan[T_MASUK_DETIK]) + "\n"
            + "selesai    : " + selesai + "\n"
            + "status     : " + pesanan[STATUS])
 
 
def buat_pesanan(nama, jenis, nomor, t_masuk, resto="-", menu="-", harga=0):
    """Membuat tuple pesanan baru dari form UI (yang diisi user hanya nama).
 
    jenis   : JENIS_VIP / JENIS_PRIORITAS / JENIS_REGULER
    nomor   : nomor urut oid berikutnya (dipegang UI, mulai 200001)
    t_masuk : detik sejak tengah malam
    """
    oid = "O-" + str(nomor).zfill(6)
    return (oid, nama, resto, menu, harga, jenis, t_masuk, None, "ANTRE")
    
    

class array :                                  
    def __init__ (pesan) :                  
        pesan.cap = 4                            #pesan.cap itu kapasitas array nya
        pesan.size = 0                           #pesan.size itu elemen yang ada dalm kapasitas arraynya
        pesan.data = [None] * pesan.cap          #pesan.data tempat penyimpana elemen

    def _grow (pesan) :
        baru = [None] * (pesan.cap*2)

        for i in range(pesan.size) :
            baru[i] = pesan.data[i] 
        pesan.data = baru
        pesan.cap*=2

    def insert (pesan, i, n) :
        if i<0 or i>pesan.size :
            raise IndexError()
        
        if pesan.size == pesan.cap :
           pesan._grow()

        for x in range (pesan.size, i, -1) :
            pesan.data[x] = pesan.data[x-1]
        pesan.data[i] = n

        pesan.size += 1

    def append(pesan, n) :
            pesan.insert (pesan.size, n)

    def get(pesan, i) :
        if i<0 or i>=pesan.size :
            raise IndexError()
        
        return pesan.data[i]

    def remove (pesan, i) :
        if i<0 or i>=pesan.size :
            raise IndexError()
        
        n = pesan.data[i]
        for x in range(i, pesan.size - 1) :
            pesan.data[x] = pesan.data[x +1]
        pesan.data[pesan.size -1] = None
        pesan.size -=1
        return n


class Linkedlist :
    def __init__(pesan) :
         pesan.head = pesan.tail = None
         pesan.size = 0

    def append (pesan,n) :
        node = {"n" : n, "next" : None}

        if pesan.head is None :
           pesan.head = pesan.tail = node
        else :
            pesan.tail["next"] = node
            pesan.tail = node

        pesan.size += 1

    def prepend (pesan, n) :
        node = {"n" : n, "next" : pesan.head}
        pesan.head = node

        if pesan.tail is None :
            pesan.tail = node

        pesan.size += 1

    def insert (pesan, i, n) :
        if i<0 or i>pesan.size :
            raise IndexError()
        
        if i == 0 :
           return pesan.prepend(n)
        
        if i == pesan.size :
           return pesan.append(n)
        
        cur = pesan.head
        for _ in range (i -1) :
             cur = cur["next"]
        node = {"n" : n, "next" : cur["next"]}
        cur["next"] = node

        pesan.size +=1   

    def get (pesan, i) :
        if i<0 or i>=pesan.size :
            raise IndexError()
        
        cur = pesan.head
        for _ in range(i) :
            cur = cur["next"]

        return cur["n"]


    def remove(pesan, i) :
        if i<0 or i>=pesan.size :
            raise IndexError()
        
        if i == 0 :
            target = pesan.head
            pesan.head = target["next"]

            if pesan.head is None :        # brarti pesanannya kosong
                pesan.tail = None

        else :
            prev = pesan.head
            for _ in range(i - 1) :
                prev = prev["next"]
                
            target = prev["next"]
            prev["next"] = target["next"]

            if target is pesan.tail :     #kalau yang di remove data paling terakhir
                pesan.tail = prev    

        pesan.size -= 1

        return target["n"]

def muat(path, arr, ll) :
    jumlah = 0
    for p in baris (path) :
        arr.append(p)
        ll.append(p)
        jumlah += 1
    return jumlah

def tambah(struktur, pesanan) :
    jenis = pesanan[PRIORITAS]

    if jenis == KATEGORI_REGULER: 
        struktur.append(pesanan)

    elif jenis == KATEGORI_PRIORITAS :
        struktur.insert(struktur.size // 2, pesanan)

    elif jenis == KATEGORI_VIP :
        struktur.insert(0, pesanan)
    else :
        raise ValueError()

