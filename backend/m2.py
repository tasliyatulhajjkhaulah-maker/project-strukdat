
from .m1 import Array, I_OID
 

##LIFO
class Stack:
    #manggil fungsi yang ada di array
    def __init__(pesan):
        pesan._a = Array()

    #nambahin pesanan jadi paling atas 
    def push(pesan, x):
        pesan._a.append(x)


    # hapus pesanan, brarti yang paling atas karena stack
    def pop(pesan):
        if len(pesan._a) == 0:
            raise IndexError("tumpukan kosong")
        return pesan._a.pop()

    def peek(pesan):
        if len(pesan._a) == 0:
            raise IndexError("tumpukan kosong")
        return pesan._a.get(len(pesan._a) - 1)

    # kalau kosong bararti balik mulai isi dari jumalh pesanan di a
    def kosong(pesan):
        return len(pesan._a) == 0

    #buat tau jumlah elemen di a
    def __len__(pesan):
        return len(pesan._a)
 
    def isi(pesan):
        return pesan._a.potong(0, len(pesan._a))
 
    def kosongkan(pesan):
        while len(pesan._a) > 0:
            pesan._a.pop()
 

# buat mesin kasir
OPERATOR = ("+", "-", "*", "/")

 # menentukan tingkat priotitas dari operator
def _prio(op):
    return 2 if (op == "*" or op == "/") else 1
 
# buat cek token diawali angka atau desimal
def _adalah_angka(tok):
    c = tok[0]
    return ("0" <= c <= "9") or c == "."
 
# bikin tokennya buat diproses ke postfix
def tokenisasi(ekspresi):
    token = []
    i = 0
    n = len(ekspresi)
  
    while i < n:
        c = ekspresi[i]
        if c == " " or c == "\t":
            i += 1
        elif c in "+-*/()":
            token.append(c)
            i += 1
        elif ("0" <= c <= "9") or c == ".":
            j = i
            while j < n and (("0" <= ekspresi[j] <= "9") or ekspresi[j] == "."):
                j += 1
            token.append(ekspresi[i:j])
            i = j
        else:
            raise ValueError("karakter tidak dikenal: '%s'" % c)
    return token
 
#ubah stack jadi teks
def _teks_stack(t):
    isi = t.isi()
    if len(isi) == 0:
        return "kosong"
    return " ".join([str(x) for x in isi])
 
# ubah float ke int terus jadi teks
def _teks(x):
    if isinstance(x, float) and x == int(x):
        return str(int(x))
    return str(x)
 
# operasi infix kepostfix
def ke_postfix(ekspresi, jejak=None):
    token = tokenisasi(ekspresi)
    if len(token) == 0:
        raise ValueError("ekspresi kosong")
    ops = Stack()
    keluar = []
    no = 0
 
    def catat(tok, tindakan, label=None):
        nonlocal no
        no += 1
        if jejak is not None:
            nama = label if label is not None else str(no)
            jejak.append(["1." + nama, tok, tindakan, _teks_stack(ops), " ".join(keluar)])
 
    for tok in token:
        if _adalah_angka(tok):
            keluar.append(tok)
            catat(tok, "operand, langsung ke output")
        elif tok == "(":
            ops.push(tok)
            catat(tok, "push ( ke stack")
        elif tok == ")":
            diambil = []
            while (not ops.kosong()) and ops.peek() != "(":
                x = ops.pop()
                keluar.append(x)
                diambil.append(x)
            if ops.kosong():
                raise ValueError("kurung tutup tanpa pasangan")
            ops.pop()  # buang '('
            ket = ("pop sampai ( : " + " ".join(diambil) + ", lalu buang (") if diambil \
                else "pop sampai (, lalu buang ("
            catat(tok, ket)
        else:  # operator
            diambil = []
            while (not ops.kosong()) and ops.peek() != "(" and _prio(ops.peek()) >= _prio(tok):
                x = ops.pop()
                keluar.append(x)
                diambil.append(x)
            ops.push(tok)
            if diambil:
                catat(tok, "pop " + " ".join(diambil) + " (sama/lebih kuat), push " + tok)
            else:
                catat(tok, "push " + tok)
 
    sisa = []
    while not ops.kosong():
        x = ops.pop()
        if x == "(":
            raise ValueError("kurung buka ga ditutup")
        keluar.append(x)
        sisa.append(x)
    catat("akhir", "pop sisa stack: " + (" ".join(sisa) if sisa else "-"), label="akhir")
    return keluar
 
 
