import os
import markdown
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

# --- Fungsi ambil partial (header, navbar, footer)
def load_partial(name):
    try:
        with open(PARTIALS[name], "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# --- Fungsi buat halaman HTML dari markdown
def convert_md_to_html(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    html = markdown.markdown(text, extensions=["fenced_code", "tables", "toc"])
    return html

# --- Fungsi masukkan HTML ke template
def render_with_template(content_html, title="Lowongan Kerja"):
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    return template.replace("{{header}}", load_partial("header")) \
                   .replace("{{navbar}}", load_partial("navbar")) \
                   .replace("{{footer}}", load_partial("footer")) \
                   .replace("{{content}}", content_html)

# --- Proses generate semua halaman
generated_files = []
for filename in os.listdir(MD_FOLDER):
    if filename.endswith(".md"):
        slug = filename.replace(".md", "")
        html_filename = f"{slug}.html"
        html_path = os.path.join(OUT_FOLDER, html_filename)
        md_path = os.path.join(MD_FOLDER, filename)

        if not os.path.exists(html_path) or os.path.getmtime(md_path) > os.path.getmtime(html_path):
            content_html = convert_md_to_html(md_path)
            final_html = render_with_template(content_html)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(final_html)
            print(f"✅ {html_filename} berhasil dibuat.")
        else:
            print(f"⏭ {html_filename} dilewati (tidak ada perubahan).")

        generated_files.append(html_filename)

# --- Buat sitemap.xml otomatis
static_pages = [
    "index.html", "about.html", "note.html", "privacy-policy.html"
]
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
