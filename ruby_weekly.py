import requests
from bs4 import BeautifulSoup
import openai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.enums import TA_LEFT
from tqdm import tqdm
import os

def fetch_article_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    article_text = "\n".join([para.get_text() for para in paragraphs])
    return article_text
def summarize_article_in_polish(text):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Jesteś programistą Ruby on Rails z 10 letnim doświadczeniem"},
            {"role": "user", "content": f"Streszcz poniższy artykuł po polsku uywajac 2500 liter:\n\n{text}\n\nStreszczenie:"}
        ],
        max_tokens=4096
    )
    return response.choices[0].message.content.strip()
url = 'https://rubyweekly.com/issues/707'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
links = [a['href'] for a in soup.find_all('a', href=True) if 'http' in a['href']]
summaries = []

for link in tqdm(links, desc="Processing links"):
    try:
        text = fetch_article_text(link)
        summary = summarize_article_in_polish(text)
        summaries.append({'link': link, 'summary': summary})
    except Exception as e:
        print(f"Error processing {link}: {e}")


pdf_file = "summaries.pdf"        
arial_paths = [
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Arial.ttf",
    "/Library/Fonts/Microsoft/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf"
]

arial_font_path = None
for path in arial_paths:
    if os.path.exists(path):
        arial_font_path = path
        break

if arial_font_path is None:
    raise FileNotFoundError("Nie można znaleźć czcionki Arial w standardowych lokalizacjach.")

# Rejestracja czcionki Arial
pdfmetrics.registerFont(TTFont('Arial', arial_font_path))

# Funkcja do łamania tekstu na paragrafy
def draw_paragraph(c, text, x, y, max_width):
    style = getSampleStyleSheet()['Normal']
    style.fontName = 'Arial'
    style.fontSize = 12
    style.leading = 14
    style.alignment = TA_LEFT
    p = Paragraph(text, style)
    p.wrapOn(c, max_width, y)
    p.drawOn(c, x, y)

# Tworzenie PDF
c = canvas.Canvas(pdf_file, pagesize=letter)
c.setLineWidth(.3)
c.setFont('Arial', 12)

# Dodawanie treści do PDF
y = 750
max_width = 500
# for item in summaries:
#     link_text = f"Link: {item['link']}"
#     summary_text = f"Streszczenie: {item['summary']}"
#     print(item['summary'])
#     draw_paragraph(c, link_text, 30, y, max_width)
#     y -= 20  # Przestrzeń po linku
#     draw_paragraph(c, summary_text, 30, y, max_width)
#     y -= 60  # Przestrzeń po streszczeniu (dostosuj w razie potrzeby)

# c.save()

text_file = "summaries.txt"

# Otwieramy plik do zapisu w trybie tekstowym
with open(text_file, 'w', encoding='utf-8') as f:
    # Iterujemy przez każdy element w liście summaries
    for item in summaries:
        # Formatujemy dane z item
        link_text = f"Link: {item['link']}"
        summary_text = f"Streszczenie: {item['summary']}"
        
        # Zapisujemy dane do pliku tekstowego
        f.write(link_text + '\n')
        f.write(summary_text + '\n\n')  # Dwa znaki nowej linii po każdym streszczeniu

# Komunikat po zapisaniu danych
print(f"Dane zostały zapisane do pliku {text_file}.")