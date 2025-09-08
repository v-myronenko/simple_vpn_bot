# services/wg_manager.py
import paramiko
import io

class WGManager:
    def __init__(self, host: str, user: str, key_path: str):
        self.host = host
        self.user = user
        self.key_path = key_path

    def add_peer(self, name: str) -> tuple[str, bytes]:
        """Повертає (текст конфігу, PNG байти QR)"""
        key = paramiko.RSAKey.from_private_key_file(self.key_path)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host, username=self.user, pkey=key, timeout=15)

        cmd = f"sudo /usr/local/bin/wg-add-peer {name}"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if err:
            ssh.close()
            raise RuntimeError(err)

        # дістаємо шлях до створеного конфігу
        conf_path = None
        for line in out.splitlines():
            if line.startswith("CONFIG_PATH="):
                conf_path = line.split("=",1)[1].strip()
                break
        if not conf_path:
            ssh.close()
            raise RuntimeError("No CONFIG_PATH returned")

        # заберемо сам конфіг
        sftp = ssh.open_sftp()
        with sftp.file(conf_path, "r") as f:
            conf_text = f.read().decode()

        # PNG QR (може не бути, тоді повернемо порожні байти)
        png_path = conf_path.replace(".conf", ".png")
        png_bytes = b""
        try:
            with sftp.file(png_path, "rb") as f:
                png_bytes = f.read()
        except Exception:
            pass

        sftp.close()
        ssh.close()
        return conf_text, png_bytes
