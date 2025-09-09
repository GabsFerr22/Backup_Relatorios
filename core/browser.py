import subprocess
import socket
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config.settings import CAMINHO_CHROME, CAMINHO_PERFIL


def get_free_port():
    """Encontra uma porta livre para o Chrome usar no remote-debugging."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def kill_chrome_port(port):
    """Mata qualquer processo do Chrome que esteja usando a porta informada."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and "chrome" in proc.info['name'].lower():
                if proc.info['cmdline'] and f'--remote-debugging-port={port}' in " ".join(proc.info['cmdline']):
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


class Browser:
    def __init__(self):
        self.driver = None
        self.chrome_process = None
        self.port = None

    def start(self):

        self.port = get_free_port()


        kill_chrome_port(self.port)

        comando = f'"{CAMINHO_CHROME}" --remote-debugging-port={self.port} --user-data-dir="{CAMINHO_PERFIL}"'
        self.chrome_process = subprocess.Popen(comando, shell=True)

 
        options = Options()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.port}")
        prefs = {
            "download.default_directory": r"C:\Users\adm.joao.mendes\Downloads",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "safebrowsing.disable_download_protection": True
        }
        options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(options=options)
        return self.driver

    def quit(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

        if self.chrome_process:
            try:
                self.chrome_process.terminate()
                self.chrome_process.wait(timeout=5)
            except Exception:
                try:
                    self.chrome_process.kill()
                except Exception:
                    pass
            finally:
                self.chrome_process = None
                
        if self.port:
            kill_chrome_port(self.port)
            self.port = None