print("🚀 APP INICIANDO...")

import time

while True:
    print("🔁 LOOP ATIVO")
    time.sleep(10)import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import os
import io
import json
from PyPDF2 import PdfReader

# OCR
import pytesseract
from pdf2image import convert_from_bytes

# =========================
# CONFIG
# =========================
NOME = "Guilherme Tamelini"
URL_BASE = "https://www.riopreto.sp.gov.br/diario-oficial"
ARQUIVO_CONTROLE = "verificados.json"

# =========================
# TWILIO
# =========================
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")
client = Client(account_sid, auth_token)

# =========================
# CONTROLE DE PDFs
# =========================
def carregar_verificados():
    if not os.path.exists(ARQUIVO_CONTROLE):
        return []
    with open(ARQUIVO_CONTROLE, "r") as f:
        return json.load(f)

def salvar_verificados(lista):
    with open(ARQUIVO_CONTROLE, "w") as f:
        json.dump(lista, f)

# =========================
# PEGAR PDF MAIS RECENTE
# =========================
def obter_pdf():
    response = requests.get(URL_BASE)
    soup = BeautifulSoup(response.text, "html.parser")

    links = soup.find_all("a")

    pdfs = []
    for link in links:
        href = link.get("href")
        if href and ".pdf" in href.lower():
            if not href.startswith("http"):
                href = URL_BASE + href
            pdfs.append(href)

    if not pdfs:
        return None

    return pdfs[0]  # primeiro geralmente é o mais recente

# =========================
# LER PDF (TEXTO)
# =========================
def ler_pdf_texto(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    texto = ""

    for page in reader.pages:
        conteudo = page.extract_text()
        if conteudo:
            texto += conteudo

    return texto

# =========================
# OCR (CASO PDF ESCANEADO)
# =========================
def ler_pdf_ocr(pdf_bytes):
    imagens = convert_from_bytes(pdf_bytes)
    texto = ""

    for img in imagens:
        texto += pytesseract.image_to_string(img)

    return texto

# =========================
# BUSCAR NOME
# =========================
def buscar_nome(texto):
    texto_lower = texto.lower()
    nome_lower = NOME.lower()

    if nome_lower in texto_lower:
        inicio = texto_lower.find(nome_lower)
        trecho = texto[inicio-100:inicio+100]
        return True, trecho

    return False, ""

# =========================
# ENVIAR ALERTA
# =========================
def enviar_alerta(trecho, url_pdf):
    mensagem = f"""🚨 ALERTA!

Seu nome foi encontrado no Diário Oficial.

Trecho:
{trecho}

Link:
{url_pdf}
"""

    client.messages.create(
        from_='whatsapp:+14155238886',
        body=mensagem,
        to='whatsapp:+5517991322765'
    )

# =========================
# PRINCIPAL
# =========================
def verificar_diario():
    pdf_url = obter_pdf()

    if not pdf_url:
        print("Nenhum PDF encontrado")
        return

    verificados = carregar_verificados()

    if pdf_url in verificados:
        print("PDF já verificado")
        return

    response = requests.get(pdf_url)
    pdf_bytes = response.content

    # tentativa 1: texto normal
    texto = ler_pdf_texto(pdf_bytes)

    # fallback OCR
    if len(texto.strip()) < 100:
        print("Usando OCR...")
        texto = ler_pdf_ocr(pdf_bytes)

    encontrou, trecho = buscar_nome(texto)

    if encontrou:
        enviar_alerta(trecho, pdf_url)
        print("Nome encontrado e enviado!")

    else:
        print("Nome não encontrado")

    verificados.append(pdf_url)
    salvar_verificados(verificados)

# =========================
# EXECUÇÃO
# =========================
if __name__ == "__main__":
    verificar_diario()
import time

while True:
    print("🚀 Rodando verificação...")
    verificar_diario()
    time.sleep(60)
