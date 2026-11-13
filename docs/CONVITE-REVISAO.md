# Convite para revisar o codigo da Rubiana

A Rubiana e um fork do Bitcoin Core com prova de trabalho RandomX, dificuldade LWMA-1 e recompensa de 86 moedas por bloco. A rede principal comeca em 12/12/2026, 15:00 UTC. Nao houve auditoria profissional. Procuramos voluntarios para revisar o codigo antes do lancamento.

Ninguem precisa revisar tudo. Escolha UMA area abaixo e avise abrindo uma issue com o titulo "Revisao: <area>", para nao duplicarmos esforco. De 2 a 4 horas por area ja ajuda. Prazo ideal para os achados: 6/12/2026.

Por onde comecar: docs/REVISAO.md (o que mudou em relacao ao Bitcoin Core e onde pedimos atencao), docs/TESTES.md (estado dos testes) e o README (como compilar).

## O que procurar, por area

1. **Emissao de moedas.** Confirmar 86 moedas por bloco, halving a cada 500.000 blocos, teto de 86.000.000, maturidade de 100 blocos, e que nao ha como criar moedas fora da recompensa do bloco nem pre-mineracao escondida.
2. **Prova de trabalho RandomX.** Chave trocada a cada 2 dias, verificacao do cabecalho, modo leve e modo completo dando o mesmo resultado, custo de verificar (risco de travar nos), troca de epoca e reorganizacoes da cadeia.
3. **Dificuldade LWMA-1.** Comparar com a implementacao de referencia. Casos extremos: primeiros blocos, horarios fora de ordem, estouro de contas, manipulacao de horario, picos de poder de mineracao. Se puder, simule.
4. **Horario e bloco inicial.** Regra de 10 minutos para blocos "do futuro" (o Bitcoin usa 2 horas), excecao do bloco inicial, e se rede principal e rede de teste nao se confundem (portas, bytes magicos, prefixos de endereco rubia e trubia).
5. **Carteira e programa de Windows.** Onde as pessoas podem perder dinheiro: geracao da frase de 12 ou 24 palavras (aleatoriedade, soma de verificacao, derivacao), se a frase vai parar em arquivo ou log, seguranca da janela local (127.0.0.1, senha na URL) e dos arquivos .bat.
6. **Testes.** Rodar e comparar com docs/TESTES.md. Investigar as 3 suites que ainda falham sem explicacao.

## O que conta como achado

Criar ou roubar moedas, travar ou derrubar nos pela rede, dividir a rede, manipular a dificuldade, perder fundos, vazar a frase de recuperacao.

## Como relatar

Abra uma issue no GitHub (ha um modelo pronto). Falhas graves: aba Security, "Report a vulnerability" (relato privado). Todo achado sera respondido no proprio GitHub, mesmo quando decidirmos nao mudar nada. Quem ajudar sera creditado, se quiser.

---

# Call for code reviewers: Rubiana

Rubiana is a Bitcoin Core fork with RandomX proof of work, LWMA-1 difficulty and a 86-coin block reward. The main network starts on 12 Dec 2026, 15:00 UTC. There has been no professional audit. We are looking for volunteers to review the code before launch.

Nobody has to review everything. Pick ONE area below and say so by opening an issue titled "Review: <area>" so we do not duplicate effort. 2 to 4 hours per area already helps. Ideal deadline for findings: 6 Dec 2026.

Start here: docs/REVISAO.md (what changed from Bitcoin Core and where we want attention), docs/TESTES.md (test status) and the README (how to build).

## What to look for, by area

1. **Coin issuance.** Confirm 86 coins per block, halving every 500,000 blocks, 86,000,000 cap, 100-block maturity, and that coins cannot be created outside the block reward and there is no hidden premine.
2. **RandomX proof of work.** Key changes every 2 days, header verification, light and full mode giving the same result, verification cost (node DoS risk), epoch changes and reorgs.
3. **LWMA-1 difficulty.** Compare with the reference implementation. Edge cases: first blocks, out-of-order timestamps, overflow, timestamp manipulation, hashrate spikes. Simulate if you can.
4. **Time and genesis block.** The 10-minute future-block rule (Bitcoin uses 2 hours), the genesis block exception, and whether main and test networks can be confused (ports, magic bytes, address prefixes rubia and trubia).
5. **Wallet and Windows app.** Where people can lose money: 12 or 24 word phrase generation (randomness, checksum, derivation), whether the phrase ends up in files or logs, security of the local window (127.0.0.1, token in the URL) and of the .bat files.
6. **Tests.** Run them and compare with docs/TESTES.md. Investigate the 3 suites still failing without explanation.

## What counts as a finding

Creating or stealing coins, crashing nodes remotely, splitting the network, manipulating difficulty, losing funds, leaking the recovery phrase.

## How to report

Open a GitHub issue (a template is ready). Serious flaws: Security tab, "Report a vulnerability" (private). Every finding gets an answer on GitHub, even when we decide not to change anything. Contributors are credited if they wish.
