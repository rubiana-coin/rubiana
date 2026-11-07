"""Carteira da Rubiana para a janela do PC (v1, com frase de recuperacao).
Usa o no pelo rubiana-cli, atraves das funcoes cli(...) e cli_stdin(...) da janela.
A frase (12 ou 24 palavras) fica so na memoria durante a criacao e nunca e gravada;
a chave vai ao no pela entrada padrao, e nao pela linha de comando."""
import json
import re
import secrets
import threading
import time

import rubiana_frase as FRASE

NOME = "rubiana"
RE_END = re.compile(r"[0-9a-z]{20,100}")
RE_VAL = re.compile(r"[0-9]{1,8}(\.[0-9]{1,8})?")
RE_TAXA = re.compile(r"[0-9]{1,3}(\.[0-9]{1,2})?")
VALIDADE = 15 * 60
TRAVA = threading.Lock()
PENDENTE = {}


def _json(txt):
    try:
        return json.loads(txt)
    except (TypeError, ValueError):
        return None


def _limpar(txt):
    # Nunca deixa uma chave aparecer em mensagens de erro.
    return re.sub(r"[1-9A-HJ-NP-Za-km-z]{80,}", "***", str(txt))


def estado(cli):
    code, out = cli("listwalletdir")
    if code != 0:
        return {"estado": "sem_no"}
    nomes = [w.get("name") for w in (_json(out) or {}).get("wallets", [])]
    if NOME not in nomes:
        return {"estado": "sem_carteira"}
    cli("loadwallet", NOME)
    code, out = cli("listdescriptors", wallet=True)
    d = _json(out) if code == 0 else None
    if d and d.get("descriptors"):
        return {"estado": "pronta"}
    return {"estado": "sem_carteira"}


def garantir(cli):
    return estado(cli)["estado"] == "pronta"


def _coins(x):
    return "%.8f" % float(x)


def resumo(cli):
    code, out = cli("getbalances", wallet=True)
    if code != 0:
        return {"erro": out}
    m = json.loads(out)["mine"]
    return {"disponivel": _coins(m["trusted"]), "pendente": _coins(m["untrusted_pending"]),
            "amadurecendo": _coins(m["immature"])}


def historico(cli, n=20):
    code, out = cli("listtransactions", "*", n, wallet=True)
    if code != 0:
        return {"erro": out}
    itens = []
    for t in reversed(json.loads(out)):
        itens.append({"tipo": t.get("category"), "valor": _coins(t.get("amount", 0)),
                      "conf": t.get("confirmations", 0), "txid": t.get("txid"), "data": t.get("time")})
    return {"itens": itens}


def receber(cli):
    code, out = cli("getnewaddress", wallet=True)
    if code != 0:
        return {"erro": out}
    return {"endereco": out}


def enviar(cli, corpo):
    end = str(corpo.get("endereco", "")).strip().lower()
    val = str(corpo.get("valor", "")).strip().replace(",", ".")
    taxa = str(corpo.get("taxa", "1")).strip().replace(",", ".") or "1"
    if not RE_END.fullmatch(end):
        return {"erro": "endereco com formato invalido"}
    if not RE_VAL.fullmatch(val) or float(val) <= 0:
        return {"erro": "valor invalido (use numeros, ate 8 casas decimais)"}
    if not RE_TAXA.fullmatch(taxa) or not (1 <= float(taxa) <= 100):
        return {"erro": "taxa invalida (use um numero entre 1 e 100)"}
    code, out = cli("validateaddress", end)
    if code != 0 or not json.loads(out).get("isvalid"):
        return {"erro": "endereco invalido nesta rede"}
    code, out = cli("-named", "sendtoaddress", "address=" + end, "amount=" + val, "fee_rate=" + taxa, wallet=True)
    if code != 0:
        return {"erro": out}
    return {"ok": True, "txid": out}


def backup(cli):
    import os
    pasta = os.path.join(os.path.expanduser("~"), ".rubiana", "backups")
    os.makedirs(pasta, exist_ok=True)
    destino = os.path.join(pasta, "carteira-%s-%s.dat" % (NOME, time.strftime("%Y%m%d-%H%M%S")))
    code, out = cli("backupwallet", destino, wallet=True)
    if code != 0:
        return {"erro": out}
    return {"ok": True, "arquivo": destino}


