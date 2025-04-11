import os
from datetime import date

BASE_URL = "https://loker-jawabali.netlify.app/"
LASTMOD = date.today().isoformat()

# Daftar file HTML yang akan dimasukkan ke sitemap
html_files = [
    "index.html",
    "about.html",
    "note.html",
    "privacy-policy.html"
]

# Tambahkan semua file HTML di folder root
html_files += [f for f in os.listdir(".") if f.endswith(".html") and f not in html_files]

# Buat sitemap.xml
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')

    for html_file in sorted(set(html_files)):
        url = BASE_URL + html_file
        f.write("  <url>\n")
        f.write(f"    <loc>{url}</loc>\n")
        f.write(f"    <lastmod>{LASTMOD}</lastmod>\n")
        f.write("  </url>\n")

    f.write('</urlset>\n')

print("✅ sitemap.xml berhasil dibuat.")
