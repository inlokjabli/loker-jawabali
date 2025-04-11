import os
import glob
import markdown
from datetime import datetime

MARKDOWN_DIR = 'lowongan'
IMAGE_DIR = 'gambar'
TEMPLATE_INDEX = 'template_index.html'
OUTPUT_INDEX = 'index.html'

def read_markdown_files(folder):
    return glob.glob(f'{folder}/*.md')

def parse_front_matter(content):
    if content.startswith('---'):
        parts = content.split('---')
        metadata_raw = parts[1] if len(parts) >= 3 else ''
        body_md = '---'.join(parts[2:]) if len(parts) >= 3 else content
    else:
        metadata_raw, body_md = '', content
    metadata = {}
    for line in metadata_raw.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip().strip('"')
    return metadata, body_md

def format_salary(salary_raw):
    if not salary_raw:
        return ''
    return salary_raw.replace('Rp', '').replace('.', '').split('-')[0].strip()

def create_schema(metadata, body_html):
    salary_clean = format_salary(metadata.get('salary', ''))
    image_line = f"\"image\": \"{IMAGE_DIR}/{metadata['image']}\"," if metadata.get('image') else ''
    salary_line = (
        f"\"baseSalary\": {{\"@type\": \"MonetaryAmount\", \"currency\": \"IDR\", \"value\": {{\"@type\": \"QuantitativeValue\", \"value\": \"{salary_clean}\", \"unitText\": \"MONTH\"}}}},"
        if salary_clean else ''
    )

    return f"""
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "JobPosting",
      "title": "{metadata['title']}",
      "datePosted": "{metadata['date']}",
      "description": "{body_html.replace('"', "'").replace('\n', ' ')}",
      {image_line}
      "hiringOrganization": {{
        "@type": "Organization",
        "name": "{metadata['company']}",
        "sameAs": "https://loker-jawabali.netlify.app/"
      }},
      "jobLocation": {{
        "@type": "Place",
        "address": {{
          "@type": "PostalAddress",
          "addressLocality": "{metadata['location']}",
          "addressCountry": "ID"
        }}
      }},
      "employmentType": "{metadata.get('employment_type', 'FULL_TIME')}",
      "applicantLocationRequirements": {{
        "@type": "Country",
        "name": "Indonesia"
      }},
      {salary_line}
      "directApply": true
    }}
    </script>
    """ if metadata.get('date') else ''

def generate_job_page(filename, metadata, body_html, schema_html):
    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{metadata['title']}</title>
  <link href="style.css" rel="stylesheet" />
  <link href="https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Coming+Soon&display=swap" rel="stylesheet">
  {schema_html}
</head>
<body>
  <!--#include virtual="header.html" -->
  <!--#include virtual="navbar.html" -->

  <main class="job-posting">
    <h1 class="job-title">{metadata['title']}</h1>
    {f'<img src="{IMAGE_DIR}/{metadata["image"]}" alt="Flyer Lowongan" class="job-image">' if metadata.get('image') else ''}
    <div class="markdown-content">{body_html}</div>
    {f'<div class="apply-button"><a href="{metadata["apply_url"]}" target="_blank">LAMAR SEKARANG</a></div>' if metadata.get('apply_url') else ''}
  </main>

  <!--#include virtual="footer.html" -->
</body>
</html>
"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

def generate_cards(lowongan_data):
    cards_html = ''
    for data in lowongan_data:
        cards_html += f"""
        <div class="card"
          data-title="{data['title'].lower()}"
          data-location="{data['location'].lower()}"
          data-company="{data['company'].lower()}"
        >
          <a href="{data['filename']}" class="card-link">
            {f'<img src="{IMAGE_DIR}/{data["image"]}" alt="Flyer" class="card-image">' if data["image"] else ''}
            <h2 class="card-title">{data['title']}</h2>
            <p class="card-date">{data['formatted_date']}</p>
            {f"<p class='card-company'>{data['company']}</p>" if data['company'] else ''}
            {f"<p class='card-location'>{data['location']}</p>" if data['location'] else ''}
          </a>
        </div>
        """
    return cards_html

def build_index(cards_html):
    with open(TEMPLATE_INDEX, 'r', encoding='utf-8') as f:
        template = f.read()
    if '<!-- GENERATED_CARDS -->' not in template:
        print("❌ Placeholder <!-- GENERATED_CARDS --> tidak ditemukan.")
        return
    final_index = template.replace('<!-- GENERATED_CARDS -->', f'<!-- GENERATED_CARDS -->\n{cards_html.strip()}')
    with open(OUTPUT_INDEX, 'w', encoding='utf-8') as f:
        f.write(final_index)
    print("✅ index.html diperbarui.")

def main():
    files = read_markdown_files(MARKDOWN_DIR)
    lowongan_data = []

    for md_file in files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        metadata, body_md = parse_front_matter(content)
        if not metadata.get('title'):
            print(f"❌ Lewati: {md_file} karena tidak ada judul.")
            continue

        body_html = markdown.markdown(body_md)
        schema_html = create_schema(metadata, body_html)

        try:
            date_obj = datetime.strptime(metadata.get('date', ''), '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d-%m-%Y')
        except Exception:
            date_obj = datetime.min
            formatted_date = 'Tanggal Tidak Valid'

        filename = os.path.splitext(os.path.basename(md_file))[0] + '.html'
        generate_job_page(filename, metadata, body_html, schema_html)

        print(f"✅ Dibuat: {filename}")
        lowongan_data.append({
            'title': metadata['title'],
            'image': metadata.get('image', ''),
            'filename': filename,
            'date_obj': date_obj,
            'formatted_date': formatted_date,
            'company': metadata.get('company', ''),
            'location': metadata.get('location', '')
        })

    lowongan_data.sort(key=lambda x: x['date_obj'], reverse=True)
    cards_html = generate_cards(lowongan_data)
    build_index(cards_html)

if __name__ == '__main__':
    main()
