#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    print("🚀 Iniciando Sistema de Análise Jurídica...")
    print("📡 URL: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("🔧 ReDoc: http://localhost:8000/redoc")
    print("-" * 50)

    # Mudar para diretório backend
    os.chdir("backend")

    # Executar uvicorn
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

if __name__ == "__main__":
    main()