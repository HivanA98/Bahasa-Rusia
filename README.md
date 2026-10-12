# Latihan Bahasa Rusia dari Dasar

Bahan latihan Bahasa Rusia untuk pelajar penutur Bahasa Indonesia yang **mulai
dari nol**: belum mengenal satu pun huruf Kiril.

Materi dimulai benar-benar dari awal — 33 huruf alfabet, termasuk
huruf yang bentuknya mirip huruf Latin tetapi bunyinya berbeda (Р dibaca r, Н
dibaca n, С dibaca s, У dibaca u) — lalu naik ke kosakata, keenam kasus, akar
kata, dan membaca teks tanpa tanda tekanan seperti tulisan Rusia yang
sebenarnya. Sasarannya tingkat A1 menuju A2.

| | |
|:--|:--|
| Alfabet Kiril | 33 huruf, 12 soal |
| Kosakata | 209 entri, 6 tahap |
| Topik tata bahasa | 14 topik, 70 soal |
| Keluarga akar kata | 14 keluarga (61 kata), 12 afiks, 10 soal |
| Tekanan dan pelafalan | 12 teks, 23 soal, 3 level |
| Teman palsu dan serapan | 18 kata, 4 catatan, 10 soal |
| Total kartu | 393 |
| Lembar kerja tertulis | 12 lembar + 12 kunci jawaban |
| Pengujian otomatis | 232 |

## Dua cara memakai

### 1. Aplikasi kartu di browser

Buka `index.html` langsung dari berkas (`file://`) — datanya dimuat lewat tag
`<script>`, bukan `fetch()`, sehingga tidak perlu peladen sama sekali. Untuk
menjalankannya sebagai situs:

```bash
python -m http.server 8766
```

lalu buka <http://localhost:8766>. Folder ini juga siap diunggah ke GitHub
Pages apa adanya (sudah ada `.nojekyll`).

Enam modul dalam bentuk kartu bolak-balik: alfabet, kosakata (dua arah), tata
bahasa (pilihan ganda), akar kata, tekanan dan pelafalan, serta teman palsu.
Sakelar "Sembunyikan tekanan" mengubah kartu kosakata mana pun menjadi latihan
membaca tanpa tanda tekanan, dan sakelar "ё → е" menulis ё sebagai е seperti
surat kabar Rusia. Progres memakai lima kotak Leitner yang sama dengan versi
terminal dan tersimpan di `localStorage` peramban Anda sendiri.

Pintasan papan ketik: `Spasi` balik kartu · `←` `→` navigasi · `1`–`4` pilih
jawaban · `H` sudah hafal · `B` belum hafal · `S` acak · `T` alih huruf ·
`L` lafal · `/` cari.

### 2. Latihan di terminal

`python quiz.py` memberi hal yang tidak ada di versi web: jawaban yang
**ditulis sendiri** (bukan pilihan ganda), sesi berbatas waktu, interleaving
antar modul, pembatasan materi baru per sesi, dan pengenalan materi menurut
urutan tahap. Rinciannya ada di bawah.

Progres kedua versi terpisah: aplikasi web memakai `localStorage`, versi
terminal memakai `progress.json`. Keduanya tidak saling tahu, jadi pilih salah
satu untuk materi yang sama.

## Dua alat bantu Latin, dan kapan mematikannya

| Alat | Mengikuti | Contoh | Bawaan |
|:-----|:----------|:-------|:-------|
| Alih huruf (`--translit`) | **tulisan** | молоко́ → `molokó` | mati |
| Pendekatan lafal | **lafal** | молоко́ → `ma-la-KO` | hidup, hanya di sisi jawaban |

Alih huruf sengaja dimatikan secara bawaan: penyangga Latin membuat mata
berhenti membaca huruf Kiril. Nyalakan pada pekan pertama bila perlu, lalu
matikan.

