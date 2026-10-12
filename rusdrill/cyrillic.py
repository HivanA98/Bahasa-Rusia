"""Utilitas teks Kiril: normalisasi, tanda tekanan, silabel, dan pelafalan.

Modul ini tidak memakai pustaka luar supaya hasilnya deterministik dan bisa
diuji. Semua aturan di sini bersifat ORTOGRAFIS dan FONOLOGIS MEKANIS (cara
penulisan dan kaidah pelafalan yang bisa dihitung), bukan penilaian isi
bahasa. Kebenaran arti, gender, bentuk jamak, dan letak tekanan sebuah kata
TIDAK bisa diperiksa mesin -- lihat data/NEEDS_REVIEW.md dan README.md.

Tanda tekanan ditulis sebagai U+0301 (combining acute) tepat sesudah huruf
vokal: рабо́та. Huruf ё selalu bertekanan dalam kata-kata di proyek ini,
sehingga kata yang memuat ё tidak diberi tanda tekanan.

Validator dipakai pada field data (lema, contoh kalimat, pilihan jawaban),
BUKAN pada field prosa (explanation, caveats, note, explain). Field prosa
sengaja memuat potongan akhiran (-ый, -ая) dan contoh bentuk yang salah untuk
diperbandingkan; keduanya akan ditolak validator ini.
"""

from __future__ import annotations

import re
import unicodedata

# ---------------------------------------------------------------- karakter ---

#: Tanda tekanan: combining acute accent. Ditulis sesudah huruf vokalnya.
STRESS = "́"
YO = "ё"

VOWELS_LOWER = "аеёиоуыэюя"
CONSONANTS_LOWER = "бвгджзйклмнпрстфхцчшщ"
SIGNS_LOWER = "ьъ"

VOWELS = set(VOWELS_LOWER) | set(VOWELS_LOWER.upper())
CONSONANTS = set(CONSONANTS_LOWER) | set(CONSONANTS_LOWER.upper())
SIGNS = set(SIGNS_LOWER) | set(SIGNS_LOWER.upper())
LETTERS = VOWELS | CONSONANTS | SIGNS

#: Huruf vokal "beriota": menyiratkan bunyi /j/ atau melunakkan konsonan
#: sebelumnya.
IOTATED = set("еёюя")

#: Konsonan yang selalu keras; sesudahnya е dan и dilafalkan seperti э dan ы.
ALWAYS_HARD = set("жшц")
#: Konsonan yang selalu lunak.
ALWAYS_SOFT = set("чщй")

#: Pasangan bersuara <-> tak bersuara, untuk kaidah pelemahan di akhir kata
#: dan asimilasi di dalam gugus konsonan.
VOICED_TO_VOICELESS = {"б": "п", "в": "ф", "г": "к", "д": "т", "ж": "ш", "з": "с"}
VOICELESS_TO_VOICED = {"п": "б", "ф": "в", "к": "г", "т": "д", "ш": "ж", "с": "з"}
#: в tidak memicu penyuaraan ke belakang, karena itu tidak masuk daftar ini.
VOICED_OBSTRUENTS = set("бгджз")
VOICELESS = set("пфктшсхцчщ")

#: Tanda baca yang diizinkan di dalam contoh kalimat.
PUNCT = set(" ,.!?;:-—–()«»…")

_LETTER_CLASS = (
    VOWELS_LOWER + VOWELS_LOWER.upper()
    + CONSONANTS_LOWER + CONSONANTS_LOWER.upper()
    + SIGNS_LOWER + SIGNS_LOWER.upper() + STRESS
)
_WORD_SPLIT_RE = re.compile("[^" + _LETTER_CLASS + "]+")


# -------------------------------------------------------------- normalisasi ---

def nfc(text: str) -> str:
    """Normalisasi Unicode ke bentuk NFC."""
    return unicodedata.normalize("NFC", text)


def is_nfc(text: str) -> bool:
    return unicodedata.is_normalized("NFC", text)


