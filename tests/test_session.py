"""Pengujian penyusun sesi: batas kartu baru, ulangan, interleaving, urutan tahap."""

from __future__ import annotations

import datetime as dt

from rusdrill import dataio
from rusdrill.leitner import Progress
from rusdrill.questions import MODES
from rusdrill.session import (
    MODE_GROUPS,
    NEW_SHARE,
    plan_session,
    upcoming_counts,
)

HARI = dt.date(2026, 1, 10)


def test_batas_kartu_baru_dihormati():
    p = Progress()
    plan = plan_session(p, new_per_session=6, seed=1, on=HARI)
    assert plan.n_new <= 6 + len(set(MODE_GROUPS.values()))  # pembulatan per kelompok
    assert plan.n_new > 0


def test_new_nol_berarti_hanya_ulangan():
    p = Progress()
    plan = plan_session(p, new_per_session=0, seed=1, on=HARI)
    assert plan.n_new == 0
    assert len(plan) == 0        # belum ada kartu yang jatuh tempo


def test_kartu_belum_jatuh_tempo_tidak_muncul():
    p = Progress()
    for cid in dataio.all_card_ids():
        p.record_answer(cid, True, HARI)      # semua naik ke kotak 2, jeda 1 hari
    plan = plan_session(p, new_per_session=0, seed=1, on=HARI)
    assert len(plan) == 0
    besok = plan_session(p, new_per_session=0, seed=1, on=HARI + dt.timedelta(days=1))
    assert len(besok) > 0


def test_ulangan_tidak_tergeser_habis_oleh_materi_baru():
    p = Progress()
    # Latih separuh kartu kemarin supaya hari ini jatuh tempo.
    ids = dataio.all_card_ids()[:120]
    kemarin = HARI - dt.timedelta(days=1)
    for cid in ids:
        p.record_answer(cid, False, kemarin)   # kotak 1, jatuh tempo hari itu juga
    plan = plan_session(p, new_per_session=20, limit=40, seed=2, on=HARI)
    baru = sum(1 for q in plan.questions if p.is_new(q.card_id))
    assert baru <= max(1, int(40 * NEW_SHARE)) + 1
    assert baru < len(plan)


def test_interleaving_mencampur_mode():
    p = Progress()
    plan = plan_session(p, new_per_session=12, limit=30, seed=3, on=HARI)
    modes = [q.mode for q in plan.questions[:8]]
    assert len(set(modes)) >= 3, modes


def test_satu_kata_dilatih_dua_arah():
    """Jatah kartu baru dibagi per KELOMPOK, sehingga kata yang sama muncul
    pada kedua arah, bukan dua kata berbeda untuk masing-masing arah."""
    p = Progress()
    plan = plan_session(p, modes=["kosakata-ru", "kosakata-id"],
                        new_per_session=4, seed=4, on=HARI)
    ru = {q.card_id for q in plan.questions if q.mode == "kosakata-ru"}
    idn = {q.card_id for q in plan.questions if q.mode == "kosakata-id"}
    assert ru and idn
    assert ru == idn


def test_materi_baru_masuk_menurut_urutan_tahap():
    p = Progress()
    plan = plan_session(p, modes=["kosakata-ru"], new_per_session=6, seed=5, on=HARI)
    tahap = {q.stage for q in plan.questions}
    assert tahap == {1}, tahap


def test_pembatasan_tahap():
    p = Progress()
    plan = plan_session(p, stage=2, new_per_session=10, limit=40, seed=6, on=HARI)
    assert all(q.stage is None or q.stage <= 2 for q in plan.questions)


def test_sesi_dapat_diulang_dengan_seed_sama():
    p1, p2 = Progress(), Progress()
    a = plan_session(p1, new_per_session=8, seed=7, on=HARI)
    b = plan_session(p2, new_per_session=8, seed=7, on=HARI)
    assert [q.card_id for q in a.questions] == [q.card_id for q in b.questions]
    assert [q.question for q in a.questions] == [q.question for q in b.questions]


def test_seed_berbeda_menghasilkan_susunan_berbeda():
    p1, p2 = Progress(), Progress()
    a = plan_session(p1, new_per_session=8, seed=1, on=HARI)
    b = plan_session(p2, new_per_session=8, seed=2, on=HARI)
    assert [q.card_id for q in a.questions] != [q.card_id for q in b.questions]


def test_lintasan_kedua_ditandai_ulangan():
    p = Progress()
    plan = plan_session(p, new_per_session=4, limit=40, seed=8, on=HARI)
    ulangan = [q for q in plan.questions if q.repeat]
    assert ulangan, "sesi longgar seharusnya mengulang kartu baru di akhir"
    kartu_baru = {q.card_id for q in plan.questions if not q.repeat}
    assert all(q.card_id in kartu_baru for q in ulangan)


def test_batas_jumlah_soal():
    p = Progress()
    plan = plan_session(p, new_per_session=30, limit=12, seed=9, on=HARI)
    assert len(plan) <= 12


def test_setiap_mode_bisa_dijalankan_sendiri():
    for m in MODES:
        p = Progress()
        plan = plan_session(p, modes=[m], new_per_session=4, seed=10, on=HARI)
        assert len(plan) > 0, m
        assert {q.mode for q in plan.questions} == {m}


def test_ringkasan_kemajuan():
    p = Progress()
    ids = dataio.all_card_ids()
    r = upcoming_counts(p, ids)
    assert r["baru"] == len(ids)
    p.record_answer(ids[0], True, HARI)
    r = upcoming_counts(p, ids, HARI)
    assert r["baru"] == len(ids) - 1
    assert r["belum_jatuh_tempo"] == 1