Pendekatan lafal menuliskan suku kata bertekanan dengan HURUF BESAR dan
menerapkan kaidah yang bisa dihitung mesin: vokal tanpa tekanan melemah
(о menjadi a, е dan я menjadi i), konsonan bersuara melemah di akhir kata
(хлеб → `khlyep`), huruf г pada akhiran -ого dibaca v, dan beberapa kekecualian
leksikal (что → `shto`). Lafal **tidak pernah** ditampilkan pada sisi soal
modul membaca, karena justru letak tekanan itulah yang ditanyakan di sana.

Keduanya hanya pendekatan, bukan transkripsi fonetik ilmiah.

## Yang TIDAK ada di sini

- **Tidak ada rekaman suara.** Pendekatan lafal berupa tulisan Latin, dan itu
  tidak bisa menggantikan mendengarkan penutur asli.
- **Tidak ada latihan menyimak dan berbicara.**
- **Tidak ada tabel kasus yang lengkap.** Keenam kasus diperkenalkan beserta
  fungsinya dan akhiran yang paling lazim, bukan seluruh pola deklinasi.
- **Tidak ada janji hasil.** Kecepatan belajar setiap orang berbeda-beda.

## Persyaratan

Python 3.10 atau lebih baru. Tidak ada pustaka pihak ketiga yang perlu dipasang
untuk menjalankan latihannya; `pytest` hanya diperlukan untuk menjalankan
pengujian.

Terminal Anda perlu bisa menampilkan huruf Kiril beserta tanda tekanannya. Di
Windows, Windows Terminal menampilkannya jauh lebih baik daripada `cmd.exe`
lama. Bila tanda tekanan tampak bergeser, itu masalah font terminal, bukan
datanya.

## Mulai cepat

Pekan pertama sebaiknya dihabiskan untuk huruf saja:

```bash
python quiz.py --mode alfabet --new 12
```

Pada simulasi penjadwal, seluruh 45 kartu alfabet (33 huruf dan 12 soal) selesai
diperkenalkan dalam **4 sesi** dengan pengaturan itu.

Sesudah huruf terasa cukup, jalankan sesi campuran:

```bash
python quiz.py
```

Sesi bawaan: 20 menit, campuran semua mode, 8 kartu baru. Progres tersimpan di
`progress.json`.

```bash
python quiz.py --stats
```

## Bendera baris perintah

| Bendera | Arti |
|:--------|:-----|
| `--mode MODE` | Batasi mode. Boleh diulang atau dipisah koma. Bawaan: semua. |
| `--stage N` | Batasi materi sampai tahap N (1-6). |
| `--minutes M` | Lama sesi dalam menit (bawaan 20). Sesi berhenti saat waktunya habis. |
| `--limit N` | Batas jumlah soal dalam satu sesi. |
| `--new N` | Kartu baru per sesi (bawaan 8). `--new 0` berarti hanya mengulang. |
| `--translit` | Tampilkan alih huruf Latin di bawah teks Kiril. |
| `--no-lafal` | Matikan pendekatan lafal pada sisi jawaban. |
| `--seed N` | Nilai awal pengacak, untuk mengulang susunan sesi yang sama. |
| `--progress BERKAS` | Lokasi berkas progres selain `progress.json`. |
| `--stats` | Tampilkan ringkasan kemajuan lalu keluar. |
| `--reset` | Hapus berkas progres (meminta konfirmasi). |
| `--no-color` | Matikan warna. |

Mode yang tersedia:

| Mode | Isi |
|:-----|:----|
| `alfabet` | Huruf ke bunyi dan bunyi ke huruf, serta soal jebakan huruf mirip Latin. |
| `kosakata-ru` | Rusia ke Indonesia. Jawaban **ditulis** (bukan pilihan ganda). |
| `kosakata-id` | Indonesia ke Rusia. Pilihan ganda. |
| `tatabahasa` | Soal tata bahasa dan teman palsu. |
| `akar` | Akar kata dan afiks, termasuk soal yang dibuat otomatis dari data. |
| `baca` | Tekanan dan pelafalan: tentukan letak tekanan, pilih arti, dan baca sendiri. |

Di dalam sesi: ketik nomor untuk pilihan ganda, `l` untuk melewati, `k` untuk
keluar, `?` untuk melihat jawaban pada soal yang jawabannya ditulis (dihitung
salah).

