#!/usr/bin/env python3
"""Rubiana - janela unica para PC (v0): minerar e ver blocos no navegador.
Uso: python3 tools/rubiana-app.py [--rede testnet|principal|regtest] [--config arquivo] [--no-browser]
Abre uma pagina local protegida por uma senha aleatoria (so vale nesta execucao).
Ctrl+C ou o botao Sair encerram."""
import argparse
import collections
import importlib.util
import json
import os
import re
import secrets
import signal
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

ap = argparse.ArgumentParser()
ap.add_argument("--rede", default="testnet", choices=["testnet", "principal", "regtest"])
ap.add_argument("--bin", default=os.path.join(RAIZ, "build", "bin"))
ap.add_argument("--config", default="", help="configuracao.txt (opcional)")
ap.add_argument("--port", type=int, default=0, help="0 = escolhe uma porta livre")
ap.add_argument("--no-browser", action="store_true")
ap.add_argument("--permitir-host", action="append", default=[], help="nome extra aceito no cabecalho Host (ex.: Codespaces)")
args = ap.parse_args()

EXT = ".exe" if os.name == "nt" else ""
daemon = os.path.join(args.bin, "rubianad" + EXT)
cli_path = os.path.join(args.bin, "rubiana-cli" + EXT)
engine = os.path.join(args.bin, "rubiana-miner" + EXT)
for f in (daemon, cli_path, engine):
    if not os.path.exists(f):
        sys.exit("nao encontrei " + f + " (compile primeiro)")
CLI = [cli_path] + ([] if args.rede == "principal" else ["-" + args.rede])
TOKEN = secrets.token_urlsafe(18)
TRAVA = threading.Lock()
LOG = collections.deque(maxlen=300)
MIN = {"proc": None, "achados": 0, "taxa": ""}
ESTADO = {"no_nosso": False}
CARTEIRA_NOME = "rubiana"
CART = {"pronta": False}
_END = {}
_NO = {"t": 0.0, "v": {}}


def cli(*a, wallet=False):
    cmd = CLI + (["-rpcwallet=" + CARTEIRA_NOME] if wallet else []) + [str(x) for x in a]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return 1, "tempo esgotado"
    return r.returncode, (r.stdout.strip() or r.stderr.strip())


