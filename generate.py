import os
import markdown
import yaml
from datetime import datetime

# Paths
lowongan_folder = "lowongan"
output_folder = "."
template_file = "template_index.html"
header_file = "header.html"
navbar_file = "navbar.html"
footer_file = "footer.html"

# Fungsi untuk menghasilkan kartu HTML
def buat_kartu_lowongan(data, filename):
    return f'''
    <a href="{filename}" class="card" data-title="{data.get('title', '').lower()}" data-company="{data.get('hiringOrganization', {}).get('name', '').lower()}" data-location="{data.get('jobLocation', {}).get('address', {}).get('addressLocality', '').lower()}">
        <img src="{data.get('image', '')}" alt="Flyer lowongan">
        <h2>{data.get('title', '')}</h2>
        <p>{data.get('hiringOrganization', {}).get('name', '')}</p>
        <p>{data.get('jobLocation', {}).get('address', {}).get('addressLocality', '')}</p>
    </a>
    '''

# Fungsi untuk membuat schema JSON-LD
def buat_schema_json_ld(data):
    schema = {
        "@context": "https://schema.org/",
        "@type": "JobPosting",
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "datePosted": data.get("datePosted", datetime.today().strftime('%Y-%m-%d')),
        "employmentType": data.get("employmentType", "FULL_TIME"),
        "hiringOrganization": {
            "@type": "Organization",
            "name": data.get("hiringOrganization", {}).get("name", ""),
            "sameAs": data.get("hiringOrganization", {}).get("sameAs", ""),
            "logo": data.get("hiringOrganization", {}).get("logo", "")
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": data.get("jobLocation", {}).get("address", {}).get("addressLocality", ""),
                "addressRegion": data.get("jobLocation", {}).get("address", {}).get("addressRegion", ""),
                "addressCountry": "ID"
            }
        }
    }
    return f'<script type="application/ld+json">\n{yaml.safe_dump(schema, default_flow_style=False, allow_unicode=True)}\n</script>'

semua_kartu = set()
html_kartu = ""

# Proses semua markdown
for filename in os.listdir(lowongan_folder):
    if filename.endswith(".md"):
        filepath = os.path.join(lowongan_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if content.startswith("---"):
            parts = content.split("---", 2)
            meta = yaml.safe_load(parts[1])
            isi_markdown = parts[2]
        else:
            print(f"❌ ERROR format YAML: {filename}")
            continue

        html_content = markdown.markdown(isi_markdown)
        schema_json_ld = buat_schema_json_ld(meta)

        # Baca template
        with open(header_file, "r", encoding="utf-8") as f: header_html = f.read()
        with open(navbar_file, "r", encoding="utf-8") as f: navbar_html = f.read()
        with open(footer_file, "r", encoding="utf-8") as f: footer_html = f.read()

        html_page = f'''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{meta.get("title", "")} - Loker Jawa Bali</title>
  <link rel="stylesheet" href="style.css">
  <link href="https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Coming+Soon&display=swap" rel="stylesheet">
  {schema_json_ld}
</head>
<body>
{header_html}
{navbar_html}
<main>
  <article class="job-post">
    <h1>{meta.get("title", "")}</h1>
    <img src="{meta.get("image", "")}" alt="Flyer lowongan">
    <div>{html_content}</div>
    {'<div class="center-button"><a href="' + meta.get("applyUrl", "") + '" class="apply-button">Lamar Sekarang</a></div>' if meta.get("applyUrl") else ''}
  </article>
</main>
{footer_html}
</body>
</html>
'''

        output_filename = filename.replace(".md", ".html")
        output_path = os.path.join(output_folder, output_filename)

        # Cek duplikat
        if os.path.exists(output_path):
            print(f"⚠️ Dilewati (sudah ada): {output_filename}")
        else:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_page)
            print(f"✅ Dibuat: {output_filename}")

        # Cek duplikat job_cards
        id_kartu = meta.get("title", "").strip().lower()
        if id_kartu in semua_kartu:
            print(f"⚠️ Duplikat judul ditemukan: {meta.get('title', '')}")
        else:
            semua_kartu.add(id_kartu)
            html_kartu += buat_kartu_lowongan(meta, output_filename)

# Buat index.html dari template
if os.path.exists(template_file):
    with open(template_file, "r", encoding="utf-8") as f:
        template_content = f.read()

    if "{{ job_cards }}" in template_content:
        index_html = template_content.replace("{{ job_cards }}", html_kartu)
        with open(os.path.join(output_folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(index_html)
        print("✅ index.html berhasil dibuat.")
    else:
        print("❌ Placeholder {{ job_cards }} tidak ditemukan.")
else:
    print("❌ File template_index.html tidak ditemukan.")