## Isi materi

### Modul 1 — Alfabet Kiril (`data/alphabet.json`)

33 huruf, dibagi empat kelompok supaya jebakannya terlihat sejak awal:

| Kelompok | Isi |
|:---------|:----|
| Mirip Latin, bunyi sama | А К М О Т |
| **Mirip Latin, bunyi berbeda** | В Е Н Р С У Х И Я |
| Bentuk baru | Б Г Д Ж З Й Л П Ф Ц Ч Ш Щ Ы Э Ю Ё |
| Tanda, bukan bunyi | Ь Ъ |

Kelompok kedua adalah sumber kesalahan baca terbesar bagi pemula, karena mata
membaca huruf Latin lebih dulu. Karena itu, kelompok tersebut diperkenalkan paling awal bersama kelompok
pertama, bukan ditunda.

Setiap huruf memuat nama hurufnya dalam bahasa Rusia, bunyinya beserta
padanan Bahasa Indonesia, alih hurufnya, satu kata contoh, dan catatan
jebakannya.

### Modul 2 — Kosakata inti (`data/vocab.json`)

209 entri dalam 6 tahap: kata ganti, salam, kata tanya, angka 0-10, keluarga,
orang, benda sehari-hari, makanan, tempat, waktu beserta nama hari, kata kerja,
kata sifat, dan kata tugas.

Setiap entri memuat: kata bertanda tekanan, arti Indonesia, kelas kata, gender
(untuk kata benda), bentuk jamak bila lazim, aspek dan pasangannya (untuk kata
kerja), konjugasi kala kini bentuk я/ты/он, bentuk feminin-netral-jamak (untuk
kata sifat), akar kata bila ada, satu contoh kalimat pendek bertanda tekanan
penuh, dan catatan pemakaian.

### Modul 3 — Tata bahasa dasar (`data/grammar.json`)

| Topik | Isi |
|:------|:----|
| g01 | Kalimat tanpa 'adalah' dan tanpa kata sandang |
| g02 | Gender kata benda: maskulin, feminin, netral |
| g03 | Kata ganti orang dan kepemilikan |
| g04 | Bentuk jamak nominatif |
| g05 | Kala kini: konjugasi pertama (-ать) |
| g06 | Kala kini: konjugasi kedua (-ить) dan kata kerja tak beraturan |
| g07 | Kasus akusatif: objek langsung |
| g08 | Kasus prepositional: menyatakan tempat |
| g09 | Kasus genitif: kepemilikan, penolakan, dan jumlah |
| g10 | Kasus datif: kepada siapa |
| g11 | Kasus instrumental: dengan apa, dengan siapa |
| g12 | Kala lampau |
| g13 | Aspek: imperfektif dan perfektif |
| g14 | Kata sifat dan adverbia |

Setiap topik memiliki field `caveats` yang memuat pengecualian dan batas
berlakunya aturan. Hal-hal itu sengaja ditulis sebagai catatan, bukan sebagai
aturan mutlak.

### Modul 4 — Akar kata dan afiks (`data/roots.json`)

14 keluarga akar (работ-, говор-, пис-, чит-, уч-, ход-, дом-, друг-, зна-,
жи-, вид-, люб-, стро-, врем-) dan 12 afiks: akhiran -тель, -ник, -ство,
-ение/-ание, -ость, -ка, -ый/-ий/-ой, -ся; awalan в-/вы-, при-/у-, по-, пере-.

Soal "apa akar kata ini" dan "mana yang bukan sekeluarga" **dibuat otomatis**
dari data keluarga akar, sehingga kuncinya tidak mungkin menyimpang dari
sumbernya.

Akar bahasa Rusia sering berubah bunyi (пис- menjadi пиш-, друг- menjadi друж-
dan друз-). Perubahan itu dicatat sebagai `variants`, dan pengujian otomatis
menolak varian yang tidak dipakai dan tidak pula dijelaskan di catatannya.

### Modul 5 — Tekanan dan pelafalan (`data/reading.json`)

Keterampilan penghubung menuju teks Rusia sehari-hari, yang memang **tidak
pernah** memakai tanda tekanan.

