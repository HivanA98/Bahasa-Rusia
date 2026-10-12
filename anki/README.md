# Ekspor Anki

Berkas di folder ini dibuat ulang oleh `python tools/build_exports.py` dari
`data/*.json`. Jangan menyuntingnya langsung.

Setiap berkas memakai pengarah Anki 2.1.55 ke atas:

```
#separator:Comma
#html:false
#tags column:N
```

Bila versi Anki Anda tidak mengenali ketiga baris itu, hapus semuanya lalu
atur pemisah dan kolom tag secara manual pada dialog impor.

## Pemetaan kolom

### alfabet.csv

| Kolom | Isi |
|------:|:----|
| 1 | Huruf besar dan kecil (А а) |
| 2 | Alih huruf dan bunyinya |
| 3 | Nama huruf dalam bahasa Rusia |
| 4 | Kata contoh |
| 5 | Pendekatan lafal kata contoh |
| 6 | Arti kata contoh |
| 7 | Catatan |
| 8 | Tag |

### kosakata.csv

| Kolom | Isi |
|------:|:----|
| 1 | Kata Rusia bertanda tekanan |
| 2 | Arti Bahasa Indonesia |
| 3 | Keterangan (kelas kata, gender, jamak, aspek, konjugasi, akar) |
| 4 | Pendekatan lafal |
| 5 | Contoh kalimat |
| 6 | Arti contoh kalimat |
| 7 | Alih huruf Latin |
| 8 | Catatan |
| 9 | Tag |

### tatabahasa.csv

| Kolom | Isi |
|------:|:----|
| 1 | Pertanyaan (ditambah teks Rusia bila ada) |
| 2 | Jawaban benar |
| 3 | Penjelasan |
| 4 | Nama topik |
| 5 | Tag |

### akar.csv

| Kolom | Isi |
|------:|:----|
| 1 | Kata Rusia |
| 2 | Arti |
| 3 | Akar |
| 4 | Makna akar |
| 5 | Afiks yang dipakai |
| 6 | Pendekatan lafal |
| 7 | Tag |

### baca.csv

| Kolom | Isi |
|------:|:----|
| 1 | Teks tanpa tanda tekanan (sisi depan) |
| 2 | Teks bertanda tekanan penuh |
| 3 | Pendekatan lafal |
| 4 | Arti |
| 5 | Level atau penjelasan |
| 6 | Tag |

### teman-palsu.csv

| Kolom | Isi |
|------:|:----|
| 1 | Kata Rusia |
| 2 | Arti sebenarnya |
| 3 | Arti yang sering disangka |
| 4 | Kata Rusia untuk sangkaan itu |
| 5 | Catatan |
| 6 | Tag |

## Catatan

Bila Anda memakai Anki, pakailah penjadwalan Anki dan jangan menjalankan
`quiz.py` untuk materi yang sama. `progress.json` dan koleksi Anki tidak saling
tahu, sehingga satu kartu akan dijadwalkan oleh dua sistem sekaligus.

Tanda tekanan ditulis sebagai U+0301 sesudah huruf vokalnya. Bila tanda itu
tampak bergeser di Anki, ubah fontnya ke font yang mendukung Kiril dengan baik
(misalnya PT Serif atau Georgia).