def frase_nova(corpo):
    try:
        n = int(corpo.get("palavras", 12))
    except (TypeError, ValueError):
        return {"erro": "numero de palavras invalido"}
    if n not in (12, 24):
        return {"erro": "escolha 12 ou 24 palavras"}
    with TRAVA:
        frase = FRASE.gerar(n)
        pedir = sorted(secrets.SystemRandom().sample(range(n), 3))
        PENDENTE.clear()
        PENDENTE.update({"frase": frase, "pedir": pedir, "t": time.time()})
    return {"palavras": frase.split(), "pedir": [p + 1 for p in pedir]}


def frase_confirmar(cli, cli_stdin, corpo, rede):
    with TRAVA:
        if not PENDENTE or time.time() - PENDENTE["t"] > VALIDADE:
            PENDENTE.clear()
            return {"erro": "A frase expirou ou nao foi gerada. Gere uma nova."}
        pal = PENDENTE["frase"].split()
        resp = corpo.get("respostas") or {}
        for pos in PENDENTE["pedir"]:
            if str(resp.get(str(pos + 1), "")).strip().lower() != pal[pos]:
                return {"erro": "As palavras nao conferem. Olhe a sua anotacao e tente de novo."}
        r = _criar(cli, cli_stdin, PENDENTE["frase"], rede, "now")
        if r.get("ok"):
            PENDENTE.clear()
        return r


def frase_restaurar(cli, cli_stdin, corpo, rede):
    frase = str(corpo.get("frase", ""))
    ok, motivo = FRASE.validar(frase)
    if not ok:
        return {"erro": motivo}
    with TRAVA:
        return _criar(cli, cli_stdin, FRASE.normalizar(frase), rede, 0)


def _criar(cli, cli_stdin, frase, rede, timestamp):
    try:
        xprv = FRASE.xprv_mestre(FRASE.semente(frase), rede)
        descs = FRASE.descritores(xprv, rede)
    except ValueError as e:
        return {"erro": str(e)}
    if estado(cli)["estado"] == "pronta":
        return {"erro": "Ja existe uma carteira Rubiana neste computador."}
    pedidos = []
    for i, d in enumerate(descs):
        code, out = cli_stdin(["getdescriptorinfo"], [d])
        info = _json(out) if code == 0 else None
        if not info or "checksum" not in info:
            return {"erro": "O no recusou a chave gerada: " + _limpar(out)[:200]}
        pedidos.append({"desc": d + "#" + info["checksum"], "timestamp": timestamp, "active": True,
                        "internal": i == 1, "range": [0, 999]})
    code, out = cli("listwalletdir")
    dados = _json(out) if code == 0 else None
    if dados is None:
        return {"erro": "O no ainda nao esta pronto. Tente de novo em instantes."}
    if NOME in [w.get("name") for w in dados.get("wallets", [])]:
        cli("loadwallet", NOME)
    else:
        code, out = cli("-named", "createwallet", "wallet_name=" + NOME, "blank=true", "load_on_startup=true")
        if code != 0:
            return {"erro": "Nao consegui criar a carteira: " + _limpar(out)[:200]}
    code, out = cli_stdin(["importdescriptors"], [json.dumps(pedidos, separators=(",", ":"))], wallet=True, timeout=7200)
    res = _json(out) if code == 0 else None
    if not isinstance(res, list) or not res or not all(x.get("success") for x in res):
        return {"erro": "Nao consegui importar a frase: " + _limpar(out)[:300]}
    return {"ok": True}


