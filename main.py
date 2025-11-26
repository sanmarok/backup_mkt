#!/etc/dev/backup/bin/python3
import os
import env
import requests
from datetime import datetime
from netmiko import ConnectHandler

def send_telegram_report(lines):
    """Envía el resumen final a Telegram"""
    if not lines:
        print("ℹ️ No hay reportes para enviar.")
        return

    print("📨 Enviando reporte a Telegram...")
    
    # Unimos las líneas para formar la lista
    message_text = "🤖 *Backups status * 🤖\n\n" + "\n".join(lines)
    
    url = f"https://api.telegram.org/bot{env.TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": env.TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown" 
    }
    
    try:
        requests.post(url, json=data, timeout=10)
        print("✅ Reporte enviado correctamente.")
    except Exception as e:
        print(f"❌ Error enviando telegram: {e}")

def backup_device(device):
    dev_name = device['name']
    print(f"\n========================================")
    print(f"🚀 Iniciando respaldo de: {dev_name}")
    print(f"========================================")

    # Estructura de carpetas
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"{dev_name}_{date_str}"
    target_path = os.path.join(env.BACKUP_ROOT_DIR, dev_name, folder_name)

    if not os.path.exists(target_path):
        os.makedirs(target_path)
        print(f"📁 Carpeta creada: {target_path}")

    remote_backup = "temp_backup.backup"
    remote_export = "temp_export.rsc"
    
    local_backup_file = os.path.join(target_path, f"{folder_name}.backup")
    local_export_file = os.path.join(target_path, f"{folder_name}.rsc")

    try:
        # Filtramos parámetros para netmiko
        netmiko_params = {k: v for k, v in device.items() if k != 'name'}
        
        # 1. Conexión
        print(f"🔌 Conectando a {device['host']}...")
        net_connect = ConnectHandler(**netmiko_params)
        print("   -> Conexión establecida.")
        
        # 2. Generar Backups en Router
        print("⚙️  Generando backup binario (.backup)...")
        net_connect.send_command(f'/system backup save name={remote_backup}')
        
        print("📝 Generando export script (.rsc)...")
        net_connect.send_command(f'/export file={remote_export}', read_timeout=60)
        
        # 3. Descargar Archivos (SFTP)
        print("⬇️  Descargando archivos vía SFTP...")
        sftp = net_connect.remote_conn.transport.open_sftp_client()
        
        sftp.get(remote_backup, local_backup_file)
        print(f"   -> Descargado: {local_backup_file}")
        
        sftp.get(remote_export, local_export_file)
        print(f"   -> Descargado: {local_export_file}")
        
        sftp.close()
        
        # 4. Limpieza en Router
        print("🧹 Borrando archivos temporales del router...")
        net_connect.send_command(f'/file remove {remote_backup}')
        net_connect.send_command(f'/file remove {remote_export}')
        
        net_connect.disconnect()
        print("🔌 Desconectado.")
        
        print(f"✅ ÉXITO: {dev_name} respaldado correctamente.")
        return f"*{dev_name}* ✅"

    except Exception as e:
        error_msg = str(e).split('\n')[0]
        print(f"❌ ERROR CRÍTICO en {dev_name}: {error_msg}")
        return f"*{dev_name}* ❌"

if __name__ == "__main__":
    print(f"\n🏁 --- INICIO DEL PROCESO: {datetime.now()} ---")
    report_lines = []
    
    for device_conf in env.DEVICES:
        result = backup_device(device_conf)
        report_lines.append(result)
        
    send_telegram_report(report_lines)
    print(f"\n🏁 --- FIN DEL PROCESO: {datetime.now()} ---")