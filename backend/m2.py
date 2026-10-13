from m1 import array, STATUS, OID, tambah

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

def undo (stack, queue) :
    if stack.kosong() :
        return None

    aksi = stack.pop()
    jenis = aksi[0]



    if jenis == "Lanjut" :
        p = aksi[1]
        queue.enqueue_depan (p)

        return f"undo Lanjut : {p[OID] } BALIK ANTRI KE DEPAN"

    if jenis == "catat" :
        struktur = aksi[1]
        i = aksi [2]
        p = struktur.remove(i)

        return f"undo catat : { p[OID]} dicabut dari indeks {i}"
    

    if jenis == "Hapus" :
        struktur = aksi[1]
        i = aksi[2]
        p = aksi[3]
        struktur.insert (i, p)

        return f"undo Hapus {p[OID]} balik ke indeks {i}"

    return None





if __name__ == "__main__":
    # 1. Tes Queue
    antrean = Queue()

    antrean.enqueue("A")
    antrean.enqueue("B")
    antrean.enqueue("C")

    assert antrean.size == 3
    assert antrean.intip() == "A"
    assert antrean.dequeue() == "A"
    assert antrean.dequeue() == "B"
    assert antrean.size == 1

    print("[OK] Queue berhasil")

    # 2. Tes Queue saat kapasitas penuh
    antrean = Queue(cap=2)
    antrean.enqueue("A")
    antrean.enqueue("B")
    antrean.enqueue("C")

    assert antrean.cap == 4
    assert antrean.size == 3
    assert antrean.get(0) == "A"
    assert antrean.get(1) == "B"
    assert antrean.get(2) == "C"

    print("[OK] Queue resize berhasil")

    # 3. Tes Stack
    stack = Stack()
    stack.push("A")
    stack.push("B")

    assert stack.ukuran() == 2
    assert stack.intip() == "B"
    assert stack.pop() == "B"
    assert stack.pop() == "A"
    assert stack.kosong()

    print("[OK] Stack berhasil")

    # 4. Tes lanjut dan undo
    antrean = Queue()
    stack = Stack()

    pesanan = ("O-001",)
    antrean.enqueue(pesanan)

    hasil = lanjut(antrean, stack)

    assert hasil == pesanan
    assert antrean.kosong()
    assert not stack.kosong()

    hasil_undo = undo(stack, antrean)

    assert hasil_undo is not None
    assert antrean.size == 1
    assert antrean.intip() == pesanan
    assert stack.kosong()

    print("[OK] Lanjut dan undo berhasil")

    print("\nSEMUA PENGUJIAN BERHASIL!")
