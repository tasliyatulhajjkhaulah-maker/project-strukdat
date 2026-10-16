
from .m1 import I_OID, I_HARGA, I_T_SELESAI
 
BATAS_INSERTION = 20000    
BELUM_SELESAI = 10 ** 12      
 
class Sorting:
 
    def __init__(pesan):
        pesan.banding = 0
        pesan.pindah = 0
 
    def reset(pesan):
        pesan.banding = 0
        pesan.pindah = 0
 
 
def _identitas(x):
    return x

def kunci_oid(p):
    return p[I_OID]         
 
def kunci_harga(p):
    return p[I_HARGA]
 
def kunci_selesai(p):
    t = p[I_T_SELESAI]
    return t if t >= 0 else BELUM_SELESAI
 
 
NAMA_KUNCI = ("oid", "harga", "selesai")
 
 
def pilih_kunci(nama):
    if nama == "oid":
        return kunci_oid
    if nama == "harga":
        return kunci_harga
    if nama == "selesai":
        return kunci_selesai
    raise ValueError("kunci tidak dikenal: " + nama)
 
 
def salin_awal(A, n):
    if n > len(A):
        n = len(A)
    hasil = []
    for i in range(n):
        hasil.append(A[i])
    return hasil
 
 # bandingkan kemudian digeser ke kanan
def insertion_sort(A, kunci=None, pencacah=None):
    def insertion_sort(A, kunci=None, pencacah=None):
      if len(A) > BATAS_INSERTION:
        raise ValueError(
            "Data terlalu besar untuk Insertion Sort"
        )

    # Lanjutkan kode Insertion Sort yang sudah ada
    if kunci is None:
        kunci = _identitas
    if pencacah is None:
        pencacah = Sorting()
    for i in range(1, len(A)):
        x = A[i]
        kx = kunci(x)
        j = i - 1
        while j >= 0:
            pencacah.banding += 1
            if kunci(A[j]) > kx:
                A[j + 1] = A[j]
                pencacah.pindah += 1
                j -= 1
            else:
                break
        if j + 1 != i:
            A[j + 1] = x
            pencacah.pindah += 1
    return A
 
 
# ambil nilai tengah
def merge_sort(A, kunci=None, pencacah=None):
    if kunci is None:
        kunci = _identitas
    if pencacah is None:
        pencacah = Sorting()
    n = len(A)
    hasil = salin_awal(A, n)
    buf = [None] * n
    _ms(hasil, buf, 0, n, kunci, pencacah)
    return hasil
 
# membagi data jadi low, middle, dsa high buat mengurutkan datanya
def _ms(a, buf, lo, hi, kunci, pc):
    if hi - lo <= 1:
        return
    mid = (lo + hi) // 2
    _ms(a, buf, lo, mid, kunci, pc)
    _ms(a, buf, mid, hi, kunci, pc)
    i = lo
    j = mid
    k = lo

    while i < mid and j < hi:
        pc.banding += 1
        if kunci(a[i]) <= kunci(a[j]):     
            buf[k] = a[i]
            i += 1
        else:
            buf[k] = a[j]
            j += 1
        k += 1
        pc.pindah += 1

    #bagian kiri
    while i < mid:                          
        buf[k] = a[i]
        i += 1
        k += 1
        pc.pindah += 1

    #bagian kanan
    while j < hi:                           
        buf[k] = a[j]
        j += 1
        k += 1
        pc.pindah += 1
    for t in range(lo, hi):
        a[t] = buf[t]
 

 # bandingkan dengan semua elemen dari awal
def linear_search(A, target, kunci=None, pencacah=None):
    if kunci is None:
        kunci = _identitas
    if pencacah is None:
        pencacah = Sorting()
    for i in range(len(A)):
        pencacah.banding += 1
        if kunci(A[i]) == target:
            return i
    return -1
 
 #ambil nilai tengah buat cari data yang udah terurut
def binary_search(A, target, kunci=None, pencacah=None):
    if kunci is None:
        kunci = _identitas
    if pencacah is None:
        pencacah = Sorting()
    lo = 0
    hi = len(A) - 1
    while lo <= hi:                         
        mid = (lo + hi) // 2
        km = kunci(A[mid])
        pencacah.banding += 1
        if km == target:
            return mid
        if km < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
 