def cli_stdin(args_list, linhas, wallet=False, timeout=900):
    # Para segredos: os valores vao pela entrada padrao, nunca pela linha de comando.
    cmd = CLI + ["-stdin", "-rpcclienttimeout=0"] + (["-rpcwallet=" + CARTEIRA_NOME] if wallet else []) + [str(x) for x in args_list]
    try:
        r = subprocess.run(cmd, input="\n".join(linhas) + "\n", capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 1, "tempo esgotado"
    return r.returncode, (r.stdout.strip() or r.stderr.strip())


def nos_de_entrada():
    nos = []
    try:
        txt = open(os.path.join(AQUI, "rubiana-mine.py"), encoding="utf-8").read()
        nome_lista = "NOS_PRINCIPAL" if args.rede == "principal" else "NOS_DE_ENTRADA"
        m = re.search(nome_lista + r"\s*=\s*\[(.*?)\]", txt, re.S)
        if m:
            nos += re.findall(r'"([^"]+)"', m.group(1))
    except OSError:
        pass
    arq = os.path.join(RAIZ, "nos.txt")
    if os.path.exists(arq):
        for linha in open(arq, encoding="utf-8", errors="replace"):
            linha = linha.strip()
            if linha and not linha.startswith("#") and ":" in linha:
                nos.append(linha)
    return nos


def threads_padrao():
    n = max(1, (os.cpu_count() or 2) // 2)
    if args.config and os.path.exists(args.config):
        for linha in open(args.config, encoding="utf-8", errors="replace"):
            linha = linha.strip()
            if linha.startswith("#") or "=" not in linha:
                continue
            k, v = [x.strip().lower() for x in linha.split("=", 1)]
            if k == "processadores" and v.isdigit() and int(v) >= 1:
                n = min(int(v), os.cpu_count() or 1)
    return n


def garantir_no():
    code, out = cli("getblockcount")
    if code == 0 or "-28" in out:
        print("no ja estava ligado.", flush=True)
        if args.rede in ("testnet", "principal"):
            for n in nos_de_entrada():
                cli("addnode", n, "add")
        return
    print("iniciando o no...", flush=True)
    flags = ([] if args.rede == "principal" else ["-" + args.rede]) + ["-dnsseed=0", "-fixedseeds=0", "-listenonion=0", "-dbcache=64", "-txindex=1"]
    addn = ["-addnode=" + n for n in nos_de_entrada()] if args.rede in ("testnet", "principal") else []
    if os.name == "nt":
        subprocess.Popen([daemon] + flags + addn, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
    else:
        subprocess.run([daemon] + flags + ["-daemon"] + addn, check=True)
    ESTADO["no_nosso"] = True


def carregar_explorador():
    caminho = os.path.join(AQUI, "rubiana-explorer.py")
    spec = importlib.util.spec_from_file_location("rubiana_explorer", caminho)
    mod = importlib.util.module_from_spec(spec)
    antigo = sys.argv
    sys.argv = [caminho, "--port", "0"]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = antigo
    mod.CLI = list(CLI)
    return mod


EXPLORADOR = carregar_explorador()
import rubiana_carteira as CARTEIRA  # noqa: E402


def preparar_carteira():
    t0 = time.time()
    while time.time() - t0 < 300:
        code, _ = cli("getblockcount")
        if code == 0:
            CART["pronta"] = CARTEIRA.garantir(cli)
            return
        time.sleep(2)


threading.Thread(target=preparar_carteira, daemon=True).start()


def api_explorador(caminho, q):
    ex = EXPLORADOR
    if caminho == "/api/summary":
        return ex.api_summary()
    if caminho == "/api/blocks":
        return ex.api_blocks(min(int(q.get("n", "20")), 100))
    if caminho == "/api/block":
        return ex.api_block(q["q"])
    if caminho == "/api/tx":
        return ex.api_tx(q["id"], q.get("bh"))
    if caminho == "/api/address":
        return ex.api_addr(q["a"])
    return None


def ler_saida(p):
    for linha in p.stdout:
        linha = linha.rstrip()
        if not linha:
            continue
        LOG.append(linha)
        if re.match(r"^bloco \d+:", linha):
            MIN["achados"] += 1
        m = re.search(r"([0-9.]+)\s*H/s", linha)
        if m:
            MIN["taxa"] = m.group(1) + " H/s"


def iniciar(corpo):
    try:
        threads = int(corpo.get("threads", threads_padrao()))
    except (TypeError, ValueError):
        return {"erro": "numero de nucleos invalido"}
    threads = max(1, min(threads, os.cpu_count() or 1))
    with TRAVA:
        p = MIN["proc"]
        if p and p.poll() is None:
            return {"erro": "ja esta minerando"}
        if not CART["pronta"]:
            return {"erro": "Crie ou restaure a sua carteira antes de minerar (aba Carteira)."}
        cmd = [sys.executable, os.path.join(AQUI, "rubiana-mine.py"), "--rede", args.rede, "--bin", args.bin, "--threads", str(threads), "--carteira", CARTEIRA_NOME]
        if corpo.get("full"):
            cmd.append("--full")
        env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
        kw = {"creationflags": 0x00000200} if os.name == "nt" else {"start_new_session": True}
        LOG.clear()
        MIN["achados"], MIN["taxa"] = 0, ""
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", bufsize=1, env=env, **kw)
        MIN["proc"] = p
        threading.Thread(target=ler_saida, args=(p,), daemon=True).start()
    return {"ok": True}


def parar_mineracao():
    with TRAVA:
        p = MIN["proc"]
        if not p or p.poll() is not None:
            return
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
        else:
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()


def endereco():
    arq = os.path.join(os.path.expanduser("~"), ".rubiana", "endereco-" + args.rede + ".txt")
    try:
        a = open(arq).read().strip()
    except OSError:
        return None
    if not a or not CART["pronta"]:
        return None
    if _END.get("a") == a:
        return a
    code, out = cli("getaddressinfo", a, wallet=True)
    try:
        if code == 0 and json.loads(out).get("ismine"):
            _END["a"] = a
            return a
    except ValueError:
        pass
    return None


def info_no():
    agora = time.time()
    if agora - _NO["t"] < 2:
        return _NO["v"]
    v = {"no": False, "altura": None, "conexoes": None, "saldo": None, "txindex": None}
    code, out = cli("getblockcount")
    if code == 0 and out.isdigit():
        v["no"] = True
        v["altura"] = int(out)
        if not CART["pronta"]:
            CART["pronta"] = CARTEIRA.estado(cli).get("estado") == "pronta"
        c, o = cli("getconnectioncount")
        if c == 0 and o.isdigit():
            v["conexoes"] = int(o)
        c, o = cli("getbalance", wallet=True)
        if c == 0:
            v["saldo"] = o
        c, o = cli("getindexinfo")
        if c == 0:
            try:
                v["txindex"] = "txindex" in json.loads(o)
            except ValueError:
                pass
    _NO["t"], _NO["v"] = agora, v
    return v


def status():
    v = dict(info_no())
    p = MIN["proc"]
    v.update({"rede": args.rede, "minerando": bool(p and p.poll() is None), "achados": MIN["achados"],
              "taxa": MIN["taxa"], "log": list(LOG)[-80:], "threads_padrao": threads_padrao(),
              "nucleos": os.cpu_count() or 1, "endereco": endereco(), "carteira": CART["pronta"]})
    return v


PAGE_APP = r"""<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rubiana</title>
<style>
body{font-family:system-ui,sans-serif;margin:0;background:#0f1220;color:#e8eaf6}
header{padding:12px 14px;background:#1a1f3a;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
h1{font-size:18px;margin:0;flex:1}
h1 small{font-weight:normal;color:#ffcc80;font-size:12px}
button{padding:8px 14px;border:0;border-radius:6px;background:#7c4dff;color:#fff;cursor:pointer}
button.sec{background:#2a2f50}
button:disabled{opacity:.5;cursor:default}
nav{display:flex;gap:6px;padding:10px 14px 0}
nav button{background:#2a2f50}
nav button.on{background:#7c4dff}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;padding:10px 14px}
.card{background:#1a1f3a;border-radius:10px;padding:10px}
.card b{display:block;font-size:11px;color:#9fa8da;font-weight:normal}
.card span{font-size:17px}
.box{background:#1a1f3a;border-radius:10px;padding:12px;margin:10px 14px}
label{margin-right:12px}
input[type=number]{width:70px;padding:6px;border-radius:6px;border:0}
pre{white-space:pre-wrap;word-break:break-all;background:#0b0e1a;padding:10px;border-radius:8px;max-height:300px;overflow:auto;font-size:12px;margin:0}
.aviso{color:#ffcc80}
.mono{font-family:monospace;word-break:break-all}
iframe{width:100%;height:80vh;border:0}
</style></head><body>
<header><h1>Rubiana <small>REDE DE TESTE: as moedas não têm valor</small></h1>
<button class="sec" onclick="sair()">Sair</button></header>
<nav><button id="b-min" class="on" onclick="aba('min')">Minerar</button>
<button id="b-blo" onclick="aba('blo')">Blocos</button>
<button id="b-car" onclick="aba('car')">Carteira</button></nav>
<div id="a-min">
<div class="cards" id="cards"></div>
<div class="box"><b>Endereço de mineração:</b> <span class="mono" id="end"></span></div>
<div class="box">
<label>Núcleos a usar: <input type="number" id="nuc" min="1" value="1"></label>
<label><input type="checkbox" id="full"> modo completo (mais rápido, usa cerca de 2 GB de memória)</label>
<button id="ini" onclick="iniciar()">Iniciar mineração</button>
<button id="par" class="sec" onclick="parar()" disabled>Parar</button>
<span id="est"></span>
<p class="aviso" id="aviso"></p>
</div>
<div class="box"><pre id="log"></pre></div>
</div>
<div id="a-blo" style="display:none"><iframe id="fr"></iframe></div>
<div id="a-car" style="display:none"><iframe id="fc"></iframe></div>
<script>
const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function api(u,corpo){
  const o=corpo===undefined?{}:{method:'POST',headers:{'X-Rubiana':'1','Content-Type':'application/json'},body:JSON.stringify(corpo)};
  const r=await fetch(u,o);return r.json();
}
function aba(n){
  $('#a-min').style.display=n==='min'?'':'none';
  $('#a-blo').style.display=n==='blo'?'':'none';
  $('#a-car').style.display=n==='car'?'':'none';
  $('#b-min').className=n==='min'?'on':'';
  $('#b-blo').className=n==='blo'?'on':'';
  $('#b-car').className=n==='car'?'on':'';
  if(n==='blo'&&!$('#fr').getAttribute('src'))$('#fr').setAttribute('src','/blocos');
  if(n==='car'&&!$('#fc').getAttribute('src'))$('#fc').setAttribute('src','/carteira');
}
let pronto=false,ocupado=false,jaIr=false;
const val=x=>(x===null||x===undefined)?'-':x;
async function atualizar(){
  if(ocupado)return;ocupado=true;
  try{
    const s=await api('/api/status');
    const c=[['Rede',s.rede],['Nó',s.no?'ligado':'iniciando...'],['Altura',val(s.altura)],['Conexões',val(s.conexoes)],['Saldo (já maduro)',val(s.saldo)],['Blocos enviados',s.achados],['Velocidade',s.taxa||'-']];
    $('#cards').innerHTML=c.map(x=>'<div class="card"><b>'+x[0]+'</b><span>'+esc(x[1])+'</span></div>').join('');
    $('#end').textContent=s.endereco||'(aparece depois de iniciar a mineração)';
    if(s.no&&!s.carteira&&!jaIr){jaIr=true;aba('car')}
    $('#ini').disabled=s.minerando||!s.carteira;$('#par').disabled=!s.minerando;
    $('#est').textContent=s.minerando?' Minerando...':' Parado.';
    $('#aviso').textContent=(s.no&&!s.carteira)?'Para minerar, primeiro crie ou restaure a sua carteira na aba Carteira.':(s.no&&s.minerando&&s.conexoes===0)?'ATENÇÃO: você não está conectado à rede (Conexões 0). Os blocos que você minerar agora podem ser descartados. Veja no LEIA-ME a seção sobre conexões.':(s.no&&s.txindex===false)?'Aviso: este nó foi iniciado sem -txindex=1. Abrir uma transação pelo número pode dar erro; clicar nela dentro de um bloco funciona.':'';
    if(!pronto){$('#nuc').value=s.threads_padrao;$('#nuc').max=s.nucleos;pronto=true}
    const pre=$('#log');const fim=pre.scrollTop+pre.clientHeight>=pre.scrollHeight-20;
    pre.textContent=s.log.join('\n');if(fim)pre.scrollTop=pre.scrollHeight;
  }catch(e){$('#est').textContent=' Sem resposta (a janela foi encerrada?)'}
  ocupado=false;
}
async function iniciar(){
  const r=await api('/api/iniciar',{threads:parseInt($('#nuc').value)||1,full:$('#full').checked});
  if(r.erro)alert(r.erro);
  atualizar();
}
async function parar(){await api('/api/parar',{});atualizar()}
async function sair(){
  if(!confirm('Encerrar a Rubiana e parar a mineração?'))return;
  try{await api('/api/sair',{})}catch(e){}
  document.body.innerHTML='<p style="padding:20px">Encerrado. Pode fechar esta aba.</p>';
}
setInterval(atualizar,2000);atualizar();
</script></body></html>"""

servidor = ThreadingHTTPServer(("127.0.0.1", args.port), BaseHTTPRequestHandler)
PORTA = servidor.server_address[1]
PERMITIDOS = {"127.0.0.1:%d" % PORTA, "localhost:%d" % PORTA}
for _h in args.permitir_host:
    PERMITIDOS.add(_h.lower())
ORIGENS = {e + h for h in PERMITIDOS for e in ("http://", "https://")}
CSP = "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'self'"


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _resp(self, corpo, tipo="application/json", code=200):
        dados = corpo.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", tipo + "; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", CSP)
        self.end_headers()
        self.wfile.write(dados)

    def _json(self, obj, code=200):
        self._resp(json.dumps(obj), code=code)

    def _host_ok(self):
        return (self.headers.get("Host") or "").lower() in PERMITIDOS

    def _cookie_ok(self):
        for parte in (self.headers.get("Cookie") or "").split(";"):
            k, _, v = parte.strip().partition("=")
            if k == "rubiana_t" and secrets.compare_digest(v.encode(), TOKEN.encode()):
                return True
        return False

    def do_GET(self):
        if not self._host_ok():
            return self._json({"erro": "host nao permitido: " + str(self.headers.get("Host"))}, 403)
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path == "/" and "t" in q and secrets.compare_digest(q["t"].encode(), TOKEN.encode()):
            self.send_response(303)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", "rubiana_t=" + TOKEN + "; Path=/; HttpOnly; SameSite=Strict")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if not self._cookie_ok():
            return self._resp("Acesso negado. Abra a janela pelo endereco que aparece no programa (janela.bat).", "text/plain", 403)
        try:
            if u.path == "/":
                self._resp(pagina(PAGE_APP), "text/html")
            elif u.path == "/blocos":
                self._resp(EXPLORADOR.PAGE, "text/html")
            elif u.path == "/api/status":
                self._json(status())
            elif u.path == "/carteira":
                self._resp(pagina(CARTEIRA.PAGE), "text/html")
            elif u.path == "/api/carteira/estado":
                self._json(CARTEIRA.estado(cli))
            elif u.path == "/api/carteira/resumo":
                self._json(CARTEIRA.resumo(cli))
            elif u.path == "/api/carteira/historico":
                self._json(CARTEIRA.historico(cli))
            elif u.path.startswith("/api/"):
                r = api_explorador(u.path, q)
                if r is None:
                    self._json({"erro": "nao encontrado"}, 404)
                else:
                    self._json(r)
            else:
                self._json({"erro": "nao encontrado"}, 404)
        except Exception as e:
            self._json({"erro": str(e)}, 500)

    def do_POST(self):
        if not self._host_ok() or not self._cookie_ok() or self.headers.get("X-Rubiana") != "1":
            return self._json({"erro": "negado"}, 403)
        o = self.headers.get("Origin")
        if o and o not in ORIGENS:
            return self._json({"erro": "origem nao permitida"}, 403)
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 2000:
                return self._json({"erro": "pedido grande demais"}, 413)
            corpo = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/api/iniciar":
                self._json(iniciar(corpo))
            elif self.path == "/api/parar":
                parar_mineracao()
                self._json({"ok": True})
            elif self.path == "/api/carteira/frase/nova":
                self._json(CARTEIRA.frase_nova(corpo))
            elif self.path == "/api/carteira/frase/confirmar":
                r = CARTEIRA.frase_confirmar(cli, cli_stdin, corpo, args.rede)
                CART["pronta"] = CART["pronta"] or bool(r.get("ok"))
                self._json(r)
            elif self.path == "/api/carteira/frase/restaurar":
                r = CARTEIRA.frase_restaurar(cli, cli_stdin, corpo, args.rede)
                CART["pronta"] = CART["pronta"] or bool(r.get("ok"))
                self._json(r)
            elif self.path == "/api/carteira/receber":
                self._json(CARTEIRA.receber(cli))
            elif self.path == "/api/carteira/enviar":
                self._json(CARTEIRA.enviar(cli, corpo))
            elif self.path == "/api/carteira/backup":
                self._json(CARTEIRA.backup(cli))
            elif self.path == "/api/sair":
                self._json({"ok": True})
                threading.Thread(target=servidor.shutdown, daemon=True).start()
            else:
                self._json({"erro": "nao encontrado"}, 404)
        except Exception as e:
            self._json({"erro": str(e)}, 500)


servidor.RequestHandlerClass = H


def encerrar():
    parar_mineracao()
    if ESTADO["no_nosso"]:
        cli("stop")
        print("no encerrado.", flush=True)


TEXTOS_PRINCIPAL = [
    ("<small>REDE DE TESTE: as moedas não têm valor</small>", "<small>REDE PRINCIPAL</small>"),
    ("REDE DE TESTE: as moedas não têm valor, mas pratique como se tivessem.", "REDE PRINCIPAL: sem a frase de recuperação não há como recuperar as suas moedas."),
    ("REDE DE TESTE: as moedas não têm valor. Esta carteira", "REDE PRINCIPAL. Esta carteira"),
]


def pagina(html):
    if args.rede == "principal":
        for a, b in TEXTOS_PRINCIPAL:
            html = html.replace(a, b)
    return html


def abrir_janela(url):
    # No Windows abre uma janela de aplicativo (Edge ou Chrome, sem abas nem barra de endereco).
    if os.name == "nt":
        bases = [os.environ.get("ProgramFiles(x86)", ""), os.environ.get("ProgramFiles", ""), os.environ.get("LOCALAPPDATA", "")]
        perfil = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Rubiana", "janela-perfil")
        for b in bases:
            if not b:
                continue
            for rel in (("Microsoft", "Edge", "Application", "msedge.exe"), ("Google", "Chrome", "Application", "chrome.exe")):
                exe = os.path.join(b, *rel)
                if os.path.exists(exe):
                    try:
                        return subprocess.Popen([exe, "--app=" + url, "--user-data-dir=" + perfil, "--no-first-run", "--no-default-browser-check", "--disable-background-mode", "--window-size=1180,860"])
                    except OSError:
                        pass
    webbrowser.open(url)
    return None


def vigiar_janela(proc):
    t0 = time.time()
    proc.wait()
    if time.time() - t0 < 5:
        return
    time.sleep(1)
    servidor.shutdown()


garantir_no()
url = "http://127.0.0.1:%d/?t=%s" % (PORTA, TOKEN)
print("Janela da Rubiana: " + url, flush=True)
print("(a senha no endereco vale so enquanto este programa estiver aberto; Ctrl+C encerra)", flush=True)
if not args.no_browser:
    janela = abrir_janela(url)
    if janela is not None:
        threading.Thread(target=vigiar_janela, args=(janela,), daemon=True).start()
try:
    servidor.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    encerrar()
# fim do rubiana-app.py