def strip_stress(text: str) -> str:
    """Buang semua tanda tekanan. Huruf ё TIDAK diubah menjadi е.

    Dalam tulisan Rusia sehari-hari tanda tekanan tidak ditulis, tetapi ё
    umumnya tetap ditulis di buku pelajaran. Modul membaca memakai fungsi ini
    untuk Level 3.
    """
    return nfc(text).replace(STRESS, "")


def strip_stress_and_yo(text: str) -> str:
    """Buang tanda tekanan DAN ganti ё menjadi е, seperti teks cetak biasa.

    Surat kabar dan buku Rusia untuk pembaca dewasa umumnya menulis е di
    tempat ё (елка untuk ёлка).
    """
    out = strip_stress(text)
    return out.replace("ё", "е").replace("Ё", "Е")


def has_stress(text: str) -> bool:
    return STRESS in nfc(text)


def has_cyrillic(text: str) -> bool:
    """True bila teks memuat setidaknya satu huruf Kiril.

    Dipakai antarmuka untuk memutuskan apakah baris alih huruf dan baris
    pendekatan lafal perlu ditampilkan. Teks jawaban yang seluruhnya Bahasa
    Indonesia tidak perlu dialihhurufkan.
    """
    return any(ch in LETTERS for ch in nfc(text))


def split_words(text: str) -> list[str]:
    """Pecah teks menjadi kata. Tanda baca dan tanda hubung menjadi pemisah.

    Tanda hubung menjadi pemisah karena bagian sebuah kata berhubung bisa
    tidak bertekanan (что-нибу́дь: что tanpa tekanan).
    """
    return [w for w in _WORD_SPLIT_RE.split(nfc(text)) if w]


# ------------------------------------------------------------ vokal & suku ---

def vowel_indices(word: str) -> list[int]:
    return [i for i, ch in enumerate(nfc(word)) if ch in VOWELS]


def count_vowels(word: str) -> int:
    """Jumlah vokal = jumlah suku kata (berlaku untuk bahasa Rusia)."""
    return len(vowel_indices(word))


def stress_position(word: str) -> int | None:
    """Nomor vokal yang bertekanan (mulai 0), atau None bila tidak diketahui.

    Tanda tekanan eksplisit menang. Bila tidak ada tanda, huruf ё dianggap
    bertekanan. Kata bervokal tunggal bertekanan pada vokal itu.
    """
    w = nfc(word)
    nth = -1
    for i, ch in enumerate(w):
        if ch in VOWELS:
            nth += 1
            if i + 1 < len(w) and w[i + 1] == STRESS:
                return nth
    lower = w.lower()
    if YO in lower:
        nth = -1
        for ch in lower:
            if ch in VOWELS:
                nth += 1
                if ch == YO:
                    return nth
    if count_vowels(w) == 1:
        return 0
    return None


def syllables(word: str) -> list[str]:
    """Pecah satu kata menjadi suku kata (pendekatan).

    Aturan yang dipakai: setiap suku kata berakhir pada vokalnya, sehingga
    seluruh gugus konsonan antar-vokal ikut ke suku kata berikutnya; й, ь, dan
    ъ menutup suku kata di depannya; konsonan di akhir kata ikut suku terakhir.

    Pembagian suku kata bahasa Rusia yang sebenarnya masih diperdebatkan para
    ahli fonetik, khususnya pada gugus konsonan. Fungsi ini alat bantu baca,
    bukan analisis fonologis.
    """
    w = nfc(word)
    if not w:
        return []
    out: list[str] = []
    cur: list[str] = []
    seen_vowel = False
    for ch in w:
        if ch in VOWELS:
            if seen_vowel:
                head: list[str] = []
                while cur and cur[-1] not in VOWELS and cur[-1] != STRESS \
                        and cur[-1].lower() not in ("й", "ь", "ъ"):
                    head.insert(0, cur.pop())
                if cur:
                    out.append("".join(cur))
                cur = head
            cur.append(ch)
            seen_vowel = True
        else:
            cur.append(ch)
    if cur:
        if out and not any(c in VOWELS for c in cur):
            out[-1] += "".join(cur)
        else:
            out.append("".join(cur))
    return out


# --------------------------------------------------------------- validasi ---

