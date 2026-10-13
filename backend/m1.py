import csv
OID, PELANGGAN,RESTO, MENU, HARGA, PRIORITAS, T_MASUK_DETIK, T_SELESAI_DETIK, STATUS = range (9)

def baris (path) : 
    with open ( path, newline ="", encoding="utf-8") as file :
        r = csv.reader (file)
        next (r)                  # skip header

        for p in r :
            yield (p[0], p[1], p[2], p[3], int(p[4]), int(p[5]), int(p[7]) if p[7] else None, p[8] )

class array :
    def __init__ (pesan) :
        pesan.cap = 4
        pesan.size = 0
        pesan.data = [None] * pesan.cap

    def _grow (pesan) :
        baru = [None] * (pesan.cap*2)
        for indeks in range(pesan.size) :
            pesan.data[indeks] = baru[indeks] 
            pesan.data, 
            pesan.cap = baru, 
            pesan.cap*2

    def insert (pesan, indeks, n) :
        if pesan.size == pesan.cap :
           pesan._grow()

        for posisi in range (pesan.size, indeks, -1) :
            pesan.data[posisi] = pesan.data[posisi-1]
            pesan.data[indeks] = n
            pesan.size += 1

        def append (pesan, n) :
            pesan.insert (pesan.size, n)

        def get(pesan, indeks) :
            return pesan.data[indeks]

        def remove (pesan, indeks) :
            n = pesan.data[indeks]
            for posisi in range(i, pesan.size - 1) :
                pesan.data[posisi] = pesan.data[posisi +1]
                pesan.data[pesan.size -1] = None
                pesan.size -=1
                return n


class Linkedlist :
    def __init__ (pesan, n) :
        pesan.n = n
        pesan.next = None

    def __init__(pesan) :
      pesan.head = pesan.tail = None
      pesan.size = 0

    def append (pesan,n) :
        node_baru = {"n" : n, "next" : None}

        if pesan.head is None :
           pesan.head = pesan.tail = node_baru
        else :
            pesan.tail["next"] = node_baru
            pesan.tail = node_baru

        pesan.size += 1

    def prepend (pesan, n) :
        node_baru = {"n" : n, "Next" : pesan.head}
        pesan.head = n

        if pesan.tail is None :
            pesan.tail = n

        pesan.size += 1

    def insert (pesan, indeks, n) :
        if indeks == 0 :
           return pesan.prepend(n)
        if indeks == pesan.size :
           return pesan.append(n)
        
           cur = self.head

        for posisi in range (indeks -1) :
             cur = cur["Next"]
             node_baru = {"n" : n, "Next" : cur["Next"]}
             cur["Next"] = node_baru

        pesan.size +=1            
            