import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import os
import io
from PyPDF2 import PdfReader

# =========================
# CONFIGURAÇÕES
# =========================
NOME = "Guilherme Tamelini"
URL_BASE = "https://www.riopreto.sp.gov.br/diario-oficial"

# =========================
# TWILIO
# =========================
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")
client = Client(account_sid, auth_token)

# =========================
# PEGAR PDF
# =========================
def obter_pdf():
    print("🔎 Buscando página do diário...")

    response = requests.get(URL_BASE)
    soup = BeautifulSoup(response.text, "html.parser")

    links = soup.find_all("a")

    for link in links:
        href = link.get("href")

        if href and ".pdf" in href.lower():
            print("📄 PDF encontrado:", href)
            return href

    print("❌ Nenhum PDF encontrado.")
    return None

# =========================
# LER PDF
# =========================
def ler_pdf(url_pdf):
    print("⬇️ Baixando PDF...")

    response = requests.get(url_pdf)
    pdf_file = io.BytesIO(response.content)

    reader = PdfReader(pdf_file)

    texto = ""

    for page in reader.pages:
        conteudo = page.extract_text()
        if conteudo:
            texto += conteudo

    return texto.lower()

# =========================
# ENVIAR WHATSAPP
# =========================
def enviar_alerta():
    mensagem = f"🚨 ALERTA!\nSeu nome '{NOME}' apareceu no Diário Oficial de Rio Preto."

    client.messages.create(
        from_='whatsapp:+14155238886',
        body=mensagem,
        to='whatsapp:+5517991322765'
    )

# =========================
# FUNÇÃO PRINCIPAL
# =========================
def verificar_diario():
    pdf_url = obter_pdf()

    if not pdf_url:
        return

    texto = ler_pdf(pdf_url)

    if NOME.lower() in texto:
        print("✅ Nome encontrado!")
        enviar_alerta()
    else:
        print("❌ Nome não encontrado.")

# =========================
# EXECUÇÃO
# =========================
if __name__ == "__main__":
    verificar_diario()