| Level | Tampilan |
|:------|:---------|
| 1 | Tanda tekanan penuh |
| 2 | Kata lain tetap bertanda; hanya kata yang ditanyakan dilepas tandanya |
| 3 | Tanpa tanda tekanan sama sekali |

Jenis latihan: menentukan letak tekanan dari konteks (за́мок 'kastil' lawan
замо́к 'kunci gembok'; мука́ 'tepung' lawan му́ка 'siksaan'; окна́ sesudah angka
lawan о́кна bentuk jamak), memilih arti kalimat tanpa tanda tekanan, menjawab
soal pelafalan yang menyimpang dari tulisannya (что, сего́дня, коне́чно,
по́здно, -ться), serta membaca teks pendek lalu mencocokkannya sendiri.

Semua pilihan pada soal "di mana letak tekanan" tersusun dari **huruf yang
sama persis**, sehingga soal tidak bisa dijawab dari bentuk tulisannya. Hal ini
diuji otomatis.

### Modul 6 — Teman palsu dan serapan (`data/falsefriends.json`)

Catatan pendek, bukan latihan utama. Memuat 18 kata yang terdengar akrab bagi
penutur Bahasa Indonesia tetapi artinya berbeda: магази́н (toko, bukan
majalah), фами́лия (nama keluarga, bukan keluarga), студе́нт (mahasiswa, bukan
siswa sekolah), маши́на (mobil), ба́нка (kaleng, bukan bank), симпати́чный
(manis dilihat, bukan baik hati), dan seterusnya.

Modul ini juga menegaskan satu hal: **sebagian besar kosakata Rusia tidak
menjebak** justru karena tidak ada hubungannya dengan Bahasa Indonesia. Daftar
di atas adalah pengecualian, dan banyak kata serapan (телефо́н, банк, парк,
метро́, апте́ка) justru mempermudah.

## Cara kerja penjadwalan

Lima kotak Leitner. Jawaban benar menaikkan kartu satu kotak, jawaban salah
mengembalikannya ke kotak 1.

| Kotak | Jeda sebelum diulang |
|------:|---------------------:|
| 1 | hari itu juga |
| 2 | 1 hari |
| 3 | 3 hari |
| 4 | 7 hari |
| 5 | 16 hari |

Angka-angka itu adalah pilihan praktis yang lazim dipakai pada kartu Leitner,
**bukan hasil pengukuran**. Ubah `INTERVALS` di `rusdrill/leitner.py` bila
jadwal lain lebih cocok (dan `BOX_DAYS` di `app.js` agar keduanya sejalan).

Empat hal lain yang diterapkan penjadwal:

- **Ulangan didahulukan.** Selama masih ada kartu jatuh tempo, materi baru
  dibatasi paling banyak 45% dari satu sesi. Tanpa pembatasan ini, materi baru
  akan memakan seluruh sesi dan kartu lama tidak pernah naik kotak.
- **Interleaving.** Soal dari mode berbeda disilang bergantian, dan materi lama
  disisipkan di antara materi baru kira-kira 2 lama : 1 baru. Mencampur materi
  umumnya menghasilkan ingatan yang lebih tahan lama daripada mengerjakan satu
  blok materi sejenis berturut-turut, meski terasa lebih sulit saat dikerjakan.
- **Materi baru masuk menurut urutan tahap**, bukan acak dari seluruh materi,
  walaupun `--stage` tidak diberikan.
- **Lintasan kedua.** Pada hari-hari awal, ketika belum ada kartu jatuh tempo,
  kartu baru diulang sekali lagi di akhir sesi. Pengulangan itu tidak menaikkan
  kotak Leitner dua kali.

## Jadwal 10 pekan

Dengan pengaturan bawaan (20 menit per sesi, 8 kartu baru, 5 sesi per pekan),
penjadwal memperkenalkan **kira-kira 15 kata baru per pekan**, ditambah huruf,
soal tata bahasa, akar kata, dan latihan membaca.