def check_chars(text: str, *, allow_punct: bool = True) -> list[str]:
    """Periksa karakter: hanya Kiril, tanda tekanan, dan tanda baca."""
    problems: list[str] = []
    if not is_nfc(text):
        problems.append("teks tidak dalam bentuk NFC")
    w = nfc(text)
    for i, ch in enumerate(w):
        if ch in LETTERS or ch == STRESS:
            continue
        if ch in PUNCT and allow_punct:
            continue
        name = unicodedata.name(ch, "U+%04X" % ord(ch))
        problems.append(
            "karakter tidak diizinkan pada posisi %d: %r (%s)" % (i, ch, name)
        )
    for i, ch in enumerate(w):
        if ch == STRESS and (i == 0 or w[i - 1] not in VOWELS):
            problems.append(
                "tanda tekanan pada posisi %d tidak mengikuti huruf vokal" % i
            )
    return problems


def check_stress_word(word: str) -> list[str]:
    """Aturan penulisan tekanan untuk SATU kata.

    1. Kata bervokal lebih dari satu wajib memuat tepat satu tanda tekanan.
    2. Kata bervokal tunggal tidak diberi tanda tekanan (tanda itu mubazir).
    3. Kata yang memuat ё tidak diberi tanda tekanan, karena ё sudah
       bertekanan dengan sendirinya.

    Aturan 3 memiliki pengecualian di luar proyek ini: pada beberapa kata
    majemuk dan serapan, ё tidak bertekanan (трёхэта́жный). Tidak ada kata
    semacam itu di data, dan validator akan menolaknya bila ditambahkan.
    """
    w = nfc(word)
    problems: list[str] = []
    marks = w.count(STRESS)
    n_vowels = count_vowels(w)
    bare = strip_stress(w).lower()
    if n_vowels == 0:
        if marks:
            problems.append(bare + ": ada tanda tekanan tetapi tidak ada vokal")
        return problems
    if YO in bare:
        if marks:
            problems.append(
                bare + ": memuat ё sehingga tidak perlu tanda tekanan "
                "(ё selalu bertekanan)"
            )
        return problems
    if n_vowels == 1:
        if marks:
            problems.append(bare + ": kata bersuku satu tidak diberi tanda tekanan")
        return problems
    if marks == 0:
        problems.append(bare + ": kata bersuku banyak tanpa tanda tekanan")
    elif marks > 1:
        problems.append(bare + ": ada %d tanda tekanan, seharusnya satu" % marks)
    return problems


def check_stress(text: str) -> list[str]:
    """Terapkan check_stress_word pada setiap kata di dalam teks."""
    problems: list[str] = []
    for word in split_words(text):
        problems += check_stress_word(word)
    return problems


def validate(text: str, *, allow_punct: bool = True) -> list[str]:
    """Gabungan check_chars dan check_stress."""
    return check_chars(text, allow_punct=allow_punct) + check_stress(text)


# -------------------------------------------------------------- pelafalan ---

#: Kata yang lafalnya tidak bisa diturunkan dengan kaidah umum. Nilainya
#: adalah ejaan fonetis dalam huruf Kiril, lengkap dengan tanda tekanan, yang
#: kemudian diproses oleh kaidah biasa.
LEXICAL = {
    "что": "што",
    "чтобы": "што́бы",
    "конечно": "коне́шно",
    "сегодня": "сиво́дня",
    "здравствуйте": "здра́ствуйте",
    "его": "йево́",
    "ничего": "ничево́",
    "скучно": "ску́шно",
    "солнце": "со́нце",
    "сейчас": "сича́с",
}

#: Gugus huruf yang dilafalkan menyimpang dari huruf per huruf. Diterapkan
#: berurutan pada ejaan yang tanda tekanannya dilepas sementara.
CLUSTERS = [
    ("гк", "хк"),        # лёгкий, мя́гкий
    ("стн", "сн"),      # че́стный
    ("здн", "зн"),      # по́здно
    ("стл", "сл"),      # счастли́вый
    ("сч", "щ"),        # счёт
    ("зч", "щ"),        # расска́зчик
    ("тьс", "ц"),       # учи́ться
    ("тс", "ц"),        # нра́вится
    ("дс", "ц"),        # городско́й
    ("зж", "ж"),
    ("жж", "ж"),
    ("сш", "ш"),
    ("зш", "ш"),
]

