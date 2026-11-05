"""Carteira da Rubiana para a janela do PC (v0).
Usa o no pelo rubiana-cli, atraves da funcao cli(*args, wallet=False) da janela."""
import json
import os
import re
import time

NOME = "minerador"
RE_END = re.compile(r"[0-9a-z]{20,100}")
RE_VAL = re.compile(r"[0-9]{1,8}(\.[0-9]{1,8})?")
RE_TAXA = re.compile(r"[0-9]{1,3}(\.[0-9]{1,2})?")


def garantir(cli):
    code, out = cli("loadwallet", NOME)
    if code != 0 and "already loaded" not in out.lower():
        code, out = cli("createwallet", NOME)
    return code == 0


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
    pasta = os.path.join(os.path.expanduser("~"), ".rubiana", "backups")
    os.makedirs(pasta, exist_ok=True)
    destino = os.path.join(pasta, "carteira-%s-%s.dat" % (NOME, time.strftime("%Y%m%d-%H%M%S")))
    code, out = cli("backupwallet", destino, wallet=True)
    if code != 0:
        return {"erro": out}
    return {"ok": True, "arquivo": destino}


PAGE = r"""<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:system-ui,sans-serif;margin:0;background:#0f1220;color:#e8eaf6}
h3{margin:0 0 8px 0;font-size:15px}
button{padding:8px 14px;border:0;border-radius:6px;background:#7c4dff;color:#fff;cursor:pointer}
input{padding:7px;border-radius:6px;border:0;margin:4px 8px 8px 0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;padding:10px 14px}
.card{background:#1a1f3a;border-radius:10px;padding:10px}
.card b{display:block;font-size:11px;color:#9fa8da;font-weight:normal}
.card span{font-size:17px}
.box{background:#1a1f3a;border-radius:10px;padding:12px;margin:10px 14px}
.aviso{color:#ffcc80;font-size:13px}
.mono{font-family:monospace;word-break:break-all}
table{width:100%;border-collapse:collapse;font-size:13px}
td,th{padding:6px;border-bottom:1px solid #2a2f50;text-align:left}
</style></head><body>
<div class="box aviso">REDE DE TESTE: as moedas não têm valor. Esta versão de teste guarda a carteira em um arquivo neste computador, <b>sem senha</b>. Quem tiver o arquivo mexe nas moedas. Faça backup (botão no fim da página) e guarde a cópia em outro lugar.</div>
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
<div class="box"><h3>Backup</h3>
<p class="aviso">Cria uma cópia do arquivo da carteira na pasta .rubiana\backups do seu usuário. Copie esse arquivo para um pendrive ou outro lugar seguro.</p>
<button onclick="backup()">Fazer backup agora</button> <span id="bk"></span></div>
<script>
const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function api(u,corpo){
  const o=corpo===undefined?{}:{method:'POST',headers:{'X-Rubiana':'1','Content-Type':'application/json'},body:JSON.stringify(corpo)};
  const r=await fetch(u,o);return r.json();
}
const nomes={send:'Enviado',receive:'Recebido',generate:'Minerado',immature:'Minerado (amadurecendo)',orphan:'Órfão'};
const sh=h=>h?h.slice(0,8)+'..'+h.slice(-6):'-';
async function atualizar(){
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
setInterval(atualizar,5000);atualizar();
</script></body></html>"""
# fim do rubiana_carteira.py
