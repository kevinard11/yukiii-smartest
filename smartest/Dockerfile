FROM python:3.10

# Tentukan working directory di dalam container
WORKDIR /app

# Step 1: Install deps — hanya berubah kalau requirements.txt berubah
# COPY requirements.txt .
# RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt

# Step 2: Copy setup-lib.py & lib/ (grammar tree-sitter)
# Step ini hanya diulang kalau file setup atau grammar berubah
# COPY setup-lib.py ./setup-lib.py
# COPY ./smartest/lib/ ./smartest/lib/
# RUN python setup-lib.py

# Salin file project ke dalam container
COPY . .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python setup-lib.py

# Jalankan aplikasi Flask
CMD ["python", "app.py"]
