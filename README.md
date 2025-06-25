# Projeto de IA Local com LM Studio

Este repositório descreve como instalar e configurar o LM Studio para executar localmente um modelo LLM e, em seguida, baixar o modelo **phi-3-mini-4k-instruct**.

---

## 🛠️ Requisitos

- **Hardware**: CPU com AVX2, mínimo 8 GB RAM (16 GB recomendado)  
- **SO**: Windows 10/11 (x86_64), Linux x86_64 ou macOS (Apple Silicon ou Intel)  
- **Espaço em disco**: ≥ 8 GB livre

---

## ⚙️ Instalação

### Linux (AppImage)

```bash
# 1. Baixar AppImage
wget https://installers.lmstudio.ai/linux/x64/<versão>/LM-Studio-<versão>-x64.AppImage

# 2. Tornar executável e extrair
chmod u+x LM-Studio-*.AppImage
./LM-Studio-*.AppImage --appimage-extract

# 3. Ajustar permissões e executar
cd squashfs-root
sudo chown root:root chrome-sandbox
sudo chmod 4755 chrome-sandbox
./lm-studio
