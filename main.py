import os
import itertools
import base64
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# CONFIG

load_dotenv()

BASE_PATH = Path("colecoes")
OUTPUT_PATH = Path("outputs")
MODEL_NAME = "gpt-image-1"
IMAGE_SIZE = "1024x1536"

client = OpenAI()

# PROMPT

PROMPT = """
Create an ultra-photorealistic vertical 2:3 interior design scene for premium ecommerce.

The uploaded files are separate framed artworks.
Each uploaded image represents ONE independent physical artwork.
If multiple images are provided, they must appear as multiple separate frames on the wall.
DO NOT merge artworks into a single frame.
DO NOT combine images into one composition.
Each image must remain an independent artwork.

Goal:
Create a sophisticated, elegant and aspirational interior that matches the artistic style and mood of the artwork(s).
Choose the most appropriate environment automatically (living room, dining room, bedroom, office, etc.) based on the style and colors of the art.

Artwork Rules (STRICT):
- Preserve exact proportions.
- Preserve exact colors.
- No cropping.
- No distortion.
- No modification of the artwork.
- No passepartout.
- No white margins.
- No added borders.
- No redesign.
- Each artwork must remain visually identical to the uploaded file.

Framing:
- Either frameless or thin frame only.
- Frame colors allowed: black, white, light wood, dark wood.
- Frame must not overpower the artwork.

Placement:
- If multiple artworks are provided, arrange them as separate frames aligned naturally on the wall.
- Keep realistic spacing between frames.
- Scale artworks proportionally to the room size (not too small, not oversized).

Environment Style:
- Luxury interior photography
- Elegant furniture
- Sophisticated decorative objects
- Realistic materials
- Soft cinematic lighting
- Natural shadows
- Subtle ambient light interaction with the frame surface (without altering artwork colors)

The final image must look like a high-end interior magazine photo.
Extremely realistic.
Highly detailed.
Premium quality.
"""


def gerar_combinacoes(arquivos):
    """Gera todas as combinações possíveis (2 ou mais imagens)."""
    combinacoes = []
    for r in range(2, len(arquivos) + 1):
        combinacoes += list(itertools.combinations(arquivos, r))
    return combinacoes


def gerar_imagem(caminhos_imagens, caminho_saida):
    """Envia imagens para a API e salva o mockup gerado."""
    try:
        print(f"🖼️  Gerando mockup para {len(caminhos_imagens)} imagens...")

        response = client.images.edit(
            model=MODEL_NAME,
            image=[open(c, "rb") for c in caminhos_imagens],
            prompt=PROMPT,
            size=IMAGE_SIZE,
            quality="high",
        )

        img_base64 = response.data[0].b64_json
        img_bytes = base64.b64decode(img_base64)

        with open(caminho_saida, "wb") as f:
            f.write(img_bytes)

        print(f"✅ Salvo em: {caminho_saida}")

    except Exception as e:
        print(f"❌ Erro ao gerar imagem: {e}")


def processar_colecao(nome_pasta):
    """Processa uma coleção inteira."""
    caminho_colecao = BASE_PATH / nome_pasta

    arquivos = [
        f for f in os.listdir(caminho_colecao)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if len(arquivos) < 2:
        print(f"⚠️  Coleção '{nome_pasta}' ignorada (menos de 2 imagens).")
        return

    combinacoes = gerar_combinacoes(arquivos)

    pasta_output = OUTPUT_PATH / nome_pasta
    pasta_output.mkdir(parents=True, exist_ok=True)

    print(f"\n🚀 Processando coleção: {nome_pasta}")
    print(f"Total de combinações: {len(combinacoes)}")

    for combinacao in combinacoes:
        caminhos = [str(caminho_colecao / img) for img in combinacao]

        nome_saida = "_".join(
            [Path(img).stem for img in combinacao]
        ) + ".png"

        caminho_saida = pasta_output / nome_saida

        gerar_imagem(caminhos, caminho_saida)

    print(f"🎉 Coleção finalizada: {nome_pasta}\n")

def main():
    OUTPUT_PATH.mkdir(exist_ok=True)

    if not BASE_PATH.exists():
        print("❌ Pasta 'colecoes' não encontrada.")
        return

    for colecao in os.listdir(BASE_PATH):
        if (BASE_PATH / colecao).is_dir():
            processar_colecao(colecao)


if __name__ == "__main__":
    main()
