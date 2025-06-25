import os
import whisper
import json
import requests
from openai import OpenAI

# --- CONFIGURAÇÕES DO CLIENTE DA API ---
# Conecta ao servidor local do LM Studio
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

# --- CAMINHOS E ARQUIVOS ---
CAMINHO_AUDIO    = "Audios/matematica.opus"
PASTA_RELATORIOS = "relatorios"
NOME_ARQUIVO     = "relatorio_recomendacoes.json"

# --- Transcrição do áudio ---
def transcrever_audio(caminho):
    if not os.path.exists(caminho):
        print(f"Erro: Arquivo de áudio não encontrado em '{caminho}'")
        # texto de fallback
        return (
            "Eu quero aprender sobre programação orientada a objetos, "
            "talvez em Python. Também me interesso por algoritmos de busca "
            "e a estrutura de dados de grafos."
        )
    modelo = whisper.load_model("base")
    resultado = modelo.transcribe(caminho)
    return resultado["text"]

# --- Extração de tópicos com IA via LM Studio ---
def extrair_topicos_com_lmstudio(texto_transcrito: str) -> list:
    prompt_messages = [
        {
            "role": "system",
            "content": (
                "Você é um especialista em educação. Sua tarefa é analisar o texto "
                "e extrair os principais tópicos técnicos. Retorne a resposta "
                "como uma lista de strings em formato JSON."
            )
        },
        {
            "role": "user",
            "content": (
                f"Analise o texto a seguir e extraia os tópicos de estudo em formato "
                f"de lista JSON: \"{texto_transcrito}\""
            )
        }
    ]

    print("Conectando ao servidor do LM Studio para extrair tópicos...")
    try:
        completion = client.chat.completions.create(
            model="phi-3-mini-4k-instruct",
            messages=prompt_messages,
            temperature=0.7,
        )
        texto_ia = completion.choices[0].message.content
        print(f"Texto recebido da IA: {texto_ia}")
        start = texto_ia.find('[')
        end   = texto_ia.rfind(']') + 1
        if start != -1 and end > start:
            json_str = texto_ia[start:end]
            return json.loads(json_str)
        else:
            print("ERRO: JSON não encontrado na resposta da IA.")
            return []
    except requests.exceptions.ConnectionError:
        print("ERRO DE CONEXÃO: Não foi possível se conectar ao servidor do LM Studio.")
        return []
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao processar a resposta da IA: {e}")
        return []

# --- Recomendação de conteúdo ---
def buscar_livros_por_tag(tag, max_results=3):
    url = f"https://www.googleapis.com/books/v1/volumes?q={tag}&maxResults={max_results}&lang=pt"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        livros = []
        for item in resp.json().get("items", []):
            info = item.get("volumeInfo", {})
            livros.append({
                "titulo":  info.get("title"),
                "autores": info.get("authors", ["N/A"]),
                "link":    info.get("infoLink")
            })
        return livros
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar livros para a tag '{tag}': {e}")
        return []

# --- EXECUÇÃO DO SISTEMA ---
if __name__ == "__main__":
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)
    print("--- Início do Processo ---")

    # 1/3: transcrição
    texto = transcrever_audio(CAMINHO_AUDIO)
    print(f"\n[1/3] Transcrição Concluída:\n\"{texto}\"")

    # 2/3: extração de tópicos
    topicos = extrair_topicos_com_lmstudio(texto)
    print(f"\n[2/3] Tópicos Extraídos pela IA: {topicos}")

    # 3/3: busca de recomendações
    if topicos:
        print("\n[3/3] Buscando Livros Recomendados...")
        recomendacoes_livros = {}

        for topico_info in topicos:
            # Trata tanto strings quanto dicionários
            if isinstance(topico_info, dict):
                # tenta extrair por 'topic' ou usa o primeiro valor disponível
                titulo = topico_info.get('topic') or next(iter(topico_info.values()), "")
            else:
                titulo = str(topico_info)

            if not titulo:
                continue

            print(f"  - Buscando por: '{titulo}'")
            livros = buscar_livros_por_tag(titulo)
            if livros:
                recomendacoes_livros[titulo] = livros

        resultado_final = {
            "texto_original": texto,
            "topicos_detectados_pela_ia": topicos,
            "recomendacoes_livros": recomendacoes_livros
        }

        caminho = os.path.join(PASTA_RELATORIOS, NOME_ARQUIVO)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(resultado_final, f, indent=4, ensure_ascii=False)

        print(f"\n--- Processo Finalizado. Relatório salvo em '{caminho}' ---")
    else:
        print("\nNenhum tópico foi extraído. Processo encerrado.")
