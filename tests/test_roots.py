"""Pengujian keluarga akar kata.

Yang bisa diperiksa mesin hanyalah bahwa huruf akar benar-benar MUNCUL
BERURUTAN di dalam kata turunannya. Mesin tidak bisa memastikan bahwa akar itu
memang akar kata tersebut secara etimologis: akar keliru yang kebetulan
hurufnya cocok akan tetap lolos. Lihat data/NEEDS_REVIEW.md.
"""

from __future__ import annotations

from rusdrill import dataio
from rusdrill.cyrillic import strip_stress


def subsequence(root: str, word: str) -> bool:
    """True bila huruf akar muncul berurutan (boleh berselang) di dalam kata."""
    i = 0
    for ch in word:
        if i < len(root) and ch == root[i]:
            i += 1
    return i == len(root)


def _bare(word: str) -> str:
    return strip_stress(word).lower()


def test_huruf_akar_muncul_pada_kata_turunan():
    salah = []
    for fam in dataio.root_families():
        roots = [fam["root"]] + (fam.get("variants") or [])
        for m in fam["members"]:
            if not any(subsequence(r, _bare(m["ru"])) for r in roots):
                salah.append("%s: %s tidak memuat akar %s" % (fam["id"], m["ru"], roots))
    assert not salah, salah


def test_varian_akar_terbukti_dipakai_atau_dijelaskan():
    """Setiap varian akar harus muncul pada anggota keluarga ATAU di catatannya.

    Sebagian varian hanya muncul pada bentuk terkonjugasi yang tidak masuk
    daftar anggota (пиш- pada пишу́). Varian semacam itu wajib disebut
    di dalam catatan keluarganya, supaya tidak menjadi keterangan yang
    menggantung tanpa contoh.
    """
    menganggur = []
    for fam in dataio.root_families():
        catatan = _bare(fam.get("note") or "")
        for v in fam.get("variants") or []:
            pada_anggota = any(subsequence(v, _bare(m["ru"])) for m in fam["members"])
            pada_catatan = v in catatan
            if not (pada_anggota or pada_catatan):
                menganggur.append(
                    "%s: varian %s tidak dipakai anggota dan tidak dijelaskan di catatan"
                    % (fam["id"], v))
    assert not menganggur, menganggur


def test_keluarga_yang_punya_varian_wajib_punya_catatan():
    """Perubahan bunyi akar harus dijelaskan, bukan dibiarkan mengejutkan."""
    kurang = [
        fam["id"] for fam in dataio.root_families()
        if fam.get("variants") and not (fam.get("note") or "").strip()
    ]
    assert not kurang, "keluarga dengan varian akar tanpa catatan: %s" % kurang


def test_satu_kata_tidak_diklaim_dua_keluarga():
    seen: dict[str, str] = {}
    bentrok = []
    for fam in dataio.root_families():
        for m in fam["members"]:
            kata = _bare(m["ru"])
            if kata in seen and seen[kata] != fam["id"]:
                bentrok.append("%s diklaim %s dan %s" % (kata, seen[kata], fam["id"]))
            seen[kata] = fam["id"]
    assert not bentrok, bentrok


def test_akar_di_vocab_sejalan_dengan_kata_nya():
    salah = [
        "%s: akar %s tidak muncul pada %s" % (e["id"], e["root"], e["ru"])
        for e in dataio.vocab_entries()
        if e.get("root") and not subsequence(e["root"], _bare(e["ru"]))
    ]
    assert not salah, salah


def test_akar_di_vocab_sejalan_dengan_roots_json():
    """Bila kata yang sama ada di kedua berkas, akarnya tidak boleh berbeda."""
    fam_of: dict[str, str] = {}
    for fam in dataio.root_families():
        for m in fam["members"]:
            fam_of[_bare(m["ru"])] = fam["root"]
    bentrok = []
    for e in dataio.vocab_entries():
        akar = fam_of.get(_bare(e["ru"]))
        if akar and e.get("root") and e["root"] != akar:
            bentrok.append("%s: vocab %s, roots %s" % (e["ru"], e["root"], akar))
    assert not bentrok, bentrok


def test_contoh_afiks_memuat_akarnya():
    salah = []
    for p in dataio.root_patterns():
        for x in p["examples"]:
            if not subsequence(x["root"], _bare(x["ru"])):
                salah.append("%s: %s tidak memuat akar %s" % (p["id"], x["ru"], x["root"]))
    assert not salah, salah


def test_setiap_keluarga_punya_minimal_tiga_anggota():
    kurang = [
        fam["id"] for fam in dataio.root_families() if len(fam["members"]) < 3
    ]
    assert not kurang, "keluarga terlalu kecil untuk memperlihatkan polanya: %s" % kurang


def test_afiks_berjenis_sah():
    salah = [p["id"] for p in dataio.root_patterns()
             if p["type"] not in ("awalan", "akhiran")]
    assert not salah, salah
