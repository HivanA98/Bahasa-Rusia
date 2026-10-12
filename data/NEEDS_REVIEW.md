# Yang perlu ditinjau manusia

Berkas ini mendaftar hal-hal di dalam `data/` yang **tidak bisa dipastikan
mesin** dan sebaiknya diperiksa dengan kamus rujukan atau pengajar sebelum
dihafalkan. Pengujian otomatis hanya memeriksa bentuk penulisan, bukan
kebenaran isi bahasa.

Rujukan yang lazim dipakai: kamus Ozhegov atau Ushakov untuk makna, kamus
tekanan (слова́рь ударе́ний) untuk letak tekanan, dan Gramota.ru untuk pemakaian
kini.

## 1. Letak tekanan

Mesin hanya memastikan bahwa setiap kata bersuku banyak memiliki **tepat
satu** tanda tekanan. Mesin tidak tahu apakah tanda itu berada di suku kata
yang benar.

Yang paling perlu diperiksa:

- Perpindahan tekanan pada bentuk jamak: `дом` → `дома́`, `го́род` → `города́`,
  `окно́` → `о́кна`, `сестра́` → `сёстры`, `семья́` → `се́мьи`, `страна́` →
  `стра́ны`, `среда́` → `сре́ды`.
- Perpindahan tekanan pada konjugasi: `писа́ть` → `пишу́`, `пи́шешь`;
  `смотре́ть` → `смотрю́`, `смо́тришь`; `люби́ть` → `люблю́`, `лю́бишь`;
  `учи́ть` → `учу́`, `у́чишь`.
- Pasangan yang hanya dibedakan tekanan di `reading.json`: `за́мок`/`замо́к`,
  `му́ка`/`мука́`, `доро́га`/`дорога́`, `у́же`/`уже́`, `по́том`/`пото́м`,
  `сто́ит`/`стои́т`, `о́кна`/`окна́`, `го́рода`/`города́`, `пла́чу`/`плачу́`.
- Kata panjang: `университе́т`, `Индоне́зия`, `воскресе́нье`, `пожа́луйста`,
  `здра́вствуйте`.

## 2. Gender, jamak, dan bentuk tak beraturan

- Kata benda berakhiran `ь`: `дверь` (f), `ночь` (f), `крова́ть` (f),
  `день` (m). Gendernya harus dihafal dan di sini ditulis manual.
- Kata maskulin berakhiran `-а`: `па́па`, `де́душка`, `мужчи́на`.
- Jamak tak beraturan: `брат` → `бра́тья`, `сын` → `сыновья́`,
  `друг` → `друзья́`, `ребёнок` → `де́ти`, `челове́к` → `лю́ди`,
  `стул` → `сту́лья`, `учи́тель` → `учителя́`.
- Kata yang hanya berbentuk jamak: `часы́`, `де́ньги` (ditandai `pluralonly`,
  tanpa gender).
- `ко́фе`: ditulis maskulin sesuai norma baku. Pemakaian netral dalam
  percakapan sudah diterima sebagian kamus; silakan sesuaikan bila tidak
  setuju dengan pilihan ini.

## 3. Aspek dan konjugasi kata kerja

Seluruh pasangan aspek dan bentuk konjugasi `я/ты/он` ditulis manual dan
perlu diperiksa, terutama:

- `мочь` → `могу́`, `мо́жешь` (pergantian г/ж)
- `хоте́ть` → `хочу́`, `хо́чешь`, lalu `хоти́м`, `хотя́т` (campuran dua konjugasi)
- `есть` → `ем`, `ешь`, `ест` (tak beraturan)
- `пить` → `пью`, `пьёшь`
- `дава́ть`, `ждать`, `спать`, `идти́`, `е́хать`
- Pasangan yang bentuknya jauh berbeda: `говори́ть`/`сказа́ть`,
  `покупа́ть`/`купи́ть`, `понима́ть`/`поня́ть`, `помога́ть`/`помо́чь`

## 4. Akar kata

Pengujian hanya memeriksa bahwa huruf akar muncul berurutan pada kata
turunannya. Hubungan etimologisnya tidak diperiksa. Yang perlu ditinjau:

- `понима́ть` diberi akar `ним`; pemenggalan akar kata ini diperdebatkan
  (sebagian analisis memakai `я`/`ним` dengan awalan `по-`).
- `помога́ть` diberi akar `мог`, sama dengan `мочь`.
- `ру́чка` diturunkan dari `рука́` dengan pergantian к menjadi ч.
- `вокза́л` di modul teman palsu: asal-usul dari nama Vauxhall adalah
  penjelasan yang paling sering disebut, bukan kepastian.

## 5. Penjelasan tata bahasa

Seluruh field `explanation` dan `caveats` adalah penyederhanaan. Yang paling
mungkin menyesatkan bila dibaca tanpa guru:

- g07: aturan "maskulin bernyawa memakai bentuk genitif" disampaikan tanpa
  tabel deklinasi lengkap.
- g09: genitif jamak hanya disinggung; pola pembentukannya jauh lebih rumit
  daripada yang ditulis.
- g13: pemilihan aspek disebut sebagai "pilihan makna". Itu benar, tetapi
  penutur asli memakai kaidah kebiasaan yang tidak dijelaskan di sini.
- g08: daftar kata yang memakai `на` dan bukan `в` tidak lengkap.

## 6. Pendekatan lafal

Fungsi `pronounce()` di `rusdrill/cyrillic.py` adalah pendekatan mekanis.
Yang sengaja TIDAK ditangani:

- Kelunakan konsonan secara halus (hanya ditandai apostrof dan huruf y).
- Reduksi vokal tingkat kedua (`о` jauh sebelum tekanan menjadi bunyi yang
  lebih lemah daripada `a` biasa).
- Pembagian suku kata pada gugus konsonan, yang masih diperdebatkan ahli
  fonetik.
- Intonasi kalimat, yang justru penting untuk membedakan pertanyaan dan
  pernyataan dalam bahasa Rusia.

Daftar kekecualian leksikal (`LEXICAL`) hanya memuat kata yang ada di data
ini. Kata lain yang berpola serupa akan dilafalkan apa adanya, huruf per
huruf.

## 7. Terjemahan Bahasa Indonesia

Beberapa pilihan terjemahan patut didiskusikan:

- `брат` dan `сестра́` diterjemahkan tanpa membedakan kakak dan adik, karena
  bahasa Rusia memang tidak membedakannya.
- `мы` diterjemahkan "kami" sekaligus "kita".
- `норма́льно` diterjemahkan "baik-baik saja", bukan "normal".
- `де́вушка` diterjemahkan "perempuan muda", padahal pemakaiannya sebagai
  panggilan kepada pelayan sulit dipadankan.