| Pekan | Huruf | Kosakata | Tata bahasa | Akar | Baca |
|------:|------:|---------:|------------:|-----:|-----:|
| 1 | 10 | 15 | 5 | 10 | 5 |
| 2 | 20 | 30 | 10 | 20 | 10 |
| 3 | 30 | 45 | 14 | 30 | 15 |
| 4 | 40 | 60 | 19 | 40 | 20 |
| 5 | 45 | 75 | 23 | 49 | 25 |
| 6 | 45 | 90 | 26 | 54 | 30 |
| 7 | 45 | 105 | 31 | 59 | 35 |
| 8 | 45 | 120 | 36 | 59 | 35 |
| 9 | 45 | 135 | 41 | 59 | 35 |
| 10 | 45 | 150 | 45 | 59 | 35 |

Angka kolom adalah jumlah KUMULATIF kartu yang sudah diperkenalkan.

Pada akhir pekan ke-5 seluruh alfabet sudah diperkenalkan, dan pada akhir pekan
ke-7 seluruh keluarga akar serta seluruh latihan membaca sudah masuk. Kosakata
mencapai 150 dari 209 kata pada pekan ke-10; menyelesaikan seluruhnya pada
kecepatan yang sama memerlukan kira-kira **14 pekan**.

Bila ingin lebih cepat, naikkan `--new` ke 12-14 — tetapi beban ulangannya ikut
naik dan sesi 20 menit menjadi tidak cukup.

### Dari mana angka-angka itu

Angka di tabel berasal dari **simulasi penjadwal**, bukan dari pengamatan
pembelajar nyata: 50 sesi berurutan, 5 sesi per pekan, dengan asumsi ketepatan
jawaban 85%. Pada simulasi itu, tunggakan soal jatuh tempo memuncak di sekitar
**92 soal**. Dengan ketepatan 95%, puncaknya sekitar **36 soal**.

Kecepatan setiap orang berbeda, dan tidak ada yang menjamin angka ini berlaku
untuk Anda.

### Bila tunggakan menumpuk

Bila `--stats` menunjukkan kartu jatuh tempo jauh lebih banyak daripada yang
bisa Anda kerjakan:

```bash
python quiz.py --new 0            # satu sesi khusus mengulang, tanpa materi baru
python quiz.py --new 4            # perlambat laju materi baru
python quiz.py --minutes 30       # sesi lebih panjang
```

Memperlambat materi baru lebih baik daripada menumpuk kartu yang tidak pernah
diulang.

## Lembar kerja

12 lembar kerja Markdown di `worksheets/`, dua lembar per tahap, dengan kunci
jawaban **terpisah** di `worksheets/answers/`. Setiap lembar memuat enam
bagian: huruf, arti kata, menulis kata Rusia, tata bahasa, akar kata, dan
tekanan.

Lembar kerja dibuat dari data oleh skrip, bukan ditulis tangan, sehingga
kuncinya selalu sejalan dengan datanya. Jangan menyuntingnya langsung.

```bash
python tools/build_worksheets.py
```

## Anki

Ekspor CSV untuk Anki ada di `anki/`, beserta pemetaan kolom ke field di
`anki/README.md`.

```bash
python tools/build_exports.py
```

Catatan: bila Anda memakai Anki, pakailah penjadwalan Anki dan jangan
menjalankan `quiz.py` untuk materi yang sama. `progress.json` dan koleksi Anki
tidak saling tahu, sehingga satu kartu akan dijadwalkan oleh dua sistem
sekaligus.

## Pengujian

```bash
python -m pytest
```

232 pengujian. Yang diperiksa:

