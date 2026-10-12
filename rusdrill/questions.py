"""Pembuat soal untuk setiap mode latihan.

Soal yang dibuat otomatis (kartu huruf, kartu kosakata dua arah, dan soal akar
kata) selalu mengambil kunci jawaban LANGSUNG dari data, bukan dari daftar
terpisah, sehingga kuncinya tidak bisa menyimpang dari sumbernya. Pengecoh
dipilih dengan generator acak ber-seed agar hasilnya bisa diulang dan diuji.
"""

from __future__ import annotations

import random
import re
import unicodedata
from dataclasses import dataclass, field

from . import dataio
from .cyrillic import (
    PUNCT,
    strip_stress,
    strip_stress_and_yo,
)
from .translit import translit_letter

MODES = ("alfabet", "kosakata-ru", "kosakata-id", "tatabahasa", "akar", "baca")

MODE_LABELS = {
    "alfabet": "Alfabet Kiril",
    "kosakata-ru": "Kosakata: Rusia ke Indonesia",
    "kosakata-id": "Kosakata: Indonesia ke Rusia",
    "tatabahasa": "Tata bahasa",
    "akar": "Akar kata dan afiks",
    "baca": "Tekanan dan pelafalan",
}

_ACCEPTED_CACHE: dict[tuple, frozenset[str]] = {}


@dataclass
class Question:
    card_id: str
    mode: str
    kind: str  # "mcq" | "typed" | "selfcheck"
    question: str
    stimulus_ru: str | None = None
    stimulus_label: str | None = None
    options: list[str] | None = None
    options_lang: str | None = None
    answer: int | None = None
    accepted: list[str] = field(default_factory=list)
    reveal: str = ""
    reveal_ru: str | None = None
    explain: str | None = None
    #: True bila soal ini pengulangan materi baru di lintasan kedua sesi yang
    #: sama. quiz.py tidak menaikkan kotak Leitner dua kali.
    repeat: bool = False
    #: Tahap materi (1-6). Dipakai session.py untuk memperkenalkan kartu baru
    #: menurut urutan tahap, bukan secara acak dari seluruh materi.
    stage: int | None = None

    def is_correct_text(self, text: str) -> bool:
        return normalize(text) in {normalize(a) for a in self.accepted}


# ------------------------------------------------------- jawaban bertaip ---

