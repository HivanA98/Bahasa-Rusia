#!/usr/bin/env python3
"""Buat lembar kerja Markdown beserta kunci jawaban terpisah.

    python tools/build_worksheets.py

Hasilnya:
  worksheets/ws-NN.md                 lembar kerja (tanpa jawaban)
  worksheets/answers/ws-NN-kunci.md   kunci jawaban

Isi lembar kerja diambil langsung dari data/*.json dengan generator acak
ber-seed tetap, sehingga menjalankan ulang skrip ini menghasilkan lembar yang
sama persis. Kunci jawaban dibuat pada proses yang sama dengan soalnya,
sehingga tidak mungkin tidak sinkron.
"""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rusdrill import dataio  # noqa: E402
from rusdrill.cyrillic import strip_stress  # noqa: E402
from rusdrill.questions import target_word, vocab_detail  # noqa: E402

ROOT = dataio.ROOT
WS_DIR = os.path.join(ROOT, "worksheets")
KEY_DIR = os.path.join(WS_DIR, "answers")

#: (nomor lembar, tahap). Dua lembar per tahap, enam tahap.
PLAN = [(n, (n + 1) // 2) for n in range(1, 13)]

N_LETTERS = 8
N_VOCAB_RU = 8
N_VOCAB_ID = 6
N_GRAMMAR = 5
N_ROOTS = 4
N_READING = 3
BLANK = " " * 20


class Picker:
    """Pengambil butir yang menghindari pengulangan antar lembar kerja."""

    def __init__(self, seed: int) -> None:
        self.rng = random.Random(seed)
        self.used: set[str] = set()

    def take(self, pool: list[dict], n: int, key: str = "id") -> list[dict]:
        fresh = [x for x in pool if x[key] not in self.used]
        self.rng.shuffle(fresh)
        chosen = fresh[:n]
        if len(chosen) < n:
            # Kolam sudah habis; ulangi butir lama agar lembar tetap penuh.
            rest = [x for x in pool if x[key] not in {c[key] for c in chosen}]
            self.rng.shuffle(rest)
            chosen += rest[: n - len(chosen)]
        for c in chosen:
            self.used.add(c[key])
        return chosen


def _mcq_block(lines: list[str], n: int, item: dict) -> None:
    lines.append("%d. %s" % (n, item["prompt"]))
    if item.get("prompt_ru"):
        lines.append("")
        lines.append("   > %s" % item["prompt_ru"])
    lines.append("")
    for i, opt in enumerate(item["options"]):
        lines.append("   %s. %s" % (chr(ord("a") + i), opt))
    lines.append("")
    lines.append("   Jawaban: ____")
    lines.append("")


def build_worksheet(number: int, stage: int, pickers: dict[str, Picker]) -> tuple[str, str]:
    letter_pool = [e for e in dataio.letters() if e["stage"] <= stage]
    vocab_pool = [e for e in dataio.vocab_entries() if e["stage"] <= stage]
    grammar_pool = [i for i in dataio.grammar_items() if i["stage"] <= stage]
    root_pool = [f for f in dataio.root_families() if f["stage"] <= stage]
    reading_pool = [
        i for i in dataio.reading_items()
        if i["stage"] <= stage and i["type"] == "stress_choice"
    ]

    letters = pickers["letters"].take(letter_pool, min(N_LETTERS, len(letter_pool)))
    v_ru = pickers["vocab_ru"].take(vocab_pool, N_VOCAB_RU)
    v_id = pickers["vocab_id"].take(vocab_pool, N_VOCAB_ID)
    gram = pickers["grammar"].take(grammar_pool, min(N_GRAMMAR, len(grammar_pool)))
    roots = pickers["roots"].take(root_pool, min(N_ROOTS, len(root_pool)))
    read = pickers["reading"].take(reading_pool, min(N_READING, len(reading_pool)))

    rng = random.Random(1000 + number)

    ws: list[str] = []
    key: list[str] = []
    tag = "ws-%02d" % number

    ws.append("# Lembar kerja %02d · tahap %d" % (number, stage))
    ws.append("")
    ws.append(
        "Kerjakan dengan tulisan tangan tanpa membuka data. Menuliskan tanda "
        "tekanan sendiri adalah bagian dari latihannya. Perkiraan waktu 20-30 menit."
    )
    ws.append("")
    ws.append("Kunci jawaban: `worksheets/answers/%s-kunci.md`" % tag)
    ws.append("")

    key.append("# Kunci jawaban · lembar kerja %02d · tahap %d" % (number, stage))
    key.append("")
    key.append("Soal: `worksheets/%s.md`" % tag)
    key.append("")

    # --- A. Huruf ---------------------------------------------------------
    ws.append("## A. Tulis bunyi dan nama huruf berikut")
    ws.append("")
    ws.append("| No | Huruf | Bunyi | Nama huruf |")
    ws.append("|---:|:------|:------|:-----------|")
    key.append("## A. Huruf")
    key.append("")
    key.append("| No | Huruf | Bunyi | Nama huruf | Contoh |")
    key.append("|---:|:------|:------|:-----------|:-------|")
    for i, e in enumerate(letters, 1):
        ws.append("| %d | %s %s | %s | %s |" % (i, e["upper"], e["lower"], BLANK, BLANK))
        key.append("| %d | %s %s | %s (%s) | %s | %s = %s |" % (
            i, e["upper"], e["lower"], e["translit"], e["sound"], e["name"],
            e["example"]["ru"], e["example"]["gloss"]))
    ws.append("")
    key.append("")

    # --- B. Kosakata Rusia ke Indonesia -----------------------------------
    ws.append("## B. Tulis arti kata berikut dalam Bahasa Indonesia")
    ws.append("")
    ws.append("| No | Kata | Arti |")
    ws.append("|---:|:-----|:-----|")
    key.append("## B. Arti kata")
    key.append("")
    key.append("| No | Kata | Arti | Keterangan |")
    key.append("|---:|:-----|:-----|:-----------|")
    for i, e in enumerate(v_ru, 1):
        ws.append("| %d | %s | %s |" % (i, e["ru"], BLANK))
        key.append("| %d | %s | %s | %s |" % (i, e["ru"], e["gloss"], vocab_detail(e)))
    ws.append("")
    key.append("")

    # --- C. Kosakata Indonesia ke Rusia -----------------------------------
    ws.append("## C. Tulis kata Rusia beserta tanda tekanannya")
    ws.append("")
    ws.append("| No | Arti | Kata Rusia |")
    ws.append("|---:|:-----|:-----------|")
    key.append("## C. Kata Rusia")
    key.append("")
    key.append("| No | Arti | Kata Rusia | Contoh pemakaian |")
    key.append("|---:|:-----|:-----------|:-----------------|")
    for i, e in enumerate(v_id, 1):
        ws.append("| %d | %s | %s |" % (i, e["gloss"], BLANK))
        key.append("| %d | %s | %s | %s = %s |" % (
            i, e["gloss"], e["ru"], e["example"]["ru"], e["example"]["gloss"]))
    ws.append("")
    key.append("")

    # --- D. Tata bahasa ----------------------------------------------------
    ws.append("## D. Tata bahasa: pilih satu jawaban")
    ws.append("")
    key.append("## D. Tata bahasa")
    key.append("")
    for i, item in enumerate(gram, 1):
        _mcq_block(ws, i, item)
        letter = chr(ord("a") + item["answer"])
        key.append("%d. **%s** — %s" % (i, letter, item["options"][item["answer"]]))
        if item.get("explain"):
            key.append("   %s" % item["explain"])
        key.append("   (topik %s: %s)" % (item["topic_id"], item["topic_title"]))
        key.append("")

    # --- E. Akar kata ------------------------------------------------------
    ws.append("## E. Akar kata")
    ws.append("")
    ws.append("Tulis akar kata dari setiap kata berikut, lalu artinya.")
    ws.append("")
    ws.append("| No | Kata | Akar | Arti |")
    ws.append("|---:|:-----|:-----|:-----|")
    key.append("## E. Akar kata")
    key.append("")
    key.append("| No | Kata | Akar | Afiks | Arti |")
    key.append("|---:|:-----|:-----|:------|:-----|")
    d_items = [(fam, rng.choice(fam["members"])) for fam in roots]
    for i, (fam, member) in enumerate(d_items, 1):
        ws.append("| %d | %s | %s | %s |" % (i, member["ru"], BLANK, BLANK))
        key.append("| %d | %s | %s- | %s | %s |" % (
            i, member["ru"], fam["root"], member["pattern"], member["gloss"]))
    ws.append("")
    key.append("")

    # --- F. Tekanan --------------------------------------------------------
    ws.append("## F. Tekanan dan pelafalan")
    ws.append("")
    key.append("## F. Tekanan dan pelafalan")
    key.append("")

    if not read:
        # Pada tahap awal belum ada soal tekanan di data, karena kalimatnya
        # memerlukan kosakata yang belum diperkenalkan. Sebagai gantinya,
        # kata bersuku banyak dari tahap ini dilatih satu per satu.
        kata = [e for e in vocab_pool if len(strip_stress(e["ru"]).split(" ")) == 1
                and sum(1 for c in strip_stress(e["ru"]).lower()
                        if c in "аеёиоуыэюя") > 1]
        kata = pickers["tekanan"].take(kata, min(N_READING + 2, len(kata)))
        ws.append(
            "Kata berikut ditulis tanpa tanda tekanan, seperti tulisan Rusia yang "
            "sebenarnya. Tulis ulang dengan tanda tekanan di tempat yang tepat, "
            "lalu tulis artinya."
        )
        ws.append("")
        for i, e in enumerate(kata, 1):
            ws.append("%d. %s" % (i, strip_stress(e["ru"])))
            ws.append("")
            ws.append("   Bertanda tekanan: _______________________________________")
            ws.append("")
            ws.append("   Arti: ___________________________________________________")
            ws.append("")
            key.append("%d. %s — %s" % (i, e["ru"], e["gloss"]))
            key.append("   %s" % e["example"]["ru"])
            key.append("")
        ws.append("---")
        ws.append("")
        ws.append(
            "Setelah selesai, cocokkan dengan kunci jawaban. Butir yang salah "
            "sebaiknya dilatih lagi lewat `python quiz.py`, bukan hanya dibaca ulang."
        )
        ws.append("")
        return "\n".join(ws), "\n".join(key)

    ws.append(
        "Kalimat berikut ditulis tanpa tanda tekanan, seperti teks Rusia yang "
        "sebenarnya. Tulis ulang dengan tanda tekanan pada kata kunci, lalu "
        "tulis artinya."
    )
    ws.append("")
    for i, item in enumerate(read, 1):
        bare_sentence = strip_stress(item["full_ru"])
        bare_word = strip_stress(target_word(item["full_ru"], item["target"]))
        ws.append("%d. %s   (kata kunci: %s)" % (i, bare_sentence, bare_word))
        ws.append("")
        ws.append("   Bertanda tekanan: _______________________________________")
        ws.append("")
        ws.append("   Arti: ___________________________________________________")
        ws.append("")
        key.append("%d. %s" % (i, item["full_ru"]))
        key.append("   Arti: %s" % item["gloss"])
        key.append("   Kata kunci %s dibaca %s." % (
            bare_word, item["options"][item["answer"]]))
        if item.get("explain"):
            key.append("   %s" % item["explain"])
        if item.get("option_glosses"):
            other = "; ".join(
                "%s = %s" % (o, g)
                for j, (o, g) in enumerate(zip(item["options"], item["option_glosses"]))
                if j != item["answer"]
            )
            if other:
                key.append("   Bacaan lain yang mungkin tetapi tidak cocok: %s" % other)
        key.append("")

    ws.append("---")
    ws.append("")
    ws.append(
        "Setelah selesai, cocokkan dengan kunci jawaban. Butir yang salah "
        "sebaiknya dilatih lagi lewat `python quiz.py`, bukan hanya dibaca ulang."
    )
    ws.append("")

    return "\n".join(ws), "\n".join(key)


def main() -> int:
    os.makedirs(WS_DIR, exist_ok=True)
    os.makedirs(KEY_DIR, exist_ok=True)
    pickers = {
        name: Picker(seed)
        for name, seed in (
            ("letters", 7), ("vocab_ru", 11), ("vocab_id", 22), ("grammar", 33),
            ("roots", 44), ("reading", 55), ("tekanan", 66),
        )
    }
    index: list[str] = [
        "# Lembar kerja",
        "",
        "Latihan tertulis yang dibuat dari `data/*.json` oleh "
        "`tools/build_worksheets.py`. Jangan menyunting berkas di folder ini; "
        "sunting datanya lalu jalankan ulang skripnya.",
        "",
        "| Lembar | Tahap | Kunci |",
        "|:-------|------:|:------|",
    ]
    for number, stage in PLAN:
        ws, key = build_worksheet(number, stage, pickers)
        tag = "ws-%02d" % number
        with open(os.path.join(WS_DIR, "%s.md" % tag), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(ws)
        with open(os.path.join(KEY_DIR, "%s-kunci.md" % tag), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(key)
        index.append("| [%s.md](%s.md) | %d | [answers/%s-kunci.md](answers/%s-kunci.md) |"
                     % (tag, tag, stage, tag, tag))
        print("  worksheets/%s.md  +  worksheets/answers/%s-kunci.md" % (tag, tag))
    index.append("")
    with open(os.path.join(WS_DIR, "README.md"), "w",
              encoding="utf-8", newline="\n") as f:
        f.write("\n".join(index))
    print("  worksheets/README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
