import os
import markdown
from datetime import datetime

# Fungsi untuk membaca komponen HTML terpisah
def load_partial(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# Fungsi untuk mengubah markdown ke HTML
def konversi_markdown(file_md):
    with open(file_md, "r", encoding="utf-8") as f:
        lines = f.readlines()

    judul = lines[0].strip().replace("#", "").strip()
    tanggal = lines[1].strip().replace("_", "").strip()
    gambar = lines[2].strip()
    apply_url = ""
    isi_markdown = ""

    for line in lines[3:]:
        if line.startswith("LAMAR:"):
            apply_url = line.replace("LAMAR:", "").strip()
        else:
            isi_markdown += line

    html_content = markdown.markdown(isi_markdown, extensions=["extra"])
    return judul, tanggal, gambar, apply_url, html_content

# Fungsi untuk menyusun HTML final dari template
def buat_html(judul, tanggal, gambar, apply_url, isi, template):
    header = load_partial("header.html")
    navbar = load_partial("navbar.html")
    footer = load_partial("footer.html")

    html = template.replace("{{ title }}", judul)
    html = html.replace("{{ date }}", tanggal)
    html = html.replace("{{ image }}", gambar)
    html = html.replace("{{ content }}", isi)
    html = html.replace("{{ header }}", header)
    html = html.replace("{{ navbar }}", navbar)
    html = html.replace("{{ footer }}", footer)

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

# Main: proses semua file di folder /lowongan
def proses_semua():
    folder = "lowongan"
    template_file = "template.html"

    if not os.path.exists(template_file):
        print("File template.html tidak ditemukan.")
        return

    with open(template_file, "r", encoding="utf-8") as f:
        template = f.read()

    for filename in os.listdir(folder):
        if filename.endswith(".md"):
            path_md = os.path.join(folder, filename)
            judul, tanggal, gambar, apply_url, isi = konversi_markdown(path_md)

            nama_html = filename.replace(".md", ".html")
            path_html = os.path.join(".", nama_html)

            html = buat_html(judul, tanggal, gambar, apply_url, isi, template)

            with open(path_html, "w", encoding="utf-8") as out:
                out.write(html)
            print(f"✅ Dibuat: {nama_html}")

if __name__ == "__main__":
    proses_semua()
