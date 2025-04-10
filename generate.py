import os
import glob
import markdown
from datetime import datetime

# Konfigurasi folder markdown dan gambar
markdown_folder = 'lowongan'
image_folder = 'gambar'

# Ambil semua file markdown
md_files = glob.glob(f'{markdown_folder}/*.md')

# List kartu untuk homepage
cards_html = ''

for md_file in md_files:
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pisahkan metadata dan isi markdown
    if content.startswith('---'):
        parts = content.split('---')
        if len(parts) >= 3:
            metadata_raw = parts[1]
            body_md = '---'.join(parts[2:])
        else:
            metadata_raw = ''
            body_md = content
    else:
        metadata_raw = ''
        body_md = content

    # Ambil metadata
    metadata = {}
    for line in metadata_raw.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip().strip('"')

    title = metadata.get('title', 'Judul Tidak Ditemukan')
    image = metadata.get('image', '')
    apply_url = metadata.get('apply_url', '')
    date = metadata.get('date', '')
    filename = os.path.splitext(os.path.basename(md_file))[0] + '.html'

    # Konversi isi markdown ke HTML
    body_html = markdown.markdown(body_md)

    # Buat HTML halaman lowongan
    lowongan_html = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
  <link href="style.css" rel="stylesheet" />
  <link href="https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Coming+Soon&display=swap" rel="stylesheet">
</head>
<body>
  <div class="site-header">Lowongan Kerja Jawa-Bali</div>

  <nav>
    <a href="index.html">Beranda</a>
    <a href="https://s.id/info_loker_jawabali" target="_blank">Temukan Kami</a>
  </nav>

  <main class="job-posting">
    <h1 class="job-title">{title}</h1>
    {f'<img src="gambar/{image}" alt="Flyer Lowongan" class="job-image">' if image else ''}
    {body_html}
    {f'<div class="apply-button"><a href="{apply_url}" target="_blank">Lamar Sekarang</a></div>' if apply_url else ''}
  </main>

  <footer>
    <div class="footer-links">
      <a href="privacy-policy.html">Privasi</a>
      <a href="note.html">Note</a>
      <a href="about.html">About</a>
    </div>
  </footer>
</body>
</html>
"""

    # Simpan halaman lowongan
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(lowongan_html)

    # Tambahkan kartu ke beranda
    cards_html += f"""
    <div class="job-card">
      <a href="{filename}">
        {f'<img src="gambar/{image}" alt="Flyer" class="card-image">' if image else ''}
        <h2 class="card-title">{title}</h2>
        <p class="card-date">{date}</p>
      </a>
    </div>
    """

# Bangun halaman index.html
with open('index.html', 'r', encoding='utf-8') as f:
    index_template = f.read()

new_index = index_template.replace(
    '<!-- GENERATED_CARDS -->',
    '<!-- GENERATED_CARDS -->\n' + cards_html.strip()
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_index)
