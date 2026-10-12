"""Alih huruf Kiril ke Latin, MENGIKUTI TULISAN, bukan lafal.

Ada dua alat bantu berbeda di proyek ini, dan keduanya sengaja dipisah:

* `translit()` di modul ini mengalihhurufkan apa yang TERTULIS. молоко́
  menjadi "molokó", padahal dilafalkan "ma-la-KO". Gunanya untuk mengenali
  huruf satu per satu pada pekan-pekan pertama.
* `cyrillic.pronounce()` memperkirakan LAFALNYA, lengkap dengan reduksi vokal.
  молоко́ menjadi "ma-la-KO".

Sistemnya mendekati BGN/PCGN yang biasa dipakai pada buku pelajaran: ж = zh,
х = kh, ц = ts, ч = ch, ш = sh, щ = shch, ю = yu, я = ya. Tanda tekanan
dipindahkan ke vokal Latinnya (rabóta), ь ditulis sebagai apostrof, dan ъ
sebagai tanda petik ganda.

Tujuan tunggalnya: jembatan sementara. Begitu 33 huruf sudah dikenal, matikan
alih huruf — penyangga Latin membuat mata berhenti membaca tulisan Kiril.
"""

from __future__ import annotations

import unicodedata

from .cyrillic import IOTATED, STRESS, VOWELS, nfc

#: Huruf tunggal. Huruf beriota (е ё ю я) ditangani terpisah karena bentuknya
#: bergantung pada huruf sebelumnya.
SIMPLE = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ж": "zh", "з": "z",
    "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh",
    "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch", "ы": "y", "э": "e",
    "ь": "'", "ъ": '"',
}

#: Huruf beriota: bentuk sesudah konsonan, dan bentuk di awal kata atau
#: sesudah vokal, ь, dan ъ.
IOTA = {
    "е": ("e", "ye"),
    "ё": ("yo", "yo"),
    "ю": ("yu", "yu"),
    "я": ("ya", "ya"),
}


def _acute(latin: str) -> str:
    """Pasang tanda tekanan pada vokal Latin terakhir di potongan ini."""
    for i in range(len(latin) - 1, -1, -1):
        if latin[i] in "aeiouy":
            return nfc(latin[: i + 1] + STRESS + latin[i + 1:])
    return latin


def translit(text: str) -> str:
    """Alihhurufkan teks Kiril ke Latin menurut tulisannya."""
    src = nfc(text)
    out: list[str] = []
    for i, ch in enumerate(src):
        if ch == STRESS:
            continue
        low = ch.lower()
        upper = ch != low
        # ё selalu bertekanan dalam data proyek ini sehingga tidak pernah
        # diberi tanda tekanan; tandanya dipasang kembali di sisi Latin.
        stressed = low == "ё" or (i + 1 < len(src) and src[i + 1] == STRESS)

        if low in IOTA:
            prev = ""
            for back in range(i - 1, -1, -1):
                if src[back] != STRESS:
                    prev = src[back]
                    break
            after_vowel = prev == "" or prev in VOWELS or prev.lower() in ("ь", "ъ")
            piece = IOTA[low][1 if after_vowel else 0]
        elif low in SIMPLE:
            piece = SIMPLE[low]
        else:
            piece = ch

        if stressed:
            piece = _acute(piece)
        if upper and piece:
            piece = piece[0].upper() + piece[1:]
        out.append(piece)
    return unicodedata.normalize("NFC", "".join(out))


def translit_letter(upper: str, lower: str) -> str:
    """Alih huruf untuk satu huruf alfabet, dipakai modul alfabet.

    Huruf beriota dialihhurufkan dalam bentuk awal kata (ye, yo, yu, ya),
    karena bentuk itulah yang dipakai saat huruf disebut sendirian.
    """
    low = lower.lower()
    if low in IOTA:
        return IOTA[low][1]
    return SIMPLE.get(low, lower)


__all__ = ["IOTA", "SIMPLE", "translit", "translit_letter"]