def _ke_angka(tok):
    try:
        return float(tok) if "." in tok else int(tok)
    except ValueError:
        raise ValueError("angka tidak valid: " + tok)
 
 
def _terapkan(op, a, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if b == 0:
        raise ValueError("pembagian dengan nol")
    if isinstance(a, int) and isinstance(b, int) and a % b == 0:
        return a // b
    return a / b
 
 
def hitung(postfix, jejak=None):
    if isinstance(postfix, str):
        postfix = tokenisasi(postfix)
    st = Stack()
    no = 0
    for tok in postfix:
        no += 1
        if tok in OPERATOR:
            if len(st) < 2:
                raise ValueError("ekspresi tidak valid (operand kurang)")
            b = st.pop()
            a = st.pop()
            r = _terapkan(tok, a, b)
            st.push(r)
            ket = "pop %s dan %s -> %s%s%s = %s" % (_teks(b), _teks(a), _teks(a), tok, _teks(b), _teks(r))
            if jejak is not None:
                jejak.append(["2.%d" % no, tok, ket, _teks_stack(st), _teks(r)])
        elif tok != "(" and tok != ")" and _adalah_angka(tok):
            st.push(_ke_angka(tok))
            if jejak is not None:
                jejak.append(["2.%d" % no, tok, "operand, push " + tok, _teks_stack(st), ""])
        else:
            raise ValueError("token tidak valid pada postfix: " + tok)
    if len(st) != 1:
        raise ValueError("ekspresi tidak valid (operator kurang)")
    return st.pop()
 
 
def mesin_kasir(ekspresi):
    jejak = []
    postfix = ke_postfix(ekspresi, jejak)
    total = hitung(postfix, jejak)
    return postfix, total, jejak
 
#Antrean
class QueueNaif:
 
    def __init__(pesan):
        pesan._a = Array()
        pesan.total_geser = 0
 
    def __len__(pesan):
        return len(pesan._a)
 
    def kapasitas(pesan):
        return pesan._a.kapasitas()

   #nambah pesanan di belakang
    def enqueue(pesan, x):
        pesan._a.append(x)

   #hapus antrean paling depan
    def dequeue(pesan):
        if len(pesan._a) == 0:
            return None
        x = pesan._a.remove_i(0)
        pesan.total_geser += pesan._a.geser_terakhir
        return x

    #hapus beberapa pesanan di depan
    def dequeue_banyak(pesan, k):
        keluar = []
        geser = 0
        for _ in range(k):
            if len(pesan._a) == 0:
                break
            keluar.append(pesan._a.remove_i(0))
            geser += pesan._a.geser_terakhir
        pesan.total_geser += geser
        return keluar, geser

    #hapus antrean terakhir
    def pop_belakang(pesan):
        if len(pesan._a) == 0:
            return None
        return pesan._a.pop()

    # nambahin pesanan di depan
    def sisip_depan(pesan, daftar):
        pesan._a.sisip_depan(daftar)
        pesan.total_geser += pesan._a.geser_terakhir
 
    def isi(pesan):
        return pesan._a.potong(0, len(pesan._a))
 

# front sama rear nyambung
class QueueCircular:
 
    def __init__(pesan, kapasitas=1024):
        if kapasitas < 1:
            kapasitas = 1
        pesan._data = [None] * kapasitas
        pesan.front = 0
        pesan.rear = 0
        pesan.count = 0
        pesan.total_geser = 0   
 
    def __len__(pesan):
        return pesan.count
 
    def kapasitas(pesan):
        return len(pesan._data)
 
    def kosong(pesan):
        return pesan.count == 0
 
    def _tumbuh(pesan):
        K = len(pesan._data)
        baru = [None] * (K * 2)
        for i in range(pesan.count):
            baru[i] = pesan._data[(pesan.front + i) % K]
        pesan._data = baru
        pesan.front = 0
        pesan.rear = pesan.count

    # tambah pesanan ke paling belakang
    def enqueue(pesan, x):
        if pesan.count == len(pesan._data):
            pesan._tumbuh()
        pesan._data[pesan.rear] = x
        pesan.rear = (pesan.rear + 1) % len(pesan._data)
        pesan.count += 1


    # hapus pesanan paling depan
    def dequeue(pesan):
        if pesan.count == 0:
            return None
        x = pesan._data[pesan.front]
        pesan._data[pesan.front] = None
        pesan.front = (pesan.front + 1) % len(pesan._data)
        pesan.count -= 1
        return x

   
    def dequeue_banyak(pesan, k):
        keluar = []
        for _ in range(k):
            if pesan.count == 0:
                break
            keluar.append(pesan.dequeue())
        return keluar, 0

    # hapus pesanan di belakang
    def pop_belakang(pesan):
        if pesan.count == 0:
            return None
        K = len(pesan._data)
        pesan.rear = (pesan.rear - 1) % K
        x = pesan._data[pesan.rear]
        pesan._data[pesan.rear] = None
        pesan.count -= 1
        return x


    #nambahin pesanan ke depan
    def sisip_depan(pesan, daftar):
        for t in range(len(daftar) - 1, -1, -1):
            if pesan.count == len(pesan._data):
                pesan._tumbuh()
            pesan.front = (pesan.front - 1) % len(pesan._data)
            pesan._data[pesan.front] = daftar[t]
            pesan.count += 1

    # buat baca pesanannya sesuai antrean 
    def isi(pesan):
        K = len(pesan._data)
        hasil = []
        for i in range(pesan.count):
            hasil.append(pesan._data[(pesan.front + i) % K])
        return hasil
 
 # hasil antrean dari naif sama circular
class Queue:
   
    def __init__(pesan):
        pesan.naif = QueueNaif()
        pesan.melingkar = QueueCircular()
        pesan.undo = Stack()
        pesan.redo = Stack()
 
    def muat_awal(pesan, p):
        pesan.naif.enqueue(p)
        pesan.melingkar.enqueue(p)
 
    def enqueue(pesan, p):
        pesan.naif.enqueue(p)
        pesan.melingkar.enqueue(p)
        pesan.undo.push(("ENQUEUE", "", [p]))
        pesan.redo.kosongkan()      

    def _antrean(pesan, target):
        return pesan.naif if target == "naif" else pesan.melingkar
 
    def dequeue_naif(pesan, k):
        keluar, geser = pesan.naif.dequeue_banyak(k)
        if keluar:
            pesan.undo.push(("DEQUEUE", "naif", keluar))
            pesan.redo.kosongkan()
        return keluar, geser
 
    def dequeue_melingkar(pesan, k):
        keluar, geser = pesan.melingkar.dequeue_banyak(k)
        if keluar:
            pesan.undo.push(("DEQUEUE", "circular", keluar))
            pesan.redo.kosongkan()
        return keluar, geser
 
    def undo_last(pesan):
        if pesan.undo.kosong():
            return None
        aksi = pesan.undo.pop()
        jenis, target, daftar = aksi
        if jenis == "ENQUEUE":
            pesan.naif.pop_belakang()
            pesan.melingkar.pop_belakang()
        else:
            pesan._antrean(target).sisip_depan(daftar)
        pesan.redo.push(aksi)
        return aksi
 
    def redo_last(pesan):
        if pesan.redo.kosong():
            return None
        aksi = pesan.redo.pop()
        jenis, target, daftar = aksi
        if jenis == "ENQUEUE":
            pesan.naif.enqueue(daftar[0])
            pesan.melingkar.enqueue(daftar[0])
        else:
            pesan._antrean(target).dequeue_banyak(len(daftar))
        pesan.undo.push(aksi)
        return aksi
 
    def history(pesan):
        hasil = []
        for jenis, target, daftar in pesan.undo.isi():
            if jenis == "ENQUEUE":
                hasil.append("ENQUEUE " + daftar[0][I_OID])
            else:
                hasil.append("DEQUEUE %s x%d" % (target, len(daftar)))
        return hasil
 
    def stats(pesan):
        return [
            ("queue_len_naif", len(pesan.naif)),
            ("queue_len_circular", len(pesan.melingkar)),
            ("queue_capacity", pesan.melingkar.kapasitas()),
            ("total_geser_naif", pesan.naif.total_geser),
            ("total_geser_circular", pesan.melingkar.total_geser),
            ("undo_depth", len(pesan.undo)),
            ("redo_depth", len(pesan.redo)),]






    