_PUNCT_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)
_SPACE_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Bakukan jawaban bertaip: huruf kecil, tanpa tanda baca, spasi tunggal."""
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = _PUNCT_RE.sub(" ", text)
    return _SPACE_RE.sub(" ", text).strip()


def expand_accepted(gloss: str, alt: list[str] | None = None) -> list[str]:
    """Kembangkan arti menjadi daftar jawaban yang diterima.

    "tua, lama" menghasilkan kalimat utuhnya, "tua", dan "lama". Tujuannya
    supaya pengguna tidak dihukum karena menulis salah satu arti saja.
    """
    out: list[str] = []

    def add(s: str) -> None:
        s = s.strip()
        if s and s not in out:
            out.append(s)

    add(gloss)
    for piece in re.split(r"[,;/]", gloss):
        add(piece)
        add(re.sub(r"\([^)]*\)", "", piece))
    for a in alt or []:
        add(a)
        add(re.sub(r"\([^)]*\)", "", a))
    return [o for o in out if o]


def accepted_set(entry: dict) -> frozenset[str]:
    """Himpunan jawaban yang diterima untuk satu entri, sudah dibakukan."""
    key = (entry["gloss"], tuple(entry.get("alt") or ()))
    cached = _ACCEPTED_CACHE.get(key)
    if cached is None:
        cached = frozenset(
            normalize(a) for a in expand_accepted(entry["gloss"], entry.get("alt"))
        )
        _ACCEPTED_CACHE[key] = cached
    return cached


# ------------------------------------------------------------- pengecoh ---

def _pick_distractors(
    rng: random.Random, pool: list[dict], target: dict, key: str, n: int = 3
) -> list[str]:
    """Pilih n pengecoh, mengutamakan kata dengan kelas kata yang sama."""
    want = target[key]
    same_pos = [e for e in pool if e[key] != want and e.get("pos") == target.get("pos")]
    same_cat = [e for e in pool if e[key] != want and e.get("cat") == target.get("cat")]
    others = [e for e in pool if e[key] != want]
    chosen: list[str] = []
    for bucket in (same_pos, same_cat, others):
        rng.shuffle(bucket)
        for e in bucket:
            if e[key] not in chosen and len(chosen) < n:
                chosen.append(e[key])
        if len(chosen) >= n:
            break
    return chosen[:n]


def _shuffle_options(
    rng: random.Random, correct: str, distractors: list[str]
) -> tuple[list[str], int]:
    opts = [correct] + [d for d in distractors if d != correct]
    rng.shuffle(opts)
    return opts, opts.index(correct)


# ------------------------------------------------------------------ huruf ---

def _letter_face(e: dict) -> str:
    return "%s %s" % (e["upper"], e["lower"])


def letter_sound(e: dict, pool: list[dict], rng: random.Random) -> Question:
    """Soal buatan: huruf ini bunyinya apa?"""
    others = [o["translit"] for o in pool if o["translit"] != e["translit"]]
    rng.shuffle(others)
    options, answer = _shuffle_options(rng, e["translit"], others[:3])
    return Question(
        card_id=e["id"],
        mode="alfabet",
        kind="mcq",
        stage=e["stage"],
        question="Huruf ini bunyinya apa?",
        stimulus_ru=_letter_face(e),
        options=options,
        options_lang="id",
        answer=answer,
        reveal="%s = %s (nama huruf: %s)" % (_letter_face(e), e["sound"], e["name"]),
        reveal_ru=e["example"]["ru"],
        explain="%s — %s. %s" % (e["example"]["ru"], e["example"]["gloss"], e["note"]),
    )


def letter_shape(e: dict, pool: list[dict], rng: random.Random) -> Question:
    """Soal buatan: huruf mana yang berbunyi begini?"""
    others = [o["lower"] for o in pool if o["translit"] != e["translit"]]
    rng.shuffle(others)
    options, answer = _shuffle_options(rng, e["lower"], others[:3])
    return Question(
        card_id=e["id"],
        mode="alfabet",
        kind="mcq",
        stage=e["stage"],
        question="Huruf mana yang berbunyi %s (%s)?" % (e["translit"], e["sound"]),
        stimulus_ru=None,
        options=options,
        options_lang="ru",
        answer=answer,
        reveal="%s = %s" % (_letter_face(e), e["sound"]),
        reveal_ru=e["example"]["ru"],
        explain="%s — %s" % (e["example"]["ru"], e["example"]["gloss"]),
    )


def letter_question(item: dict) -> Question:
    return Question(
        card_id=item["id"],
        mode="alfabet",
        kind="mcq",
        stage=item["stage"],
        question=item["prompt"],
        stimulus_ru=item.get("prompt_ru"),
        options=list(item["options"]),
        options_lang=item["options_lang"],
        answer=item["answer"],
        reveal=item["options"][item["answer"]],
        explain=item.get("explain"),
    )


# --------------------------------------------------------------- kosakata ---

def vocab_detail(e: dict) -> str:
    """Keterangan singkat satu entri kosakata, untuk sisi belakang kartu."""
    bits = [dataio.POS_LABEL.get(e["pos"], e["pos"])]
    if e.get("gender"):
        bits.append(dataio.GENDER_LABEL[e["gender"]])
    if e.get("pluralonly"):
        bits.append("hanya bentuk jamak")
    if e.get("plural"):
        bits.append("jamak: " + e["plural"])
    if e.get("forms"):
        f = e["forms"]
        bits.append("f: %s · n: %s · pl: %s" % (f["f"], f["n"], f["pl"]))
    if e.get("aspect"):
        bits.append(e["aspect"])
    if e.get("pair"):
        bits.append("pasangan: " + e["pair"])
    if e.get("conj"):
        c = e["conj"]
        bits.append("я %s · ты %s · он %s" % (c["sg1"], c["sg2"], c["sg3"]))
    if e.get("root"):
        bits.append("akar: " + e["root"] + "-")
    return " · ".join(bits)


def vocab_ru_to_id(e: dict) -> Question:
    return Question(
        card_id=e["id"],
        mode="kosakata-ru",
        kind="typed",
        stage=e["stage"],
        question="Apa arti kata ini?",
        stimulus_ru=e["ru"],
        options=None,
        accepted=expand_accepted(e["gloss"], e.get("alt")),
        reveal="%s  (%s)" % (e["gloss"], vocab_detail(e)),
        reveal_ru=e["example"]["ru"],
        explain="%s — %s" % (e["example"]["ru"], e["example"]["gloss"]),
    )


def vocab_id_to_ru(e: dict, pool: list[dict], rng: random.Random) -> Question:
    # Pengecoh tidak boleh menerima teks pertanyaan sebagai jawabannya sendiri.
    # Tanpa saringan ini, pertanyaan "kata Rusia untuk 'malam'" bisa memuat
    # ночь dan ве́чер sekaligus, sehingga ada dua jawaban benar.
    prompt_key = normalize(e["gloss"])
    safe = [
        o for o in pool
        if o["id"] != e["id"] and prompt_key not in accepted_set(o)
    ]
    distractors = _pick_distractors(rng, safe, e, "ru", 3)
    options, answer = _shuffle_options(rng, e["ru"], distractors)
    return Question(
        card_id=e["id"],
        mode="kosakata-id",
        kind="mcq",
        stage=e["stage"],
        question="Mana kata Rusia untuk ‘%s’?" % e["gloss"],
        stimulus_ru=None,
        options=options,
        options_lang="ru",
        answer=answer,
        reveal="%s = %s  (%s)" % (e["ru"], e["gloss"], vocab_detail(e)),
        reveal_ru=e["example"]["ru"],
        explain="%s — %s" % (e["example"]["ru"], e["example"]["gloss"]),
    )


# ------------------------------------------------------------- tatabahasa ---

def grammar_question(item: dict) -> Question:
    return Question(
        card_id=item["id"],
        mode="tatabahasa",
        kind="mcq",
        stage=item["stage"],
        question=item["prompt"],
        stimulus_ru=item.get("prompt_ru"),
        options=list(item["options"]),
        options_lang=item["options_lang"],
        answer=item["answer"],
        reveal=item["options"][item["answer"]],
        explain=item.get("explain"),
    )


def falsefriend_question(item: dict) -> Question:
    q = grammar_question(item)
    q.card_id = item["id"]
    return q


# ------------------------------------------------------------------- akar ---

def root_question(item: dict) -> Question:
    return Question(
        card_id=item["id"],
        mode="akar",
        kind="mcq",
        stage=item["stage"],
        question=item["prompt"],
        stimulus_ru=item.get("prompt_ru"),
        options=list(item["options"]),
        options_lang=item["options_lang"],
        answer=item["answer"],
        reveal=item["options"][item["answer"]],
        explain=item.get("explain"),
    )


def root_of_word(family: dict, families: list[dict], rng: random.Random) -> Question:
    """Soal buatan: 'Apa akar kata ini?' Kunci diambil dari data keluarga akar."""
    member = rng.choice(family["members"])
    other_roots = [f["root"] for f in families if f["root"] != family["root"]]
    rng.shuffle(other_roots)
    options, answer = _shuffle_options(rng, family["root"], other_roots[:3])
    return Question(
        card_id=family["id"],
        mode="akar",
        kind="mcq",
        stage=family["stage"],
        question="Apa akar kata dari ‘%s’ berikut?" % member["gloss"],
        stimulus_ru=member["ru"],
        options=options,
        options_lang="ru",
        answer=answer,
        reveal="%s- (%s)" % (family["root"], family["meaning"]),
        explain="%s dibentuk dengan %s dari akar %s- yang bermakna ‘%s’." % (
            member["ru"], member["pattern"], family["root"], family["meaning"]
        ),
    )


def odd_one_out(family: dict, families: list[dict], rng: random.Random) -> Question:
    """Soal buatan: 'Mana yang BUKAN dari akar ini?'."""
    members = [m["ru"] for m in family["members"]]
    rng.shuffle(members)
    keep = members[:3]
    outsiders = [
        m["ru"] for f in families if f["root"] != family["root"] for m in f["members"]
    ]
    outsider = rng.choice(outsiders)
    options = keep + [outsider]
    rng.shuffle(options)
    return Question(
        card_id=family["id"],
        mode="akar",
        kind="mcq",
        stage=family["stage"],
        question="Mana kata yang BUKAN dari akar %s- ?" % family["root"],
        stimulus_ru=None,
        options=options,
        options_lang="ru",
        answer=options.index(outsider),
        reveal=outsider,
        explain="Tiga kata lainnya berakar %s- (%s). %s berakar lain." % (
            family["root"], family["meaning"], outsider
        ),
    )


# ------------------------------------------------------------------- baca ---

def render_level(
    text: str,
    level: int,
    *,
    keep: set[int] | None = None,
    blank: int | None = None,
    yo: bool = True,
) -> str:
    """Tampilkan teks pada level tanda tekanan tertentu.

    level 1: tanda tekanan penuh.
    level 2: tanda tekanan hanya pada kata yang indeksnya ada di `keep`.
    level 3: tanpa tanda tekanan sama sekali.
    `blank` adalah indeks kata yang SELALU dilepas tandanya (kata yang
    ditanyakan), supaya jawabannya tidak terlihat.
    `yo=False` menulis ё sebagai е, seperti teks cetak untuk pembaca dewasa.
    Pilihan itu hanya berlaku pada level 3, karena pada level 1 dan 2 huruf ё
    masih menjadi satu-satunya penanda tekanan kata yang memuatnya; menghapus
    titiknya di sana akan menghilangkan keterangan yang tidak bisa dipulihkan.
    """
    words = text.split(" ")
    keep = keep if keep is not None else set()
    strip3 = strip_stress_and_yo if (level >= 3 and not yo) else strip_stress
    out: list[str] = []
    for i, w in enumerate(words):
        if blank is not None and i == blank:
            out.append(strip3(w))
        elif level == 1:
            out.append(w)
        elif level == 2:
            out.append(w if i in keep else strip_stress(w))
        else:
            out.append(strip3(w))
    return " ".join(out)


def render_item(full_ru: str, level: int, target: int | None) -> str:
    """Tampilan satu soal membaca pada levelnya.

    Pada level 1 dan 2, seluruh kata lain TETAP bertanda tekanan dan hanya
    kata yang ditanyakan yang dilepas tandanya: pembaca menentukan tekanannya
    dari konteks kalimat yang sudah terbaca. Pada level 3 tidak ada satu pun
    tanda tekanan, seperti teks Rusia yang sebenarnya.
    """
    if level >= 3:
        return render_level(full_ru, 3, blank=target)
    n = len(full_ru.split(" "))
    return render_level(full_ru, 2, keep=set(range(n)), blank=target)


def target_word(full_ru: str, index: int) -> str:
    """Kata ke-`index` pada sebuah kalimat, tanpa tanda baca yang menempel."""
    word = full_ru.split(" ")[index]
    return "".join(ch for ch in word if ch not in PUNCT)


def reading_question(item: dict) -> Question:
    level = item["level"]
    if item["type"] == "stress_choice":
        target = item["target"]
        shown = render_item(item["full_ru"], level, target)
        bare = strip_stress(target_word(item["full_ru"], target))
        glosses = item.get("option_glosses") or []
        explain = item.get("explain") or ""
        if glosses:
            detail = "; ".join(
                "%s = %s" % (o, g) for o, g in zip(item["options"], glosses)
            )
            explain = "%s\n   Semua pilihan: %s" % (explain, detail)
        return Question(
            card_id=item["id"],
            mode="baca",
            kind="mcq",
            stage=item["stage"],
            question="Di mana letak tekanan kata yang ditanyakan?",
            stimulus_ru=shown,
            stimulus_label="kata yang ditanyakan: %s" % bare,
            options=list(item["options"]),
            options_lang="ru",
            answer=item["answer"],
            reveal="%s — %s" % (item["full_ru"], item["gloss"]),
            explain=explain,
        )
    if item["type"] == "meaning_choice":
        shown = render_item(item["full_ru"], level, None)
        return Question(
            card_id=item["id"],
            mode="baca",
            kind="mcq",
            stage=item["stage"],
            question="Apa arti kalimat tanpa tanda tekanan berikut?",
            stimulus_ru=shown,
            options=list(item["options"]),
            options_lang="id",
            answer=item["answer"],
            reveal="%s — %s" % (item["full_ru"], item["gloss"]),
            explain=item.get("explain"),
        )
    if item["type"] == "pronounce_choice":
        return Question(
            card_id=item["id"],
            mode="baca",
            kind="mcq",
            stage=item["stage"],
            question=item["prompt"],
            stimulus_ru=item["full_ru"],
            options=list(item["options"]),
            options_lang=item["options_lang"],
            answer=item["answer"],
            reveal="%s — %s" % (item["full_ru"], item["gloss"]),
            explain=item.get("explain"),
        )
    raise ValueError("jenis soal baca tidak dikenal: %s" % item["type"])


def passage_question(p: dict) -> Question:
    shown = render_level(p["ru"], p["level"], keep=set(p.get("keep") or []))
    return Question(
        card_id=p["id"],
        mode="baca",
        kind="selfcheck",
        stage=p["stage"],
        question=(
            "Bacalah dengan suara (Level %d), tentukan letak tekanannya, "
            "lalu bandingkan dengan jawabannya." % p["level"]
        ),
        stimulus_ru=shown,
        reveal="%s — %s" % (p["ru"], p["gloss"]),
        reveal_ru=p["ru"],
        explain=None,
    )


# --------------------------------------------------------------- kumpulan ---

def build_pool(mode: str, stage: int | None, rng: random.Random) -> list[Question]:
    """Bangun seluruh soal yang tersedia untuk satu mode."""
    if mode == "alfabet":
        pool = dataio.letters(stage)
        qs = [letter_sound(e, pool, rng) for e in pool]
        qs += [letter_shape(e, pool, rng) for e in pool]
        qs += [letter_question(i) for i in dataio.letter_items(stage)]
        return qs
    if mode == "kosakata-ru":
        return [vocab_ru_to_id(e) for e in dataio.vocab_entries(stage)]
    if mode == "kosakata-id":
        pool = dataio.vocab_entries(stage)
        return [vocab_id_to_ru(e, pool, rng) for e in pool]
    if mode == "tatabahasa":
        qs = [grammar_question(i) for i in dataio.grammar_items(stage)]
        qs += [falsefriend_question(i) for i in dataio.falsefriend_items(stage)]
        return qs
    if mode == "akar":
        fams = dataio.root_families(stage)
        qs = [root_question(i) for i in dataio.root_items(stage)]
        if len(fams) >= 4:
            qs += [root_of_word(f, fams, rng) for f in fams]
            qs += [odd_one_out(f, fams, rng) for f in fams]
        return qs
    if mode == "baca":
        qs = [reading_question(i) for i in dataio.reading_items(stage)]
        qs += [passage_question(p) for p in dataio.reading_passages(stage)]
        return qs
    raise ValueError("mode tidak dikenal: %s" % mode)


__all__ = [
    "MODES",
    "MODE_LABELS",
    "Question",
    "accepted_set",
    "build_pool",
    "expand_accepted",
    "falsefriend_question",
    "grammar_question",
    "letter_question",
    "letter_shape",
    "letter_sound",
    "normalize",
    "odd_one_out",
    "passage_question",
    "reading_question",
    "render_item",
    "render_level",
    "root_of_word",
    "root_question",
    "target_word",
    "translit_letter",
    "vocab_detail",
    "vocab_id_to_ru",
    "vocab_ru_to_id",
]