| Berkas | Isi |
|:-------|:----|
| `test_schema.py` | Id unik di seluruh modul, format id, tidak ada field kosong, nilai kelas kata dan gender sah, kata benda bergender, kata kerja memiliki aspek dan konjugasi, kata sifat memiliki bentuk f/n/pl, alfabet berisi tepat 33 huruf dan 10 vokal, setiap tahap dan setiap level terisi, pasangan aspek saling menunjuk. |
| `test_cyrillic.py` | Hanya karakter Kiril yang diizinkan, bentuk NFC, aturan tanda tekanan (bersuku banyak wajib satu tanda, bersuku satu tanpa tanda, kata ber-ё tanpa tanda), akar tanpa tanda tekanan, kasus pelafalan yang dipatok, contoh kalimat diakhiri tanda baca. |
| `test_translit.py` | Kasus alih huruf yang dipatok, е beriota di awal kata dan sesudah konsonan, tidak ada huruf Kiril yang tertinggal, alih huruf nama huruf sejalan dengan data. |
| `test_roots.py` | Huruf akar muncul berurutan pada kata turunannya, varian akar terbukti dipakai atau dijelaskan, keluarga bervarian wajib bercatatan, satu kata tidak diklaim dua keluarga, akar di `vocab.json` sejalan dengan `roots.json`. |
| `test_keys.py` | Setiap soal memiliki tepat satu jawaban benar, tidak ada pilihan ganda identik, semua pilihan soal tekanan berhuruf sama, kunci sama dengan kata pada kalimatnya, pengecoh kosakata tidak ikut benar, pengecoh soal buatan otomatis benar-benar asing, jawaban tidak bocor di sisi soal. |
| `test_leitner.py` | Kenaikan dan penurunan kotak, jeda sesuai tabel, jatuh tempo, simpan dan muat ulang, berkas rusak tidak merusak pemuatan, nilai aneh diabaikan, penulisan atomik. |
| `test_session.py` | Batas kartu baru, ulangan tidak tergeser habis oleh materi baru, kartu belum jatuh tempo tidak muncul, interleaving mencampur mode, satu kata dilatih dua arah, materi baru masuk menurut urutan tahap, sesi dapat diulang dengan seed sama. |
| `test_exports.py` | Semua hasil ekspor mutakhir terhadap data (CSV, Anki, lembar kerja, dan `webdata.js`), kolom kunci sesuai, format Anki benar, `webdata.js` hanya ASCII, kunci soal di `webdata.js` sama dengan di `data/`, dan aplikasi web tidak memakai `fetch()` sehingga tetap jalan di `file://`. |
| `test_worksheets.py` | Kunci berada di berkas terpisah, semua bagian ada, soal tekanan disajikan tanpa tanda sedangkan kuncinya bertanda penuh, setiap butir berasal dari data, lembar awal tidak memuat materi tahap lanjut. |

### Apa yang TIDAK bisa diuji mesin

Pengujian di atas memeriksa **bentuk**, bukan **kebenaran isi bahasa**. Yang
tidak diperiksa mesin:

- Apakah letak tekanan sebuah kata sudah benar. Mesin hanya memastikan bahwa
  setiap kata bersuku banyak memiliki tepat satu tanda — bukan bahwa tandanya
  ada di suku kata yang tepat.
- Apakah arti Bahasa Indonesia sudah tepat dan wajar.
- Apakah gender, bentuk jamak, aspek, dan konjugasi sudah benar.
- Apakah akar yang dicantumkan memang akar kata itu. Pengujian hanya memeriksa
  bahwa huruf-hurufnya muncul berurutan pada kata — akar keliru yang kebetulan
  hurufnya cocok akan tetap lolos.
- Apakah contoh kalimat benar secara tata bahasa dan terdengar wajar bagi
  penutur.
- Apakah penjelasan tata bahasa tidak menyederhanakan secara menyesatkan.
- Apakah pendekatan lafal sudah cukup dekat dengan ucapan penutur asli.

**Periksalah isinya dengan kamus rujukan atau dengan pengajar** sebelum
menghafalkannya. Hal-hal yang belum diyakini sepenuhnya didaftar di
`data/NEEDS_REVIEW.md`.

## Menyunting data

`data/*.json` adalah **satu-satunya sumber data**. Berkas di `data/csv/`,
`anki/`, `worksheets/`, dan `webdata.js` adalah turunan yang dibuat ulang oleh
skrip.

```bash
# 1. sunting data/vocab.json (atau modul lain)
python -m pytest                      # 2. pastikan data masih sah
python tools/build_exports.py         # 3. buat ulang CSV dan Anki
python tools/build_worksheets.py      # 4. buat ulang lembar kerja
python tools/build_web.py             # 5. buat ulang data aplikasi web
python -m pytest                      # 6. pastikan semua hasil mutakhir
```

