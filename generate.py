import os
import glob
import markdown
from datetime import datetime

markdown_folder = 'lowongan'
image_folder = 'gambar'

md_files = glob.glob(f'{markdown_folder}/*.md')
lowongan_data = []

for md_file in md_files:
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

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

    metadata = {}
    for line in metadata_raw.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip().strip('"')

    title = metadata.get('title', 'Judul Tidak Ditemukan')
    image = metadata.get('image', '')
    apply_url = metadata.get('apply_url', '')
    date_str = metadata.get('date', '')
    company = metadata.get('company', 'Perusahaan Tidak Diketahui')
    location = metadata.get('location', '')
    employment_type = metadata.get('employment_type', 'FULL_TIME')
    salary_raw = metadata.get('salary', '')

    # Ambil hanya nilai awal salary (angka pertama)
    if salary_raw:
        salary_cleaned = salary_raw.replace('Rp', '').replace('.', '').split('-')[0].strip()
    else:
        salary_cleaned = ''

    filename = os.path.splitext(os.path.basename(md_file))[0] + '.html'

    body_html = markdown.markdown(body_md)

    # Format tanggal
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d-%m-%Y')
    except:
        date_obj = datetime.min
        formatted_date = 'Tanggal Tidak Valid'

    # Schema.org JobPosting
    jobposting_schema = f"""
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "JobPosting",
      "title": "{title}",
      "datePosted": "{date_str}",
      "description": "{body_html.replace('"', "'").replace('\n', ' ')}",
      {"\"image\": \"" + image_folder + "/" + image + "\"," if image else ""}
      "hiringOrganization": {{
        "@type": "Organization",
        "name": "{company}",
        "sameAs": "https://loker-jawabali.netlify.app/"
      }},
      "jobLocation": {{
        "@type": "Place",
        "address": {{
          "@type": "PostalAddress",
          "addressLocality": "{location}",
          "addressCountry": "ID"
        }}
      }},
      "employmentType": "{employment_type}",
      "applicantLocationRequirements": {{
        "@type": "Country",
        "name": "Indonesia"
      }},
      {"\"baseSalary\": {{\"@type\": \"MonetaryAmount\", \"currency\": \"IDR\", \"value\": {{\"@type\": \"QuantitativeValue\", \"value\": \"" + salary_cleaned + "\", \"unitText\": \"MONTH\"}}}}," if salary_cleaned else ""}
      "directApply": true
    }}
    </script>
    """ if date_str else ''

    # HTML Halaman Lowongan
    lowongan_html = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
  <link href="style.css" rel="stylesheet" />
  <link href="https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Coming+Soon&display=swap" rel="stylesheet">
  {jobposting_schema}
</head>
<body>
  <div class="site-header">Lowongan Kerja Jawa-Bali</div>

  <nav>
    <a href="index.html">Beranda</a>
    <a href="https://s.id/info_loker_jawabali" target="_blank">Temukan Kami</a>
  </nav>

  <main class="job-posting">
    <h1 class="job-title">{title}</h1>
    {f'<img src="{image_folder}/{image}" alt="Flyer Lowongan" class="job-image">' if image else ''}
    <div class="markdown-content">
      {body_html}
    </div>
    {f'<div class="apply-button"><a href="{apply_url}" target="_blank">LAMAR SEKARANG</a></div>' if apply_url else ''}
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

    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(lowongan_html)
        print(f"✅ File baru dibuat: {filename}")
    else:
        print(f"⚠️  File dilewati (sudah ada): {filename}")

    lowongan_data.append({
        'title': title,
        'image': image,
        'filename': filename,
        'date_obj': date_obj,
        'formatted_date': formatted_date
    })

# Urutkan dari yang terbaru
lowongan_data.sort(key=lambda x: x['date_obj'], reverse=True)

# Kartu HTML
cards_html = ''
for data in lowongan_data:
    cards_html += f"""
    <div class="card">
      <a href="{data['filename']}" class="card-link">
        {f'<img src="{image_folder}/{data["image"]}" alt="Flyer" class="card-image">' if data["image"] else ''}
        <h2 class="card-title">{data['title']}</h2>
        <p class="card-date">{data['formatted_date']}</p>
      </a>
    </div>
    """

# Update index.html
with open('template_index.html', 'r', encoding='utf-8') as f:
    index_template = f.read()

new_index = index_template.replace(
    '<!-- GENERATED_CARDS -->',
    '<!-- GENERATED_CARDS -->\n' + cards_html.strip()
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_index)

print("🏠 index.html berhasil diperbarui (dengan urutan terbaru).")
