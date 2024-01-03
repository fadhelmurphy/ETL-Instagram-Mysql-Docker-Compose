# Menggunakan image Python 3.8 sebagai base image
FROM python:3.9

# Set working directory di dalam container
WORKDIR /app

# Menyalin requirements.txt untuk menginstal dependensi
COPY requirements.txt .

# Menginstal dependensi dari requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh konten dari direktori saat ini ke dalam container di dalam direktori /app
COPY . .

# Command untuk menjalankan skrip Python
CMD ["python", "scraper.py"]
