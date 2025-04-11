import os
import markdown
import re
from datetime import date

# --- Konfigurasi dasar
BASE_URL = "https://loker-jawabali.netlify.app/"
MD_FOLDER = "lowongan"
OUT_FOLDER = "."
TEMPLATE_FILE = "template_index.html"
SITEMAP_FILE = "sitemap.xml"
PARTIALS = {
    "header": "header.html",
    "navbar": "navbar.html",
    "footer": "footer.html"
}
today = date.today().isoformat()

# --- Fungsi ambil partial
def load_partial(name):
    try:
        with open(PARTIALS[name], "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# --- Fungsi konversi markdown jadi HTML
def convert_md_to_html(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    html = markdown.markdown(text, extensions=["fenced_code", "tables"])
    return html, text

# --- Fungsi render ke template HTML
def render_with_template(content_html):
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    return template.replace("{{header}}", load_partial("header")) \
                   .replace("{{navbar}}", load_partial("navbar")) \
                   .replace("{{footer}}", load_partial("footer")) \
                   .replace("{{content}}", content_html)

# --- Proses halaman individual
lowongan_data = []
generated_files = []

for filename in os.listdir(MD_FOLDER):
    if filename.endswith(".md"):
        slug = filename.replace(".md", "")
        html_filename = f"{slug}.html"
        html_path = os.path.join(OUT_FOLDER, html_filename)
        md_path = os.path.join(MD_FOLDER, filename)

        html, md_text = convert_md_to_html(md_path)

        # Ambil metadata dari markdown (judul, gambar, tanggal)
        title_match = re.search(r'# (.+)', md_text)
        img_match = re.search(r'!\[.*?\]\((.*?)\)', md_text)
        date_match = re.search(r'date: (.+)', md_text)

        title = title_match.group(1) if title_match else slug
        image = img_match.group(1) if img_match else "gambar/default.jpg"
        tanggal = date_match.group(1) if date_match else today

        # Simpan info untuk halaman index
        lowongan_data.append({
            "title": title,
            "slug": slug,
            "image": image,
            "date": tanggal
        })

        # Tulis halaman HTML individual
        if not os.path.exists(html_path) or os.path.getmtime(md_path) > os.path.getmtime(html_path):
            final_html = render_with_template(html)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(final_html)
            print(f"✅ {html_filename} berhasil dibuat.")
        else:
            print(f"⏭ {html_filename} dilewati (tidak ada perubahan).")

        generated_files.append(html_filename)

# --- Buat halaman index.html (daftar lowongan)
lowongan_data.sort(key=lambda x: x["date"], reverse=True)

index_html = '<section class="grid-container">\n'
for data in lowongan_data:
    index_html += f'''
    <a class="lowongan-card" href="{data["slug"]}.html">
        <img src="{data["image"]}" alt="{data["title"]}">
        <h2>{data["title"]}</h2>
        <p class="tanggal">{data["date"]}</p>
    </a>
    '''
index_html += '</section>'

# Tulis ke index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(render_with_template(index_html))

print("🏠 index.html berhasil diperbarui.")

# --- Buat sitemap.xml
static_pages = ["index.html", "about.html", "note.html", "privacy-policy.html"]
all_html_files = static_pages + generated_files

with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for html_file in sorted(set(all_html_files)):
        f.write("  <url>\n")
        f.write(f"    <loc>{BASE_URL}{html_file}</loc>\n")
        f.write(f"    <lastmod>{today}</lastmod>\n")
        f.write("  </url>\n")
    f.write('</urlset>\n')

print("🗺️  sitemap.xml berhasil diperbarui.")
