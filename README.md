# Mikrotik Backup Automator 🤖

Script automatizado en Python para realizar backups (Binarios y Exports) de routers Mikrotik y enviarlos a un servidor seguro vía SFTP/SSH. Incluye reportes automáticos a Telegram.

## Características
- 🔒 Conexión segura vía SSH Key.
- 📂 Genera backups `.backup` y `.rsc`.
- 🚀 Setup automático (`setup.sh`).
- 📱 Notificaciones a Telegram con estado del backup.
- 🧹 Limpieza automática de archivos temporales en el router.

## Instalación Rápida

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/TU_USUARIO/TU_REPO.git](https://github.com/TU_USUARIO/TU_REPO.git)
   cd TU_REPO
    ```
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
2. Cronjob (Automático)
Para ejecutar todos los domingos a las 03:00 AM:

    ```bash
    crontab -e
    00 03 * * 0 /ruta/al/repo/main.py >> /ruta/al/repo/backup.log 2>&1