_LAT_CONS = {
    "б": "b", "в": "v", "г": "g", "д": "d", "ж": "zh", "з": "z", "й": "y",
    "к": "k", "л": "l", "м": "m", "н": "n", "п": "p", "р": "r", "с": "s",
    "т": "t", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
}

_LAT_VOWEL = {
    "а": "a", "о": "o", "у": "u", "ы": "y", "э": "e", "и": "i",
    "е": "ye", "ё": "yo", "ю": "yu", "я": "ya",
}


def _preprocess(word: str) -> str:
    """Terapkan kekecualian leksikal, akhiran -ого, dan gugus konsonan."""
    bare = strip_stress(word).lower()
    if bare in LEXICAL:
        word = LEXICAL[bare]
    w = nfc(word).lower()
    plain = strip_stress(w)
    if len(plain) > 3 and (plain.endswith("ого") or plain.endswith("его")):
        idx = w.rfind("г")
        if idx != -1:
            w = w[:idx] + "в" + w[idx + 1:]
    nth = stress_position(w)
    plain = strip_stress(w)
    for src, dst in CLUSTERS:
        plain = plain.replace(src, dst)
    if nth is None:
        return plain
    out: list[str] = []
    seen = -1
    for ch in plain:
        out.append(ch)
        if ch in VOWELS:
            seen += 1
            if seen == nth:
                out.append(STRESS)
    return "".join(out)


def _vowel(ch: str, prev: str, stressed: bool, *, pre_stress: bool) -> str:
    """Satu vokal menjadi huruf Latin, dengan reduksi bila tanpa tekanan."""
    base = _LAT_VOWEL[ch]
    hard = prev in ALWAYS_HARD
    soft = prev in ("ч", "щ")
    if stressed:
        if hard and ch == "е":
            return "e"
        if hard and ch == "и":
            return "y"
        if (hard or soft) and ch in IOTATED:
            return base[1:]
        return base
    if ch == "а":
        return "i" if soft else "a"
    if ch == "о":
        return "a"
    if ch == "ы":
        return "y"
    if ch == "у":
        return "u"
    if ch == "э":
        return "e"
    if ch == "и":
        return "y" if hard else "i"
    if ch == "е":
        return "y" if hard else "i"
    if ch == "ё":
        return "yo"
    if ch == "ю":
        return "u" if (hard or soft) else "yu"
    if ch == "я":
        if hard or soft:
            return "i" if pre_stress else "a"
        return "yi" if pre_stress else "ya"
    return base


def _consonant(ch: str, chars: list[str], i: int) -> str:
    """Lafalkan satu konsonan dengan kaidah pelemahan dan asimilasi."""
    j = i + 1
    while j < len(chars) and chars[j] in SIGNS:
        j += 1
    nxt = chars[j] if j < len(chars) else ""
    out = ch
    if nxt == "":
        out = VOICED_TO_VOICELESS.get(ch, ch)
    elif nxt in VOICELESS and ch in VOICED_TO_VOICELESS:
        out = VOICED_TO_VOICELESS[ch]
    elif nxt in VOICED_OBSTRUENTS and ch in VOICELESS_TO_VOICED:
        out = VOICELESS_TO_VOICED[ch]
    return _LAT_CONS.get(out, out)


