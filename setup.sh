#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}--- Iniciando Setup del Sistema de Backup Mikrotik ---${NC}"

# 1. Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 no está instalado.${NC}"
    exit 1
fi

# 2. Crear Entorno Virtual (si no existe)
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual en ./venv ..."
    python3 -m venv venv
else
    echo -e "${YELLOW}El entorno virtual ya existe. Saltando creación.${NC}"
fi

# 3. Crear requirements.txt si no existe
if [ ! -f "requirements.txt" ]; then
    echo "Creando requirements.txt base..."
    echo -e "netmiko\nrequests" > requirements.txt
fi

# 4. Instalar Dependencias
echo "Instalando/Actualizando dependencias..."
./venv/bin/pip install -r requirements.txt --upgrade --quiet
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dependencias instaladas correctamente.${NC}"
else
    echo -e "${RED}Error instalando dependencias.${NC}"
    exit 1
fi

# 5. Crear plantilla env.py (SOLO SI NO EXISTE)
if [ ! -f "env.py" ]; then
    echo "Creando plantilla de configuración env.py..."
    cat <<EOT >> env.py
import os

# --- Configuración de Rutas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_ROOT_DIR = os.path.join(BASE_DIR, 'backups')

# --- CONFIGURACIÓN DE TELEGRAM ---
TELEGRAM_TOKEN = "TU_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "TU_CHAT_ID_AQUI"

# --- LISTA DE EQUIPOS ---
DEVICES = [
    {
        'name': 'Mikrotik_Ejemplo',
        'host': '192.168.88.1',
        'username': 'admin',
        'use_keys': True,
        'key_file': '/root/.ssh/id_rsa',
        'port': 22,
        'device_type': 'mikrotik_routeros'
    },
]
EOT
    echo -e "${YELLOW}⚠️  AVISO: Se ha creado 'env.py'. Debes editarlo con tus datos reales.${NC}"
else
    echo -e "${GREEN}Archivo 'env.py' detectado. Se mantiene la configuración actual.${NC}"
fi

# 6. Configurar main.py y ajustar Shebang
if [ -f "main.py" ]; then
    # Obtenemos la ruta absoluta del python nuevo
    VENV_PYTHON=$(readlink -f ./venv/bin/python3)
    
    # Reemplazamos la primera línea de main.py con la ruta correcta
    sed -i "1s|^#!.*|#!$VENV_PYTHON|" main.py
    
    chmod +x main.py
    echo -e "Shebang de main.py actualizado a: $VENV_PYTHON"
else
    echo -e "${RED}Error: No se encuentra main.py${NC}"
fi

echo -e "${GREEN}--- Setup Finalizado Exitosamente ---${NC}"
echo "1. Edita env.py con tus datos."
echo "2. Ejecuta ./main.py para probar."