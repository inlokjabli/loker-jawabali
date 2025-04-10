import os
import markdown
import re
from datetime import datetime

# Lokasi folder
folder_lowongan = "lowongan"
folder_output = "."
template_index = "template_index.html"
file_index_output = "index.html"

# Fungsi bantu: ambil metadata dari markdown
def extract_metadata(content):
    meta = {}
    match = re.search(r"---(.*?)---", content, re.DOTALL)
    if match:
        lines = match.group(1).strip().split("\n")
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta

# Load template index.html (asli dengan <!-- GENERATED_CARDS -->)
with open(template_index, "r", encoding="utf-8") as f:
    index_template = f.read()

cards_html = ""

# Proses semua file .md
for filename in os.listdir(folder_lowongan):
    if filename.endswith(".md"):
        path_md = os.path.join(folder_lowongan, filename)
        with open(path_md, "r", encoding="utf-8") as f:
            content = f.read()

        metadata = extract_metadata(content)
        html_body = markdown.markdown(content)

        slug = os.path.splitext(filename)[0]
        output_filename = f"{slug}.html"
        image = metadata.get("image", "")
        title = metadata.get("title", "Lowongan")
        apply_url = metadata.get("apply_url", "#")

        # Buat halaman lowongan HTML
        html_output = f"""<!DOCTYPE html>
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

  <main>
    <h1>{title}</h1>
    {"<img src='gambar/" + image + "' alt='" + title + "'>" if image else ""}
    <div class="markdown-content">
      {html_body}
    </div>
    {"<div class='apply-button'><a href='" + apply_url + "' target='_blank'>Lamar Sekarang</a></div>" if apply_url else ""}
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
        with open(os.path.join(folder_output, output_filename), "w", encoding="utf-8") as f:
            f.write(html_output)

        # Tambahkan ke index.html bagian card
        card_html = f"""
    <div class="card">
      <a href="{output_filename}">
        {"<img src='gambar/" + image + "' alt='" + title + "'>" if image else ""}
        <h3>{title}</h3>
      </a>
    </div>
"""
        cards_html += card_html

# Sisipkan semua cards ke template index
index_final = index_template.replace("<!-- GENERATED_CARDS -->", cards_html)

# Simpan sebagai index.html
with open(file_index_output, "w", encoding="utf-8") as f:
    f.write(index_final)

print("✅ Semua file HTML berhasil dibuat!")
