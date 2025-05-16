FROM python:3.11-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo requirements.txt da raiz
COPY requirements.txt /app/

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expor porta
EXPOSE 8050

# Comando para rodar o Dash
CMD ["python", "dash_projetos.py"]
