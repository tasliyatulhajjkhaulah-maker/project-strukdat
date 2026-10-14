import re 
from .m1 import array, STATUS, OID, tambah

class Queue :
    def __init__(pesan, cap = 8) :
        pesan.cap = cap
        pesan.data = [None]*pesan.cap
        pesan.head = 0
        pesan.size = 0

    def kosong (pesan) :
        return pesan.size == 0

    def _grow(pesan) :
        baru = [None] * (pesan.cap*2)

        for i in range (pesan.size) :
            baru[i] = pesan.data[(pesan.head + i) % pesan.cap]
        pesan.data = baru 
        pesan.cap *= 2
        pesan.head = 0
        
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
    def enqueue (pesan, n):
        if pesan.size == pesan.cap :
            pesan._grow()

        i =(pesan.head + pesan.size) % pesan.cap
        pesan.data[i] = n

        pesan.size +=1

    def dequeue (pesan) :
        if pesan.size == 0:
            raise IndexError()

        n = pesan.data[pesan.head]
        pesan.data[pesan.head] = None
        pesan.head = (pesan.head + 1) % pesan.cap

        pesan.size -= 1

        return n

    def enqueue_depan(pesan, n) :
        if pesan.size == pesan.cap :
            pesan._grow()

        pesan.head = (pesan.head - 1) % pesan.cap
        pesan.data[pesan.head] = n

        pesan.size += 1


    def intip (pesan) :
        if pesan.size == 0 :
            raise IndexError ()

        return pesan.data[pesan.head]

    def get(pesan, i) :
        if i <0 or i>= pesan.size :
            raise IndexError()

        return pesan.data[(pesan.head + i) % pesan.cap]


class Stack :
    def __init__(pesan) :
        pesan.isi = array()

    def kosong (pesan) :
        return pesan.isi.size == 0

    def ukuran(pesan) :
        return pesan.isi.size 

    def push (pesan, n) :
        pesan.isi.append(n)

    def pop (pesan ):
        if pesan.isi.size == 0 :
            raise IndexError ()

        return pesan.isi.remove (pesan.isi.size -1)

    def intip (pesan) :
        if pesan.isi.size == 0 :
            raise IndexError ()

        return pesan.isi.get(pesan.isi.size -1)

def isi_antrean(arr, antrean) :
    jumlah = 0 
    for i in range (arr.size) :
        p = arr.get(i)

        if p[STATUS] == "ANTRE" :
            antrean.enqueue(p)

            jumlah +=1
    return jumlah

def lanjut (queue, stack) :
    if queue.kosong ():
        return None

    p = queue.dequeue()
    stack.push(("Lanjut",p))

    return p

def catat(stack, struktur, pesanan) :
    i = tambah(struktur, pesanan)
    stack.push(("catat", struktur, i))

    return i

def hapus(stack, struktur, i) :
    p = struktur.remove(i)
    stack.push(("Hapus", struktur, i, p))

    return p


def undo(stack, queue, redo_stack=None):
    if stack.kosong():
        return None

    aksi = stack.pop()
    jenis = aksi[0]

    if jenis == "Lanjut":
        p = aksi[1]
        queue.enqueue_depan(p)

    elif jenis == "catat":
        struktur = aksi[1]
        i = aksi[2]
        p = struktur.remove(i)
        aksi = ("catat", struktur, i, p)

    elif jenis == "Hapus":
        struktur = aksi[1]
        i = aksi[2]
        p = aksi[3]
        struktur.insert(i, p)

    else:
        stack.push(aksi)
        return None

    if redo_stack is not None:
        redo_stack.push(aksi)

    return f"Undo berhasil: {jenis}"


def redo(stack, queue, redo_stack):
    if redo_stack.kosong():
        return None

    aksi = redo_stack.pop()
    jenis = aksi[0]

    if jenis == "Lanjut":
        p = queue.dequeue()
        stack.push(("Lanjut", p))

    elif jenis == "catat":
        struktur = aksi[1]
        i = aksi[2]
        p = aksi[3]
        struktur.insert(i, p)
        stack.push(("catat", struktur, i))

    elif jenis == "Hapus":
        struktur = aksi[1]
        i = aksi[2]
        p = struktur.remove(i)
        stack.push(("Hapus", struktur, i, p))

    else:
        redo_stack.push(aksi)
        return None

    return f"Redo berhasil: {jenis}"



PRIORITAS = {
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2
}


def ke_postfix(infix):
    pola = r"\d+(?:\.\d+)?|[()+\-*/]"
    token = []
    posisi = 0

    for cocok in re.finditer(pola, infix):
        if infix[posisi:cocok.start()].strip():
            raise ValueError("Ada karakter yang tidak valid.")

        token.append(cocok.group())
        posisi = cocok.end()

    if infix[posisi:].strip() or not token:
        raise ValueError("Ekspresi kosong atau tidak valid.")

    hasil = []
    stack = Stack()

    for t in token:
        if re.fullmatch(r"\d+(?:\.\d+)?", t):
            hasil.append(t)

        elif t == "(":
            stack.push(t)

        elif t == ")":
            while not stack.kosong() and stack.intip() != "(":
                hasil.append(stack.pop())

            if stack.kosong():
                raise ValueError("Kurung buka tidak ditemukan.")

            stack.pop()

        else:
            while (
                not stack.kosong()
                and stack.intip() != "("
                and PRIORITAS[stack.intip()] >= PRIORITAS[t]
            ):
                hasil.append(stack.pop())

            stack.push(t)

    while not stack.kosong():
        operator = stack.pop()

        if operator == "(":
            raise ValueError("Kurung tutup tidak ditemukan.")

        hasil.append(operator)

    return " ".join(hasil)


def hitung_postfix(ekspresi_postfix):
    stack = Stack()

    for t in ekspresi_postfix.split():
        if t not in PRIORITAS:
            stack.push(float(t))
        else:
            if stack.ukuran() < 2:
                raise ValueError("Ekspresi tidak valid.")

            b = stack.pop()
            a = stack.pop()

            if t == "+":
                hasil = a + b
            elif t == "-":
                hasil = a - b
            elif t == "*":
                hasil = a * b
            else:
                if b == 0:
                    raise ZeroDivisionError(
                        "Tidak bisa membagi dengan nol."
                    )
                hasil = a / b

            stack.push(hasil)

    if stack.ukuran() != 1:
        raise ValueError("Ekspresi tidak valid.")

    return stack.pop()


def hitung(infix):
    hasil_postfix = ke_postfix(infix)
    total = hitung_postfix(hasil_postfix)

    if isinstance(total, float) and total.is_integer():
        total = int(total)

    return hasil_postfix, total

                         