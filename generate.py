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

    # Pisahkan front matter dan isi markdown
    if content.startswith('---'):
        parts = content.split('---')
        metadata_raw = parts[1] if len(parts) >= 3 else ''
        body_md = '---'.join(parts[2:]) if len(parts) >= 3 else content
    else:
        metadata_raw, body_md = '', content

    # Parsing metadata
    metadata = {}
    for line in metadata_raw.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip().strip('"')

    # Ambil data metadata
    title = metadata.get('title', 'Judul Tidak Ditemukan')
    image = metadata.get('image', '')
    apply_url = metadata.get('apply_url', '')
    date_str = metadata.get('date', '')
    company = metadata.get('company', '')
    location = metadata.get('location', '')
    employment_type = metadata.get('employment_type', 'FULL_TIME')
    salary_raw = metadata.get('salary', '')

    # Format gaji
    salary_cleaned = ''
    if salary_raw:
        salary_cleaned = salary_raw.replace('Rp', '').replace('.', '').split('-')[0].strip()

    # Konversi Markdown ke HTML
    body_html = markdown.markdown(body_md)

    # Format tanggal
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d-%m-%Y')
    except Exception:
        date_obj = datetime.min
        formatted_date = 'Tanggal Tidak Valid'

    filename = os.path.splitext(os.path.basename(md_file))[0] + '.html'

    # Schema.org
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

    # HTML halaman lowongan
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
  <!--#include virtual="header.html" -->
  <!--#include virtual="navbar.html" -->

  <main class="job-posting">
    <h1 class="job-title">{title}</h1>
    {f'<img src="{image_folder}/{image}" alt="Flyer Lowongan" class="job-image">' if image else ''}
    <div class="markdown-content">
      {body_html}
    </div>
    {f'<div class="apply-button"><a href="{apply_url}" target="_blank">LAMAR SEKARANG</a></div>' if apply_url else ''}
  </main>

  <!--#include virtual="footer.html" -->
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
        'formatted_date': formatted_date,
        'company': company,
        'location': location
    })

# Urutkan dari terbaru
lowongan_data.sort(key=lambda x: x['date_obj'], reverse=True)

# Bangun kartu lowongan
cards_html = ''
for data in lowongan_data:
    cards_html += f"""
    <div class="card">
      <a href="{data['filename']}" class="card-link">
        {f'<img src="{image_folder}/{data["image"]}" alt="Flyer" class="card-image">' if data["image"] else ''}
        <h2 class="card-title">{data['title']}</h2>
        <p class="card-date">{data['formatted_date']}</p>
        {f"<p class='card-company'>{data['company']}</p>" if data['company'] else ''}
        {f"<p class='card-location'>{data['location']}</p>" if data['location'] else ''}
      </a>
    </div>
    """

# Sisipkan ke index.html
with open('template_index.html', 'r', encoding='utf-8') as f:
    index_template = f.read()

if '<!-- GENERATED_CARDS -->' in index_template:
    new_index = index_template.replace(
        '<!-- GENERATED_CARDS -->',
        '<!-- GENERATED_CARDS -->\n' + cards_html.strip()
    )
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_index)
    print("✅ index.html berhasil diperbarui (dengan urutan terbaru).")
else:
    print("❌ Placeholder <!-- GENERATED_CARDS --> tidak ditemukan di template_index.html.")
