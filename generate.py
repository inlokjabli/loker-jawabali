import os

LOWONGAN_FOLDER = "lowongan"
GAMBAR_FOLDER = "gambar"
OUTPUT_FOLDER = "."
TEMPLATE_FILE = "template.html"
INDEX_FILE = "index.html"

CARD_TEMPLATE = '''  <a href="{filename}" class="card-link">
    <div class="card">
      <img src="gambar/{image}" alt="{title}" />
      <div class="card-title">{title}</div>
    </div>
  </a>
'''

def baca_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return f.read()

def konversi_md_ke_html(markdown):
    lines = markdown.splitlines()
    title = ""
    date = ""
    image = ""
    content_lines = []
    in_metadata = True

    for line in lines:
        if in_metadata:
            if line.strip() == "---":
                continue
            elif line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("date:"):
                date = line.split(":", 1)[1].strip()
            elif line.startswith("image:"):
                image = line.split(":", 1)[1].strip()
            elif line.strip() == "":
                in_metadata = False
        else:
            content_lines.append(line)

    content = "\n".join(content_lines).strip().replace("\n", "<br>")
    return title, date, image, content

def buat_html(judul, tanggal, gambar, isi, template):
    html = template.replace("{{ title }}", judul)
    html = html.replace("{{ date }}", tanggal)
    html = html.replace("{{ image }}", gambar)
    html = html.replace("{{ content }}", isi)
    return html

def tambah_ke_index(nama_file, judul, gambar):
    if not os.path.exists(INDEX_FILE):
        print("❌ index.html tidak ditemukan.")
        return

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index_html = f.read()

    # Masukkan kartu sebelum </div> dari grid-container
    kartu = CARD_TEMPLATE.format(filename=nama_file, title=judul, image=gambar)
    index_html = index_html.replace("<!-- GENERATED_CARDS -->", kartu + "\n  <!-- GENERATED_CARDS -->")

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(index_html)

def proses_file():
    template = baca_template()

    for nama_file in os.listdir(LOWONGAN_FOLDER):
        if nama_file.endswith(".md"):
            path_file = os.path.join(LOWONGAN_FOLDER, nama_file)
            with open(path_file, "r", encoding="utf-8") as f:
                markdown = f.read()

            judul, tanggal, gambar, isi = konversi_md_ke_html(markdown)
            nama_html = nama_file.replace(".md", ".html").lower()
            html = buat_html(judul, tanggal, gambar, isi, template)

            # Simpan HTML
            with open(nama_html, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"✅ Dibuat: {nama_html}")

            # Tambahkan ke index.html
            tambah_ke_index(nama_html, judul, gambar)

if __name__ == "__main__":
    proses_file()