def _pieces(word: str) -> list[tuple[str, bool, bool]]:
    """Ubah satu kata menjadi potongan Latin.

    Setiap potongan adalah (teks, vokal?, penutup suku kata?). Penutup suku
    kata adalah й dan ь: keduanya ikut suku kata di DEPANnya, bukan suku kata
    sesudahnya (боль-ша́-я, bukan бо-льша́-я).
    """
    w = _preprocess(word)
    chars = [c for c in nfc(w) if c != STRESS]
    marks = [False] * len(chars)
    j = -1
    for ch in nfc(w):
        if ch != STRESS:
            j += 1
        elif j >= 0:
            marks[j] = True

    nth = stress_position(w)
    out: list[tuple[str, bool, bool]] = []
    vowel_seen = -1
    for i, ch in enumerate(chars):
        nxt = chars[i + 1] if i + 1 < len(chars) else ""
        prev = chars[i - 1] if i else ""
        if ch in VOWELS:
            vowel_seen += 1
            stressed = marks[i] or ch == YO or (nth is not None and vowel_seen == nth)
            out.append((
                _vowel(ch, prev, stressed,
                       pre_stress=(nth is not None and vowel_seen < nth)),
                True, False,
            ))
        elif ch in SIGNS:
            # ь dilafalkan sebagai pelunakan dan ditulis sebagai apostrof.
            # Di depan vokal beriota, pelunakannya sudah terbawa huruf y pada
            # vokal itu, jadi apostrofnya tidak ditulis. ъ hanya pemisah.
            if ch == "ь" and nxt not in IOTATED:
                out.append(("'", False, True))
        elif ch in CONSONANTS:
            out.append((_consonant(ch, chars, i), False, ch == "й"))
        else:
            out.append((ch, False, False))
    return [(t, v, c) for t, v, c in out if t != ""]


def pronounce(word: str) -> str:
    """Pendekatan lafal satu kata, ditulis dengan huruf Latin per suku kata.

    Suku kata dipisah tanda hubung dan suku kata bertekanan ditulis dengan
    HURUF BESAR: молоко́ menjadi "ma-la-KO".

    Ini PENDEKATAN untuk penutur Bahasa Indonesia, bukan transkripsi fonetik
    ilmiah. Kaidah yang diterapkan: reduksi vokal tanpa tekanan (о menjadi a,
    е dan я menjadi i), pelemahan konsonan bersuara di akhir kata, asimilasi
    di dalam gugus konsonan, akhiran -ого/-его dengan в, serta sejumlah
    kekecualian leksikal (lihat LEXICAL). Yang TIDAK ditangani: kelunakan
    konsonan secara halus, panjang vokal, dan intonasi.
    """
    w = nfc(word)
    if not w or not any(c in LETTERS for c in w):
        return ""
    pieces = _pieces(w)
    if not pieces:
        return ""
    groups: list[list[str]] = []
    pending: list[str] = []
    for text, is_vowel, closes in pieces:
        if closes and groups:
            # й dan ь menutup suku kata di depannya. Bila ь melunakkan sebuah
            # konsonan yang masih tertahan (боль-ша́-я), konsonan itu ikut
            # pindah ke suku kata sebelumnya bersama tanda lunaknya.
            groups[-1].extend(pending)
            pending = []
            groups[-1].append(text)
            continue
        pending.append(text)
        if is_vowel:
            groups.append(pending)
            pending = []
    if pending:
        if groups:
            groups[-1] += pending
        else:
            groups.append(pending)

    nth = stress_position(_preprocess(w))
    out: list[str] = []
    for k, g in enumerate(groups):
        s = "".join(g)
        out.append(s.upper() if (nth is not None and k == nth and len(groups) > 1) else s)
    return "-".join(out)


def pronounce_text(text: str) -> str:
    """Pendekatan lafal untuk satu kalimat; tanda baca dipertahankan."""
    out: list[str] = []
    buf: list[str] = []
    for ch in nfc(text):
        if ch in LETTERS or ch == STRESS:
            buf.append(ch)
        else:
            if buf:
                out.append(pronounce("".join(buf)))
                buf = []
            out.append(ch)
    if buf:
        out.append(pronounce("".join(buf)))
    return "".join(out)


__all__ = [
    "ALWAYS_HARD",
    "ALWAYS_SOFT",
    "CONSONANTS",
    "IOTATED",
    "LETTERS",
    "PUNCT",
    "SIGNS",
    "STRESS",
    "VOWELS",
    "YO",
    "check_chars",
    "check_stress",
    "check_stress_word",
    "count_vowels",
    "has_cyrillic",
    "has_stress",
    "is_nfc",
    "nfc",
    "pronounce",
    "pronounce_text",
    "split_words",
    "strip_stress",
    "strip_stress_and_yo",
    "stress_position",
    "syllables",
    "validate",
    "vowel_indices",
]