Pengujian `test_exports.py` akan gagal bila data sudah berubah tetapi
ekspornya belum dibuat ulang.

### Aturan penulisan tanda tekanan

Tanda tekanan ditulis sebagai U+0301 (combining acute) tepat **sesudah** huruf
vokalnya: `о` + U+0301 menjadi о́. Validator di `rusdrill/cyrillic.py`
menegakkan tiga aturan:

| Aturan | Alasan |
|:-------|:-------|
| Kata yang bervokal lebih dari satu wajib memuat tepat satu tanda | Itulah yang dilatih; tanpa tanda, datanya tidak bisa dipakai menilai jawaban. |
| Kata yang bervokal tunggal tidak diberi tanda | Tandanya mubazir: hanya ada satu tempat untuk tekanan. |
| Kata yang memuat ё tidak diberi tanda | Huruf ё selalu bertekanan dengan sendirinya. |

Pengecualian yang diketahui: pada beberapa kata majemuk, ё tidak bertekanan
(трёхэта́жный). Tidak ada kata semacam itu di data, dan validator akan
menolaknya bila ditambahkan.

Validator **tidak** menjangkau field prosa (`explanation`, `caveats`, `note`,
`explain`), dan memang seharusnya begitu. Field itu sengaja memuat potongan
akhiran (`-ый`, `-ая`, `-тся`) dan contoh bentuk yang sengaja **salah** untuk
diperbandingkan, misalnya `любю́` pada topik g06. Isi field prosa karena itu
perlu ditinjau manusia.

Teks yang memang ditulis tanpa tanda tekanan — papan nama seperti `ВЫХОД` dan
`РЕСТОРАН` — ditandai `"stress_marked": false` sehingga validator hanya
memeriksa karakternya.

## Struktur folder

```
index.html            aplikasi kartu di browser (siap untuk GitHub Pages)
style.css             tiga tema: bumaga, noch, samovar
app.js                kartu, saringan, Leitner di localStorage
webdata.js            data aplikasi web (dibuat ulang)
.nojekyll             agar GitHub Pages tidak memproses berkas lewat Jekyll
data/                 sumber data JSON + NEEDS_REVIEW.md
  csv/                ekspor CSV (dibuat ulang)
rusdrill/             paket inti
  cyrillic.py         normalisasi, tanda tekanan, silabel, pendekatan lafal
  translit.py         alih huruf Latin opsional
  leitner.py          lima kotak + jadwal + berkas progres
  dataio.py           pemuat data
  questions.py        pembuat soal per mode
  session.py          penyusun sesi (jatuh tempo, materi baru, interleaving)
quiz.py               antarmuka baris perintah
tools/                build_exports.py, build_worksheets.py, build_web.py
anki/                 ekspor Anki (dibuat ulang) + pemetaan field
worksheets/           lembar kerja (dibuat ulang)
  answers/            kunci jawaban
tests/                pengujian otomatis
progress.json         progres Anda (dibuat saat latihan pertama)
```

## Catatan keterbatasan

- Materi ini disusun oleh model bahasa dan diperiksa secara otomatis hanya pada
  hal-hal yang bisa diperiksa mesin. Isi bahasanya belum ditinjau penutur asli
  atau pengajar.
- Tingkat A1-A2 berarti kalimat pendek dan kosakata sehari-hari. Membaca surat
  kabar Rusia dengan lancar memerlukan kosakata yang jauh lebih banyak daripada
  yang ada di sini.
- Keenam kasus diperkenalkan lewat fungsinya dan akhiran yang paling lazim.
  Deklinasi lengkap, kata sifat dalam semua kasus, dan kata kerja gerak
  berawalan memerlukan bahan lanjutan.
- Modul membaca melatih penentuan tekanan pada kalimat pendek yang kosakatanya
  sudah Anda kenal. Teks nyata lebih sulit karena memuat kata yang belum
  dikenal.
