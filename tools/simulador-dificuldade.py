#!/usr/bin/env python3
"""Simulador da dificuldade da Rubiana (LWMA-1). Nao altera nada do projeto.
Uso: python3 tools/simulador-dificuldade.py"""
import random

T = 300                  # segundos por bloco (alvo)
N = 60                   # janela do LWMA
DIA = 24 * 3600
P_LIMITE = 1.0 / 256     # dificuldade minima permitida (powLimit)

# classe, quantidade, H/s de cada um (modo leve; PC forte = modo completo)
CENARIOS = {
    "1 PC forte sozinho": [("forte", 1, 5000)],
    "1 PC forte + 10 medios + 30 celulares": [("forte", 1, 5000), ("medio", 10, 300), ("celular", 30, 30)],
    "10 medios + 50 celulares (sem PC forte)": [("medio", 10, 300), ("celular", 50, 30)],
    "comeco fraco: 5 PCs em modo leve + 10 celulares": [("leve", 5, 66), ("celular", 10, 30)],
}
PARTIDAS = [16384, 65536, 262144, 1048576]   # tentativas esperadas por bloco
VARIANTES = ("atual", "janela-cresce")


def lwma(ps, ts, variante):
    h = len(ts) - 1
    n = N
    if h < N:
        if variante == "atual" or h < 5:
            return ps[-1]
        n = h
    k = n * (n + 1) * T / 2
    anterior = ts[h - n]
    t = 0.0
    soma = 0.0
    for j in range(1, n + 1):
        i = h - n + j
        este = ts[i] if ts[i] > anterior else anterior + 1
        solve = min(6 * T, este - anterior)
        anterior = este
        t += solve * j
        soma += ps[i] / n
    t = max(t, n * n * T / 20)
    return min(P_LIMITE, soma / k * t)


def simular(miners, D0, variante, seed):
    rnd = random.Random(seed)
    classes, taxas = [], []
    for classe, qtd, hs in miners:
        classes += [classe] * qtd
        taxas += [hs] * qtd
    total = sum(taxas)
    ps, ts, venc = [1.0 / D0], [0], []
    agora = 0.0
    while True:
        p = lwma(ps, ts, variante)
        agora += rnd.expovariate(total * p)
        if agora > DIA:
            break
        quem = rnd.choices(range(len(taxas)), weights=taxas)[0]
        ps.append(p)
        ts.append(int(agora))
        venc.append(classes[quem])
    return ts, venc


def main():
    for nome, miners in CENARIOS.items():
        total = sum(q * hs for _, q, hs in miners)
        print("\n=== " + nome + " ===")
        print("poder total: " + str(total) + " H/s | blocos ideais em 24 h: " + str(DIA // T))
        print(f"{'partida':>9} {'ajuste':<14} {'blocos 1h':>10} {'blocos 24h':>11} {'60 primeiros (min)':>19}")
        for D0 in PARTIDAS:
            for var in VARIANTES:
                runs = [simular(miners, D0, var, s) for s in range(20)]
                b1 = sum(sum(1 for t in ts[1:] if t <= 3600) for ts, _ in runs) / len(runs)
                b24 = sum(len(ts) - 1 for ts, _ in runs) / len(runs)
                m60 = sum((ts[60] / 60 if len(ts) > 60 else DIA / 60) for ts, _ in runs) / len(runs)
                print(f"{D0:>9} {var:<14} {b1:>10.0f} {b24:>11.0f} {m60:>19.1f}")
        runs = [simular(miners, 65536, "janela-cresce", s) for s in range(20)]
        cont, tot = {}, 0
        for _, venc in runs:
            for c in venc:
                cont[c] = cont.get(c, 0) + 1
                tot += 1
        print("participacao nos blocos (partida 65536, janela-cresce) x participacao no poder:")
        for classe, qtd, hs in miners:
            print("  " + classe + ": " + format(100.0 * cont.get(classe, 0) / max(tot, 1), ".1f")
                  + "% dos blocos | " + format(100.0 * qtd * hs / total, ".1f") + "% do poder")


main()
