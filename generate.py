import os
import re

LOWONGAN_FOLDER = "lowongan"
OUTPUT_FOLDER = "."
TEMPLATE_FILE = "template.html"

def baca_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return f.read()

def parse_front_matter(md_text):
    front_matter = {}
    content = md_text
    if md_text.startswith('---'):
        parts = md_text.split('---', 2)
        if len(parts) >= 3:
            _, meta, content = parts
            lines = meta.strip().splitlines()
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    front_matter[key.strip()] = value.strip().strip('"')
    return front_matter, content.strip()

def konversi_md_ke_html(md_text):
    # Ganti markdown sederhana jadi HTML
    html = md_text.replace("\n", "<br>")
    html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html)
    html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', html)
    return html

def buat_html(template, title, image, content_html):
    return template.replace("{{ title }}", title)\
                   .replace("{{ image }}", image)\
                   .replace("{{ content }}", content_html)

def proses_file():
    template = baca_template()
    for nama_file in os.listdir(LOWONGAN_FOLDER):
        if nama_file.endswith(".md"):
            path_file = os.path.join(LOWONGAN_FOLDER, nama_file)
            with open(path_file, "r", encoding="utf-8") as f:
                md = f.read()

            meta, isi = parse_front_matter(md)
            title = meta.get("title", "Tanpa Judul")
            image = meta.get("image", "gambar/default.jpg")
            isi_html = konversi_md_ke_html(isi)

            html = buat_html(template, title, image, isi_html)

            nama_output = nama_file.replace(".md", ".html").replace(" ", "-").lower()
            path_output = os.path.join(OUTPUT_FOLDER, nama_output)
            with open(path_output, "w", encoding="utf-8") as f:
                f.write(html)

            print(f"✅ Dibuat: {nama_output}")

if __name__ == "__main__":
    proses_file()
