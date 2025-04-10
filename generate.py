import os

LOWONGAN_FOLDER = "lowongan"
OUTPUT_FOLDER = "."
TEMPLATE_FILE = "template.html"

def baca_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return f.read()

def konversi_md_ke_html(markdown):
    # Ambil metadata dan isi
    baris = markdown.splitlines()
    judul = ""
    tanggal = ""
    isi_md = []
    parsing_isi = False

    for baris_md in baris:
        if baris_md.startswith("title:"):
            judul = baris_md.replace("title:", "").strip().strip('"')
        elif baris_md.startswith("date:"):
            tanggal = baris_md.replace("date:", "").strip()
        elif baris_md.strip() == "---":
            continue
        else:
            isi_md.append(baris_md)

    isi_text = "\n".join(isi_md).strip()

    # Konversi markdown dasar ke HTML
    isi_html = isi_text.replace("\n", "<br>") \
                       .replace("**", "<b>").replace("__", "<b>") \
                       .replace("*", "<i>").replace("_", "<i>")

    return judul, tanggal, isi_html

def buat_html(judul, tanggal, isi, template):
    html = template.replace("{{title}}", judul)
    html = html.replace("{{content}}", isi)
    return html

def proses_file():
    template = baca_template()
    for nama_file in os.listdir(LOWONGAN_FOLDER):
        if nama_file.endswith(".md"):
            path_file = os.path.join(LOWONGAN_FOLDER, nama_file)
            with open(path_file, "r", encoding="utf-8") as f:
                markdown = f.read()

            judul, tanggal, isi = konversi_md_ke_html(markdown)
            html = buat_html(judul, tanggal, isi, template)

            nama_output = nama_file.replace(".md", ".html").replace(" ", "-").lower()
            path_output = os.path.join(OUTPUT_FOLDER, nama_output)
            with open(path_output, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"✅ Dibuat: {nama_output}")

if __name__ == "__main__":
    proses_file()
