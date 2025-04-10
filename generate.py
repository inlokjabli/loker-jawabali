import os
import re
from datetime import datetime

LOWONGAN_FOLDER = "lowongan"
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
    apply_url = ""
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
                image = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("apply_url:"):
                apply_url = line.split(":", 1)[1].strip().strip('"')
            elif line.strip() == "":
                in_metadata = False
        else:
            content_lines.append(line)

    content_md = "\n".join(content_lines).strip()
    # Konversi markdown sederhana
    content_html = re.sub(r"^## ?(.*)", r"<h2 style='color:limegreen;'>\1</h2>", content_md, flags=re.MULTILINE)
    content_html = content_html.replace("\n", "<br>")

    return title, date, image, apply_url, content_html

def buat_html(judul, tanggal, gambar, apply_url, isi, template):
    html = template.replace("{{ title }}", judul)
    html = html.replace("{{ date }}", tanggal)
    html = html.replace("{{ image }}", gambar)
    html = html.replace("{{ content }}", isi)

    if apply_url:
        tombol = f'''
        <div style="text-align: center; margin-top: 30px;">
          <a href="{apply_url}" target="_blank" style="background-color: limegreen; color: black; padding: 12px 25px; border-radius: 6px; font-weight: bold; text-decoration: none;">Lamar Sekarang</a>
        </div>
        '''
    else:
        tombol = ""

    html = html.replace("{{ apply_button }}", tombol)
    return html

def proses_file():
    template = baca_template()
    postingan = []

    for nama_file in os.listdir(LOWONGAN_FOLDER):
        if nama_file.endswith(".md"):
            path_file = os.path.join(LOWONGAN_FOLDER, nama_file)
            with open(path_file, "r", encoding="utf-8") as f:
                markdown = f.read()

            judul, tanggal_str, gambar, apply_url, isi = konversi_md_ke_html(markdown)
            try:
                tanggal_obj = datetime.strptime(tanggal_str, "%Y-%m-%d")
            except ValueError:
                tanggal_obj = datetime.min

            nama_html = nama_file.replace(".md", ".html").lower()
            html = buat_html(judul, tanggal_str, gambar, apply_url, isi, template)

            # Simpan HTML
            with open(nama_html, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"✅ Dibuat: {nama_html}")

            postingan.append((tanggal_obj, nama_html, judul, gambar))

    # Urutkan berdasarkan tanggal, terbaru di atas
    postingan.sort(reverse=True)

    # Bangun ulang index.html
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            index_html = f.read()
        index_html = re.sub(r'(?s)<!-- GENERATED_CARDS -->.*?<!-- END_GENERATED_CARDS -->', '<!-- GENERATED_CARDS -->\n  <!-- END_GENERATED_CARDS -->', index_html)
    else:
        print("❌ index.html tidak ditemukan.")
        return

    kartu_html = "\n".join([CARD_TEMPLATE.format(filename=f, title=t, image=g) for _, f, t, g in postingan])
    index_html = index_html.replace("<!-- GENERATED_CARDS -->\n  <!-- END_GENERATED_CARDS -->", f"<!-- GENERATED_CARDS -->\n{kartu_html}\n  <!-- END_GENERATED_CARDS -->")

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(index_html)
    print("📄 index.html diperbarui!")

if __name__ == "__main__":
    proses_file()
