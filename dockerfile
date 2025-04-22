FROM openjdk:11-slim

# Instalar Python
RUN apt-get update && apt-get install -y python3 python3-pip procps

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Configurar entorno
WORKDIR /app
COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
