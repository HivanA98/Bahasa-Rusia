#!/usr/bin/env python3
"""Latihan Bahasa Rusia dari dasar, di terminal.

Contoh pemakaian:

    python quiz.py                           sesi campuran 20 menit
    python quiz.py --mode alfabet --new 12   pekan pertama: huruf saja
    python quiz.py --mode kosakata-ru        hanya Rusia ke Indonesia
    python quiz.py --mode baca --stage 3     tekanan dan pelafalan, tahap 1-3
    python quiz.py --translit                tampilkan alih huruf Latin
    python quiz.py --stats                   ringkasan kemajuan
    python quiz.py --reset                   hapus progress.json

Progres disimpan di progress.json di folder proyek.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rusdrill import dataio  # noqa: E402
from rusdrill.cyrillic import has_cyrillic, has_stress, pronounce_text  # noqa: E402
from rusdrill.leitner import MAX_BOX, MIN_BOX, Progress  # noqa: E402
from rusdrill.questions import MODE_LABELS, MODES, Question  # noqa: E402
from rusdrill.session import (  # noqa: E402
    DEFAULT_MINUTES,
    DEFAULT_NEW_PER_SESSION,
    plan_session,
    upcoming_counts,
)
from rusdrill.translit import translit  # noqa: E402

PROGRESS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "progress.json")
RULE = "─" * 62


# ------------------------------------------------------------- tampilan ---

class Style:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def _wrap(self, code: str, text: str) -> str:
        return "\033[%sm%s\033[0m" % (code, text) if self.enabled else text

    def bold(self, t: str) -> str:
        return self._wrap("1", t)

    def dim(self, t: str) -> str:
        return self._wrap("2", t)

    def ok(self, t: str) -> str:
        return self._wrap("32", t)

    def bad(self, t: str) -> str:
        return self._wrap("31", t)

    def info(self, t: str) -> str:
        return self._wrap("36", t)


def setup_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def prompt(text: str) -> str | None:
    """Baca satu masukan pengguna.

    Mengembalikan None bila masukan berakhir (EOF, misalnya saat dijalankan
    dengan masukan dari pipa) atau dihentikan dengan Ctrl+C, sehingga sesi
    berhenti rapi tanpa jejak galat.
    """
    try:
        return input(text)
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def show_ru(text: str, *, use_translit: bool) -> str:
    """Tampilkan teks Kiril, dengan alih huruf di bawahnya bila diminta."""
    if use_translit:
        return "%s\n   %s" % (text, translit(text))
    return text


def show_reveal(text: str, *, use_translit: bool, use_lafal: bool) -> str:
    """Teks jawaban, boleh disertai alih huruf dan pendekatan lafal.

    Pendekatan lafal hanya ditampilkan untuk teks yang BERTANDA TEKANAN.
    Pada modul membaca, teks soalnya sengaja tidak bertanda, dan menampilkan
    lafalnya di sisi soal akan membocorkan jawabannya.
    """
    out = text
    if not has_cyrillic(text):
        return out
    if use_translit:
        out += "\n   " + translit(text)
    if use_lafal and has_stress(text):
        out += "\n   [" + pronounce_text(text) + "]"
    return out


# ----------------------------------------------------------- satu soal ---

def ask(
    q: Question,
    st: Style,
    *,
    use_translit: bool,
    use_lafal: bool,
    index: int,
    total: int,
) -> str | None:
    """Tanyakan satu soal. Kembalikan 'benar', 'salah', 'lewat', atau None (keluar)."""
    print()
    tag = " · ulangan" if q.repeat else ""
    print(st.dim("[%d/%d] %s%s" % (index, total, MODE_LABELS[q.mode], tag)))
    print(st.bold(q.question))
    if q.stimulus_ru:
        print()
        print("   " + show_ru(q.stimulus_ru, use_translit=use_translit))
    if q.stimulus_label:
        print("   " + st.dim(q.stimulus_label))

    if q.kind == "mcq":
        return _ask_mcq(q, st, use_translit=use_translit, use_lafal=use_lafal)
    if q.kind == "typed":
        return _ask_typed(q, st, use_translit=use_translit, use_lafal=use_lafal)
    return _ask_selfcheck(q, st, use_translit=use_translit, use_lafal=use_lafal)


def _reveal(q: Question, st: Style, *, use_translit: bool, use_lafal: bool) -> None:
    if q.reveal:
        label = "Jawaban" if q.kind != "selfcheck" else "Bacaan penuh"
        shown = show_reveal(q.reveal, use_translit=use_translit, use_lafal=use_lafal)
        print("   %s: %s" % (st.info(label), shown))
    if q.explain:
        print("   " + st.dim(q.explain))
    if use_lafal and q.reveal_ru and has_stress(q.reveal_ru):
        print("   " + st.dim("[" + pronounce_text(q.reveal_ru) + "]"))


def _ask_mcq(q: Question, st: Style, *, use_translit: bool, use_lafal: bool) -> str | None:
    assert q.options is not None and q.answer is not None
    print()
    for i, opt in enumerate(q.options, 1):
        shown = opt
        if q.options_lang == "ru" and use_translit:
            shown = "%s   %s" % (opt, st.dim(translit(opt)))
        print("   %d. %s" % (i, shown))
    print()
    while True:
        jawab = prompt("   Pilih nomor (atau l=lewat, k=keluar): ")
        if jawab is None:
            return None
        raw = jawab.strip().lower()
        if raw in ("k", "keluar", "q"):
            return None
        if raw in ("l", "lewat", "s"):
            _reveal(q, st, use_translit=use_translit, use_lafal=use_lafal)
            return "lewat"
        if raw.isdigit() and 1 <= int(raw) <= len(q.options):
            chosen = int(raw) - 1
            if chosen == q.answer:
                print("   " + st.ok("Benar."))
                if q.explain:
                    print("   " + st.dim(q.explain))
                if use_lafal and q.reveal_ru and has_stress(q.reveal_ru):
                    print("   " + st.dim("[" + pronounce_text(q.reveal_ru) + "]"))
                return "benar"
            print("   " + st.bad("Salah. Jawaban: %s" % q.options[q.answer]))
            if q.explain:
                print("   " + st.dim(q.explain))
            return "salah"
        print("   " + st.dim("Masukan tidak dikenali."))


def _ask_typed(q: Question, st: Style, *, use_translit: bool, use_lafal: bool) -> str | None:
    print()
    while True:
        jawab = prompt("   Arti dalam Bahasa Indonesia (?=lihat, l=lewat, k=keluar): ")
        if jawab is None:
            return None
        raw = jawab.strip()
        low = raw.lower()
        if low in ("k", "keluar", "q"):
            return None
        if low in ("l", "lewat", "s"):
            _reveal(q, st, use_translit=use_translit, use_lafal=use_lafal)
            return "lewat"
        if low in ("?", "lihat"):
            _reveal(q, st, use_translit=use_translit, use_lafal=use_lafal)
            return "salah"
        if not raw:
            continue
        if q.is_correct_text(raw):
            print("   " + st.ok("Benar."))
            _reveal(q, st, use_translit=use_translit, use_lafal=use_lafal)
            return "benar"
        print("   " + st.bad("Belum tepat."))
        _reveal(q, st, use_translit=use_translit, use_lafal=use_lafal)
        return "salah"


def _ask_selfcheck(q: Question, st: Style, *, use_translit: bool, use_lafal: bool) -> str | None:
    print()
    jawab = prompt("   Tekan Enter untuk melihat jawaban (k=keluar): ")
    if jawab is None or jawab.strip().lower() in ("k", "keluar", "q"):
        return None
    _reveal(q, st, use_translit=use_translit, use_lafal=use_lafal)
    while True:
        jawab = prompt("   Bacaan Anda tepat? (b=benar, s=salah, l=lewat): ")
        if jawab is None:
            return None
        raw = jawab.strip().lower()
        if raw in ("b", "benar"):
            return "benar"
        if raw in ("s", "salah"):
            return "salah"
        if raw in ("l", "lewat"):
            return "lewat"
        print("   " + st.dim("Masukan tidak dikenali."))


# ------------------------------------------------------------- ringkasan ---

def print_stats(progress: Progress, st: Style) -> None:
    ids = dataio.all_card_ids()
    counts = upcoming_counts(progress, ids)
    boxes = progress.box_counts(ids)
    print(RULE)
    print(st.bold("Ringkasan kemajuan"))
    print(RULE)
    print("  Total kartu di seluruh modul : %d" % len(ids))
    print("  Belum pernah dilatih         : %d" % counts["baru"])
    print("  Jatuh tempo hari ini         : %d" % counts["jatuh_tempo"])
    print("  Belum jatuh tempo            : %d" % counts["belum_jatuh_tempo"])
    print()
    print("  Sebaran kotak Leitner:")
    for b in range(MIN_BOX, MAX_BOX + 1):
        bar = "█" * min(40, boxes[b])
        print("    kotak %d: %4d  %s" % (b, boxes[b], bar))
    seen = [s for s in progress.cards.values() if s.seen]
    if seen:
        total_seen = sum(s.seen for s in seen)
        total_ok = sum(s.correct for s in seen)
        pct = (total_ok / total_seen * 100) if total_seen else 0.0
        print()
        print("  Jawaban tercatat: %d, benar %d (%.0f%%)" % (total_seen, total_ok, pct))
    if progress.sessions:
        print()
        print("  Lima sesi terakhir:")
        for s in progress.sessions[-5:]:
            print("    %s  %3d soal, benar %3d, %.0f menit" % (
                s.get("tanggal", "?"), s.get("soal", 0), s.get("benar", 0),
                s.get("menit", 0),
            ))
    print(RULE)


# ------------------------------------------------------------------ main ---

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="quiz.py",
        description="Latihan Bahasa Rusia dari dasar untuk penutur Bahasa Indonesia.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Mode yang tersedia: " + ", ".join(MODES),
    )
    p.add_argument(
        "--mode", action="append", default=None,
        help="mode latihan; boleh diulang atau dipisah koma. Bawaan: semua mode.",
    )
    p.add_argument("--stage", type=int, default=None, metavar="N",
                   help="batasi materi sampai tahap N (1-6). Bawaan: semua tahap.")
    p.add_argument("--minutes", type=int, default=DEFAULT_MINUTES, metavar="M",
                   help="lama sesi dalam menit (bawaan %d)." % DEFAULT_MINUTES)
    p.add_argument("--limit", type=int, default=None, metavar="N",
                   help="batas jumlah soal dalam satu sesi.")
    p.add_argument("--new", type=int, default=DEFAULT_NEW_PER_SESSION, metavar="N",
                   help="kartu baru per sesi (bawaan %d); 0 = hanya ulangan."
                        % DEFAULT_NEW_PER_SESSION)
    p.add_argument("--translit", action="store_true",
                   help="tampilkan alih huruf Latin (bawaan: mati).")
    p.add_argument("--no-lafal", action="store_true",
                   help="matikan pendekatan lafal pada sisi jawaban (bawaan: hidup).")
    p.add_argument("--seed", type=int, default=None,
                   help="seed acak, untuk mengulang susunan sesi yang sama.")
    p.add_argument("--progress", default=PROGRESS_PATH, metavar="BERKAS",
                   help="lokasi berkas progres.")
    p.add_argument("--stats", action="store_true",
                   help="tampilkan ringkasan lalu keluar.")
    p.add_argument("--reset", action="store_true", help="hapus berkas progres.")
    p.add_argument("--no-color", action="store_true", help="matikan warna.")
    return p.parse_args(argv)


def resolve_modes(raw: list[str] | None) -> list[str]:
    if not raw:
        return list(MODES)
    out: list[str] = []
    for chunk in raw:
        for m in chunk.split(","):
            m = m.strip()
            if not m:
                continue
            if m not in MODES:
                raise SystemExit(
                    "Mode tidak dikenal: %s\nMode yang tersedia: %s"
                    % (m, ", ".join(MODES))
                )
            if m not in out:
                out.append(m)
    return out


def main(argv: list[str] | None = None) -> int:
    setup_stdout()
    args = parse_args(argv)
    st = Style(enabled=not args.no_color and sys.stdout.isatty())

    if args.reset:
        if os.path.exists(args.progress):
            ans = prompt("Hapus %s? Semua progres hilang. (ya/tidak): " % args.progress)
            if ans is None or ans.strip().lower() not in ("ya", "y"):
                print("Dibatalkan.")
                return 0
            os.remove(args.progress)
            print("Berkas progres dihapus.")
        else:
            print("Tidak ada berkas progres untuk dihapus.")
        return 0

    progress = Progress.load(args.progress)
    if args.stats:
        print_stats(progress, st)
        return 0

    if args.stage is not None and not (1 <= args.stage <= dataio.MAX_STAGE):
        raise SystemExit("--stage harus antara 1 dan %d" % dataio.MAX_STAGE)

    use_translit = args.translit or bool(progress.settings.get("translit"))
    use_lafal = not args.no_lafal and progress.settings.get("lafal", True)
    modes = resolve_modes(args.mode)

    plan = plan_session(
        progress,
        modes=modes,
        stage=args.stage,
        minutes=args.minutes,
        new_per_session=args.new,
        limit=args.limit,
        seed=args.seed,
    )

    print(RULE)
    print(st.bold("Latihan Bahasa Rusia"))
    print(RULE)
    print("  Mode   : %s" % ", ".join(modes))
    print("  Tahap  : %s" % (args.stage if args.stage else "semua"))
    print("  Target : %d menit, %d soal tersusun" % (args.minutes, len(plan)))
    print("  Kartu  : %d jatuh tempo, %d baru dalam sesi ini" % (plan.n_due, plan.n_new))
    if use_translit:
        print("  " + st.dim("Alih huruf Latin: aktif (mengikuti tulisan, bukan lafal)"))
    if use_lafal:
        print("  " + st.dim("Pendekatan lafal: aktif pada sisi jawaban"))
    print(RULE)

    if not plan.questions:
        print()
        print("Tidak ada soal yang jatuh tempo hari ini.")
        print("Pilihan: naikkan --new untuk menambah kartu baru, atau jalankan --stats.")
        return 0

    start = time.monotonic()
    deadline = start + args.minutes * 60
    tally = {"benar": 0, "salah": 0, "lewat": 0}
    asked = 0
    quit_early = False
    # Satu kartu hanya sekali menggerakkan kotak Leitner per sesi; kemunculan
    # berikutnya dalam sesi yang sama adalah latihan tambahan saja.
    scored: set[str] = set()

    for i, q in enumerate(plan.questions, 1):
        if asked and time.monotonic() > deadline:
            print()
            print(st.info("Waktu sesi habis."))
            break
        result = ask(
            q, st, use_translit=use_translit, use_lafal=use_lafal,
            index=i, total=len(plan),
        )
        if result is None:
            quit_early = True
            break
        asked += 1
        tally[result] += 1
        if result in ("benar", "salah") and q.card_id not in scored:
            scored.add(q.card_id)
            progress.record_answer(q.card_id, result == "benar")

    minutes = (time.monotonic() - start) / 60
    if asked:
        progress.log_session({
            "tanggal": dt.date.today().isoformat(),
            "mode": ",".join(modes),
            "soal": asked,
            "benar": tally["benar"],
            "salah": tally["salah"],
            "lewat": tally["lewat"],
            "menit": round(minutes, 1),
        })
    progress.settings["translit"] = bool(args.translit) or bool(
        progress.settings.get("translit")
    )
    progress.settings["lafal"] = bool(use_lafal)
    progress.save(args.progress)

    print()
    print(RULE)
    print(st.bold("Sesi selesai" + (" (dihentikan)" if quit_early else "")))
    print(RULE)
    print("  Soal dikerjakan : %d" % asked)
    print("  Benar           : %d" % tally["benar"])
    print("  Salah           : %d" % tally["salah"])
    print("  Dilewati        : %d" % tally["lewat"])
    print("  Lama            : %.1f menit" % minutes)
    print("  Progres         : %s" % args.progress)
    print(RULE)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print()
        print("Dihentikan.")
        raise SystemExit(130)
