from m1 import array, RESTO, STATUS, HARGA, T_MASUK_DETIK, jam

BATAS_WAKTU = 10** 12

def bangun_laporan(arr, resto="", status="", t_awal=0, t_akhir=BATAS_WAKTU):
    """Saring arr -> array baru (urutan asli, belum terurut).
 
    resto  : "" berarti semua resto
    status : "" berarti semua status ("DONE", "CANCEL", "ANTRE")
    t_awal, t_akhir : rentang t_masuk_detik, inklusif
    """
    lap = array()
    for indeks in range(arr.size):
        p = arr.get(indeks)
        if resto != "" and p[RESTO] != resto:
            continue
        if status != "" and p[STATUS] != status:
            continue
        if p[T_MASUK_DETIK] < t_awal or p[T_MASUK_DETIK] > t_akhir:
            continue
        lap.append(p)
    return lap
 
 
# ---------------------------------------------------------------- sorting
# data = list mentah (array.data), n = jumlah elemen valid (array.size),
# kolom = nomor kolom tuple yang jadi kunci (mis. T_MASUK_DETIK, HARGA).
 
def insertion_sort(data, n, kolom):
    """Stabil: '>' (bukan '>=') menjaga urutan awal untuk kunci yang sama."""
    for i in range(1, n):
        x = data[i]
        kunci = x[kolom]
        j = i - 1
        while j >= 0 and data[j][kolom] > kunci:
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = x
 
 
def selection_sort(data, n, kolom):
    """Tidak stabil. Selalu O(n^2) perbandingan."""
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            if data[j][kolom] < data[m][kolom]:
                m = j
        if m != i:
            tmp = data[i]
            data[i] = data[m]
            data[m] = tmp
 
 
def bubble_sort(data, n, kolom):
    """Stabil. Berhenti lebih awal bila satu putaran tanpa pertukaran."""
    for i in range(n - 1):
        tukar = False
        for j in range(n - 1 - i):
            if data[j][kolom] > data[j + 1][kolom]:
                tmp = data[j]
                data[j] = data[j + 1]
                data[j + 1] = tmp
                tukar = True
        if not tukar:
            break
 
 
def urutkan(lap, kolom=T_MASUK_DETIK, metode="insertion"):
    """Urutkan laporan (array) di tempat, return lap."""
    if metode == "selection":
        selection_sort(lap.data, lap.size, kolom)
    elif metode == "bubble":
        bubble_sort(lap.data, lap.size, kolom)
    else:
        insertion_sort(lap.data, lap.size, kolom)
    return lap
 
 
# ---------------------------------------------------------------- binary search
def cari_pertama(data, n, target, kolom):
    """Lower bound: indeks kemunculan PERTAMA target, atau -1 bila tidak ada.
 
    data harus sudah terurut menaik menurut kolom.
    """
    lo = 0
    hi = n
    while lo < hi:
        mid = (lo + hi) // 2
        if data[mid][kolom] < target:
            lo = mid + 1
        else:
            hi = mid
    if lo < n and data[lo][kolom] == target:
        return lo
    return -1
 
 
def cari_semua(lap, target, kolom=T_MASUK_DETIK):
    """Semua pesanan di laporan terurut dengan kunci == target (array baru)."""
    hasil = array()
    indeks = cari_pertama(lap.data, lap.size, target, kolom)
    if indeks == -1:
        return hasil
    while indeks < lap.size and lap.data[indeks][kolom] == target:
        hasil.append(lap.data[indeks])
        indeks += 1
    return hasil
 
 
# ---------------------------------------------------------------- ringkasan
def ringkasan(lap):
    """(jumlah, total_harga, t_pertama, t_terakhir). Waktu None bila kosong."""
    if lap.size == 0:
        return (0, 0, None, None)
    total = 0
    awal = lap.data[0][T_MASUK_DETIK]
    akhir = awal
    for indeks in range(lap.size):
        p = lap.data[indeks]
        total += p[HARGA]
        if p[T_MASUK_DETIK] < awal:
            awal = p[T_MASUK_DETIK]
        if p[T_MASUK_DETIK] > akhir:
            akhir = p[T_MASUK_DETIK]
    return (lap.size, total, awal, akhir)
 
 
def teks_ringkasan(lap):
    jumlah, total, awal, akhir = ringkasan(lap)
    if jumlah == 0:
        return "laporan kosong"
    return ("jumlah " + str(jumlah) + " pesanan | total Rp" + str(total)
            + " | " + jam(awal) + " - " + jam(akhir))


