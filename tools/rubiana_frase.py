"""Frase de recuperacao (BIP39, 12 ou 24 palavras) da carteira da Rubiana (v0).
So usa a biblioteca padrao do Python. A frase gera uma chave mestra (BIP32) com os
prefixos de chave da rede; o no recebe os descritores e deriva as chaves."""
import hashlib
import hmac
import os
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
HASH_LISTA = "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"
# Prefixos de chave estendida (os mesmos de chainparams.cpp) e numero de moeda
# do caminho de derivacao (a rede principal usa 8686).
PREFIXOS = {"testnet": bytes([0x04, 0x0D, 0x5A, 0x57]), "regtest": bytes([0x04, 0x0D, 0x5A, 0x57]), "principal": bytes([0x04, 0x0B, 0xEE, 0x6E])}
MOEDA = {"testnet": 1, "regtest": 1, "principal": 8686}
_LISTA = None


def lista():
    global _LISTA
    if _LISTA is None:
        dados = open(os.path.join(AQUI, "bip39-english.txt"), "rb").read()
        if hashlib.sha256(dados).hexdigest() != HASH_LISTA:
            raise RuntimeError("a lista de palavras da frase de recuperacao esta alterada ou corrompida")
        palavras = dados.decode("utf-8").split()
        if len(palavras) != 2048:
            raise RuntimeError("lista de palavras invalida")
        _LISTA = palavras
    return _LISTA


def de_entropia(ent):
    if len(ent) not in (16, 32):
        raise ValueError("a entropia deve ter 16 ou 32 bytes")
    cs = len(ent) * 8 // 32
    valor = (int.from_bytes(ent, "big") << cs) | (hashlib.sha256(ent).digest()[0] >> (8 - cs))
    n = (len(ent) * 8 + cs) // 11
    p = lista()
    return " ".join(p[(valor >> (11 * (n - 1 - i))) & 0x7FF] for i in range(n))


def gerar(n=12):
    if n not in (12, 24):
        raise ValueError("use 12 ou 24 palavras")
    return de_entropia(os.urandom(16 if n == 12 else 32))


def normalizar(frase):
    return " ".join(unicodedata.normalize("NFKD", frase).lower().split())


def validar(frase):
    """Devolve (True, "") ou (False, motivo)."""
    pal = normalizar(frase).split()
    if len(pal) not in (12, 24):
        return False, "a frase deve ter 12 ou 24 palavras (esta tem %d)" % len(pal)
    indice = {w: i for i, w in enumerate(lista())}
    valor = 0
    for w in pal:
        if w not in indice:
            return False, "palavra desconhecida: " + w[:20]
        valor = (valor << 11) | indice[w]
    total = len(pal) * 11
    cs = total // 33
    ent = (valor >> cs).to_bytes((total - cs) // 8, "big")
    if (hashlib.sha256(ent).digest()[0] >> (8 - cs)) != (valor & ((1 << cs) - 1)):
        return False, "frase invalida: a conferencia final nao bate (alguma palavra esta errada ou fora de ordem)"
    return True, ""


def semente(frase, senha=""):
    sal = "mnemonic" + unicodedata.normalize("NFKD", senha)
    return hashlib.pbkdf2_hmac("sha512", normalizar(frase).encode("utf-8"), sal.encode("utf-8"), 2048)


_B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _b58check(payload):
    dados = payload + hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    n = int.from_bytes(dados, "big")
    s = ""
    while n:
        n, r = divmod(n, 58)
        s = _B58[r] + s
    return "1" * (len(dados) - len(dados.lstrip(b"\0"))) + s


def xprv_mestre(sem, rede, prefixo=None):
    if prefixo is None:
        if rede not in PREFIXOS:
            raise ValueError("a rede '%s' ainda nao esta liberada para frase de recuperacao" % rede)
        prefixo = PREFIXOS[rede]
    i = hmac.new(b"Bitcoin seed", sem, hashlib.sha512).digest()
    k, c = i[:32], i[32:]
    ordem = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    if not (0 < int.from_bytes(k, "big") < ordem):
        raise ValueError("semente invalida (muito improvavel); gere outra frase")
    return _b58check(prefixo + b"\x00" + b"\x00" * 4 + b"\x00" * 4 + c + b"\x00" + k)


def descritores(xprv, rede):
    """Descritores de recebimento e de troco (sem o texto de conferencia '#...')."""
    base = "%s/84h/%dh/0h" % (xprv, MOEDA[rede])
    return ["wpkh(%s/0/*)" % base, "wpkh(%s/1/*)" % base]


def autoteste():
    erros = []

    def conf(nome, obtido, esperado):
        if obtido != esperado:
            erros.append(nome)

    conf("12 palavras (zeros)", de_entropia(bytes(16)), "abandon " * 11 + "about")
    conf("12 palavras (7f)", de_entropia(bytes([0x7F]) * 16), "legal winner thank year wave sausage worth useful legal winner thank yellow")
    conf("12 palavras (ff)", de_entropia(bytes([0xFF]) * 16), "zoo " * 11 + "wrong")
    conf("24 palavras (zeros)", de_entropia(bytes(32)), "abandon " * 23 + "art")
    conf("validar correta", validar("abandon " * 11 + "about")[0], True)
    conf("validar errada", validar("abandon " * 12)[0], False)
    conf("validar tamanho", validar("abandon abandon")[0], False)
    conf("validar gerada 12", validar(gerar(12))[0], True)
    conf("validar gerada 24", validar(gerar(24))[0], True)
    conf("semente BIP39", semente("abandon " * 11 + "about", "TREZOR").hex(),
         "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04")
    conf("chave mestra BIP32", xprv_mestre(bytes.fromhex("000102030405060708090a0b0c0d0e0f"), "bitcoin", bytes([0x04, 0x88, 0xAD, 0xE4])),
         "xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi")
    return erros


if __name__ == "__main__":
    falhas = autoteste()
    if falhas:
        print("FALHOU: " + ", ".join(falhas))
        sys.exit(1)
    print("autoteste ok")
# fim do rubiana_frase.py
