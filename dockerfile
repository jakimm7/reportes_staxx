FROM tobix/pywine:latest

ENV WINEDEBUG=-all
ENV XDG_RUNTIME_DIR=/tmp/runtime-root

WORKDIR /app

COPY requirements.txt .

RUN wine python -m pip install --upgrade pip
RUN wine python -m pip install pyinstaller
RUN wine python -m pip install -r requirements.txt

COPY . .

CMD ["wine", "pyinstaller", "--onefile", "--clean", "main.py"]