PAGE = r"""<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:system-ui,sans-serif;margin:0;background:#0f1220;color:#e8eaf6}
h3{margin:0 0 8px 0;font-size:15px}
button{padding:8px 14px;border:0;border-radius:6px;background:#7c4dff;color:#fff;cursor:pointer;margin:4px 6px 4px 0}
button.sec{background:#2a2f50}
input,textarea{padding:7px;border-radius:6px;border:0;margin:4px 8px 8px 0}
label{display:inline-block;margin-right:14px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;padding:10px 14px}
.grade{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;margin:10px 0}
.card{background:#1a1f3a;border-radius:10px;padding:10px}
.card b{display:block;font-size:11px;color:#9fa8da;font-weight:normal}
.card span{font-size:17px}
.box{background:#1a1f3a;border-radius:10px;padding:12px;margin:10px 14px}
.aviso{color:#ffcc80;font-size:13px}
.mono{font-family:monospace;word-break:break-all}
table{width:100%;border-collapse:collapse;font-size:13px}
td,th{padding:6px;border-bottom:1px solid #2a2f50;text-align:left}
</style></head><body>
<div id="aguarde" class="box">Carregando a carteira... (se o nó ainda estiver iniciando, aguarde alguns segundos)</div>
<div id="setup" style="display:none"><div class="box">
<h3>Crie a sua carteira</h3>
<p class="aviso">REDE DE TESTE: as moedas não têm valor, mas pratique como se tivessem.</p>
<p>A <b>frase de recuperação</b> é a única forma de recuperar as suas moedas se o computador quebrar, for formatado ou o arquivo da carteira se perder. <b>Quem tiver a frase controla as moedas</b>: nunca a mostre a ninguém e nunca a digite em sites. Anote no papel, na ordem, e guarde em lugar seguro. Não tire foto e não salve no computador.</p>
<div id="s1">
<label><input type="radio" name="n" value="12" checked> 12 palavras (recomendado)</label>
<label><input type="radio" name="n" value="24"> 24 palavras (mais longa)</label><br>
<button onclick="gerar()">Criar carteira nova</button>
<button class="sec" onclick="passo('sr')">Já tenho uma frase (restaurar)</button>
</div>
<div id="s2" style="display:none">
<p class="aviso">Anote as palavras na ordem, com o número de cada uma. Elas só aparecem agora.</p>
<div class="grade" id="grade"></div>
<button onclick="anotei()">Já anotei</button>
<button class="sec" onclick="passo('s1')">Cancelar</button>
</div>
<div id="s3" style="display:none">
<p>Para conferir, digite as palavras pedidas:</p>
<div id="pedidos"></div>
<button onclick="confirmar()">Confirmar e criar a carteira</button>
<button class="sec" onclick="voltar()">Ver as palavras de novo</button>
<span id="msg3"></span>
</div>
<div id="sr" style="display:none">
<p>Digite as palavras da sua frase (12 ou 24), separadas por espaço.</p>
<textarea id="frase" rows="3" cols="60" autocomplete="off" spellcheck="false"></textarea><br>
<button onclick="restaurar()">Restaurar carteira</button>
<button class="sec" onclick="passo('s1')">Voltar</button>
<span id="msgr"></span>
</div>
</div></div>
<div id="principal" style="display:none">
<div class="box aviso">REDE DE TESTE: as moedas não têm valor. Esta carteira é protegida pela frase de recuperação que você anotou: guarde-a em lugar seguro, porque quem a tiver controla as moedas. O arquivo da carteira neste computador não tem senha.</div>
<div class="cards" id="cards"></div>
<div class="box"><h3>Receber</h3>
<button onclick="receber()">Gerar novo endereço</button>
<p class="aviso">Use um endereço novo a cada recebimento.</p>
<div id="rec"></div></div>
<div class="box"><h3>Enviar</h3>
<label>Endereço<br><input id="e" size="58"></label><br>
<label>Valor (RUBIA)<br><input id="v" size="14"></label>
<label>Taxa (sat/vB)<br><input id="t" size="6" value="1"></label><br>
<button onclick="enviar()">Enviar</button> <span id="env"></span></div>
<div class="box"><h3>Histórico (últimas 20)</h3><table id="hist"></table></div>
<div class="box"><h3>Backup do arquivo (opcional)</h3>
<p class="aviso">Cria uma cópia do arquivo da carteira na pasta .rubiana\backups do seu usuário. A frase de recuperação já é a sua cópia de segurança principal.</p>
<button onclick="backup()">Fazer backup agora</button> <span id="bk"></span></div>
</div>
<script>
const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function api(u,corpo){
  const o=corpo===undefined?{}:{method:'POST',headers:{'X-Rubiana':'1','Content-Type':'application/json'},body:JSON.stringify(corpo)};
  const r=await fetch(u,o);return r.json();
}
const nomes={send:'Enviado',receive:'Recebido',generate:'Minerado',immature:'Minerado (amadurecendo)',orphan:'Órfão'};
const sh=h=>h?h.slice(0,8)+'..'+h.slice(-6):'-';
let palavras=[],pedir=[],visivel='';
function ver(id){['aguarde','setup','principal'].forEach(x=>$('#'+x).style.display=x===id?'':'none');visivel=id}
function passo(id){['s1','s2','s3','sr'].forEach(x=>$('#'+x).style.display=x===id?'':'none')}
async function iniciarPagina(){
  let r;
  try{r=await api('/api/carteira/estado')}catch(e){r={estado:'sem_no'}}
  if(r.estado==='pronta'){ver('principal');atualizar()}
  else if(r.estado==='sem_carteira'){if(visivel!=='setup'){ver('setup');passo('s1')}}
  else{ver('aguarde');setTimeout(iniciarPagina,3000)}
}
function mostrarGrade(){
  $('#grade').innerHTML=palavras.map((w,i)=>'<div class="card"><b>'+(i+1)+'</b><span>'+esc(w)+'</span></div>').join('');
}
async function gerar(){
  const n=document.querySelector('input[name=n]:checked').value;
  const r=await api('/api/carteira/frase/nova',{palavras:parseInt(n)});
  if(r.erro){alert(r.erro);return}
  palavras=r.palavras;pedir=r.pedir;
  mostrarGrade();passo('s2');
}
function anotei(){
  $('#pedidos').innerHTML=pedir.map(p=>'<label>Palavra nº '+p+'<br><input id="w'+p+'" autocomplete="off" size="14"></label>').join('');
  $('#grade').innerHTML='';$('#msg3').textContent='';passo('s3');
}
function voltar(){mostrarGrade();passo('s2')}
async function confirmar(){
  const resp={};pedir.forEach(p=>{resp[p]=$('#w'+p).value.trim().toLowerCase()});
  $('#msg3').textContent=' Criando a carteira... isso pode levar mais de um minuto. Não feche esta janela.';
  const r=await api('/api/carteira/frase/confirmar',{respostas:resp});
  if(r.erro){$('#msg3').textContent=' '+r.erro;return}
  palavras=[];pedir=[];$('#grade').innerHTML='';$('#pedidos').innerHTML='';
  await iniciarPagina();
}
async function restaurar(){
  $('#msgr').textContent=' Restaurando... pode levar alguns minutos. Não feche esta janela.';
  const r=await api('/api/carteira/frase/restaurar',{frase:$('#frase').value});
  if(r.erro){$('#msgr').textContent=' '+r.erro;return}
  $('#frase').value='';$('#msgr').textContent='';
  await iniciarPagina();
}
async function atualizar(){
  if(visivel!=='principal')return;
  try{
    const r=await api('/api/carteira/resumo');
    if(r.erro){$('#cards').innerHTML='<div class="card"><b>Carteira</b><span>ainda não está pronta</span></div>'}
    else{
      const c=[['Disponível',r.disponivel],['Amadurecendo (mineração, 100 blocos)',r.amadurecendo],['Aguardando confirmação',r.pendente]];
      $('#cards').innerHTML=c.map(x=>'<div class="card"><b>'+x[0]+'</b><span>'+esc(x[1])+'</span></div>').join('');
    }
    const h=await api('/api/carteira/historico');
    if(h.itens){
      $('#hist').innerHTML='<tr><th>Data</th><th>Tipo</th><th>Valor</th><th>Conf.</th><th>Transação</th></tr>'+h.itens.map(t=>'<tr><td>'+(t.data?new Date(t.data*1000).toLocaleString('pt-BR'):'-')+'</td><td>'+esc(nomes[t.tipo]||t.tipo)+'</td><td>'+esc(t.valor)+'</td><td>'+t.conf+'</td><td class="mono">'+esc(sh(t.txid))+'</td></tr>').join('');
    }
  }catch(e){}
}
async function receber(){
  const r=await api('/api/carteira/receber',{});
  if(r.erro){$('#rec').textContent=r.erro;return}
  $('#rec').innerHTML='<b class="mono">'+esc(r.endereco)+'</b> <button onclick="copiar(\''+esc(r.endereco)+'\')">Copiar</button>';
}
async function copiar(t){
  try{await navigator.clipboard.writeText(t)}catch(e){alert('Selecione o endereço com o mouse e copie com Ctrl+C.')}
}
async function enviar(){
  const e=$('#e').value.trim(),v=$('#v').value.trim(),t=$('#t').value.trim()||'1';
  if(!e||!v){$('#env').textContent=' Preencha o endereço e o valor.';return}
  if(!confirm('Enviar '+v+' RUBIA para\n'+e+'\ncom taxa de '+t+' sat/vB?\nEsta ação não pode ser desfeita.'))return;
  $('#env').textContent=' Enviando...';
  const r=await api('/api/carteira/enviar',{endereco:e,valor:v,taxa:t});
  $('#env').textContent=r.erro?(' Erro: '+r.erro):(' Enviado! Transação: '+r.txid);
  if(!r.erro){$('#v').value=''}
  atualizar();
}
async function backup(){
  const r=await api('/api/carteira/backup',{});
  $('#bk').textContent=r.erro?(' Erro: '+r.erro):(' Backup salvo em: '+r.arquivo);
}
setInterval(atualizar,5000);iniciarPagina();
</script></body></html>"""
# fim do rubiana_carteira.py
