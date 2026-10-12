"""Pengujian alih huruf Latin: kasus yang dipatok dan tidak ada sisa Kiril."""

from __future__ import annotations

import pytest

from rusdrill import dataio
from rusdrill.cyrillic import LETTERS, nfc
from rusdrill.translit import translit, translit_letter

STRESS = "́"

KASUS = [
    ("молоко" + STRESS, "moloko" + STRESS),
    ("рабо" + STRESS + "та", "rabo" + STRESS + "ta"),
    ("щи", "shchi"),
    ("ёлка", "yo" + STRESS + "lka"),
    ("семья" + STRESS, "sem'ya" + STRESS),
    ("объя" + STRESS + "сни", "ob\"ya" + STRESS + "sni"),
    ("Я", "Ya"),
    ("учи" + STRESS + "тель", "uchi" + STRESS + "tel'"),
]


@pytest.mark.parametrize("kiril,latin", KASUS)
def test_kasus_dipatok(kiril, latin):
    assert translit(kiril) == nfc(latin)


def test_e_beriota_di_awal_kata_dan_sesudah_konsonan():
    # нет -> "net" (sesudah konsonan), есть -> "yest'" (di awal kata)
    assert translit("нет") == "net"
    assert translit("есть") == "yest'"


def test_tidak_ada_huruf_kiril_yang_tertinggal():
    sisa = []
    for e in dataio.vocab_entries():
        for teks in (e["ru"], e["example"]["ru"]):
            hasil = translit(teks)
            if any(ch in LETTERS for ch in hasil):
                sisa.append(teks)
    assert not sisa, sisa


def test_alih_huruf_nama_huruf_konsisten_dengan_data():
    """translit_letter harus sepadan dengan kolom translit di data alfabet."""
    beda = []
    for e in dataio.letters():
        hasil = translit_letter(e["upper"], e["lower"])
        # Kolom translit pada data boleh memuat dua bentuk (misalnya "e / ye")
        # dan tanda kutip untuk ь dan ъ.
        bentuk = {b.strip() for b in e["translit"].split("/")}
        if hasil not in bentuk:
            beda.append("%s: translit_letter %r vs data %r"
                        % (e["lower"], hasil, e["translit"]))
    assert not beda, beda


def test_alih_huruf_bersifat_deterministik():
    teks = "Я чита" + STRESS + "ю кни" \
           + STRESS + "гу."
    assert translit(teks) == translit(teks)
