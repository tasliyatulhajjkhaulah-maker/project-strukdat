
from .m1 import array, RESTO, STATUS, HARGA, T_MASUK_DETIK, jam

BATAS_WAKTU = 24 * 3600


def laporan(arr, resto="", status="", t_awal=0, t_akhir=BATAS_WAKTU):
    lap = array()

    for i in range(arr.size):
        p = arr.get(i)

        if (
            (resto != "" and p[RESTO] != resto)
            or (status != "" and p[STATUS] != status)
            or not t_awal <= p[T_MASUK_DETIK] <= t_akhir
        ):
            continue

        lap.append(p)

    return lap


def insertion_sort(data, n, kolom):
    for i in range(1, n):
        x = data[i]
        kunci = x[kolom]
        j = i - 1

        while j >= 0 and data[j][kolom] > kunci:
            data[j + 1] = data[j]
            j -= 1

        data[j + 1] = x


def merge_sort(data, n, kolom):
    if n <= 1:
        return

    sementara = [None] * n

    def bagi(kiri, kanan):
        if kanan - kiri <= 1:
            return

        tengah = (kiri + kanan) // 2

        bagi(kiri, tengah)
        bagi(tengah, kanan)

        i = kiri
        j = tengah
        k = kiri

        while i < tengah and j < kanan:
            if data[i][kolom] <= data[j][kolom]:
                sementara[k] = data[i]
                i += 1
            else:
                sementara[k] = data[j]
                j += 1
            k += 1

        while i < tengah:
            sementara[k] = data[i]
            i += 1
            k += 1

        while j < kanan:
            sementara[k] = data[j]
            j += 1
            k += 1

        for indeks in range(kiri, kanan):
            data[indeks] = sementara[indeks]

    bagi(0, n)


def urutkan(lap, kolom=T_MASUK_DETIK, metode="insertion"):
    if metode == "insertion":
        insertion_sort(lap.data, lap.size, kolom)

    elif metode == "merge":
        merge_sort(lap.data, lap.size, kolom)

    else:
        raise ValueError(
            "Metode sorting harus insertion atau merge."
        )
    return lap


def linear_search(lap, target, kolom=T_MASUK_DETIK):
    """Mencari semua data yang nilainya sama dengan target."""

    hasil = array()

    for i in range(lap.size):
        p = lap.get(i)

        if p[kolom] == target:
            hasil.append(p)

    return hasil

def cari_pertama(data, n, target, kolom):
    kiri = 0
    kanan = n

    while kiri < kanan:
        tengah = (kiri + kanan) // 2

        if data[tengah][kolom] < target:
            kiri = tengah + 1
        else:
            kanan = tengah

    if kiri < n and data[kiri][kolom] == target:
        return kiri

    return -1


def cari_semua(lap, target, kolom=T_MASUK_DETIK):
    hasil = array()

    indeks = cari_pertama(
        lap.data, lap.size, target, kolom
    )

    if indeks == -1:
        return hasil

    while (
        indeks < lap.size
        and lap.data[indeks][kolom] == target
    ):
        hasil.append(lap.data[indeks])
        indeks += 1

    return hasil


def ringkasan(lap):
    if lap.size == 0:
        return 0, 0, None, None

    total = 0
    awal = lap.get(0)[T_MASUK_DETIK]
    akhir = awal

    for i in range(lap.size):
        p = lap.get(i)
        total += p[HARGA]

        if p[T_MASUK_DETIK] < awal:
            awal = p[T_MASUK_DETIK]

        if p[T_MASUK_DETIK] > akhir:
            akhir = p[T_MASUK_DETIK]

    return lap.size, total, awal, akhir


def teks_ringkasan(lap):
    jumlah, total, awal, akhir = ringkasan(lap)

    if jumlah == 0:
        return "Laporan kosong"

    return (
        "Jumlah " + str(jumlah)
        + " pesanan | Total Rp" + str(total)
        + " | " + jam(awal) + " - " + jam(akhir)
    )
