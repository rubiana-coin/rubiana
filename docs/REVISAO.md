# Guia para quem vai revisar o código

A Rubiana é um fork do Bitcoin Core: a maior parte do código é a dele, e o que mudamos está concentrado em poucos lugares. Este guia diz onde olhar.

## Ponto de partida
- Base: Bitcoin Core, ramo principal, commit 924f4c4ac7 (16/10/2026, versão de desenvolvimento 32.99).
- Primeiro commit da Rubiana: 3f96d79ec0 (17/10/2026). Todo o histórico do Bitcoin Core continua no repositório.
- Para ver tudo o que mudamos, fora a biblioteca RandomX: `git diff 924f4c4ac7 HEAD -- src ':!src/randomx'`

## O que mudou nas regras de consenso
- **Prova de trabalho:** o hash que vale para a prova de trabalho é o RandomX do cabeçalho do bloco (função `GetPoWHash`, em `src/pow.cpp`). A identidade do bloco continua sendo o hash duplo SHA-256 do cabeçalho. A chave do RandomX troca a cada 2 dias: a época é `nTime / 172800` do cabeçalho, e o texto da chave é `Rubiana-RandomX-v1-<época>`. O nó guarda até 2 chaves em memória (cerca de 275 MB cada, no modo leve) e cada thread tem a sua própria máquina virtual.
- **Onde a prova de trabalho é conferida:** `src/validation.cpp` (conferência do cabeçalho e dos cabeçalhos recebidos), `src/node/blockstorage.cpp` (leitura do disco) e `src/rpc/mining.cpp` (geração de blocos de teste).
- **Dificuldade:** LWMA-1 (de Zawy), reajuste a cada bloco, janela de 60 blocos, alvo de 300 segundos por bloco. Nos primeiros 5 blocos a dificuldade é fixa (`nInitialPowBits`); depois a janela cresce até 60. A variação por bloco é limitada. Código: `GetNextWorkRequiredLWMA`, em `src/pow.cpp`. A regtest não reajusta.
- **Recompensa:** 86 moedas por bloco, cortadas pela metade a cada 500.000 blocos (`GetBlockSubsidy`, em `src/validation.cpp`; o intervalo está em `src/kernel/chainparams.cpp`). A maturação da coinbase continua em 100 blocos.
- **Teto de moedas:** 86.000.000 (`MAX_MONEY`, em `src/consensus/amount.h`).
- **Redes:** principal (porta 8686, endereços `rubia1...`), teste (porta 18686, endereços `trubia1...`) e regtest. As redes signet e testnet4 do Bitcoin Core continuam no código, mas bloqueadas na seleção.
- **Bloco inicial da rede principal:** hora 1797087600 (12/12/2026, 15:00 UTC), nonce 161, hash `bbbc5c41c749213b84e0d846aafa18720144dff411b87c122ac48d1715fb4677`, com uma mensagem gravada no bloco. O nó se recusa a iniciar se o bloco não conferir com o hash fixo no código.
- As regras modernas do Bitcoin (SegWit, Taproot) estão ativas desde o bloco 1.

## Onde pedimos atenção especial
1. Integração do RandomX (`src/pow.cpp`): uso de memória das chaves em cache, segurança entre threads e o custo de conferir cabeçalhos (ataque com cabeçalhos falsos).
2. A troca de chave a cada 2 dias: o que acontece perto da virada, já que a época vem do horário do próprio cabeçalho.
3. LWMA-1: comportamento com horários manipulados e com poucos mineradores, como no começo da rede.
4. O bloco inicial e os parâmetros de cada rede (`src/kernel/chainparams.cpp`).
5. Qualquer valor ou texto do Bitcoin que tenhamos esquecido de trocar.

## Como compilar e testar
- Compilar: veja o README.
- Testes: veja `docs/TESTES.md`. Hoje 26 das 157 suítes de teste falham, e cada uma tem explicação; 3 ainda estão em investigação.

## O que há fora do consenso
A pasta `tools/` tem programas em Python (minerador, pool de teste, janela no navegador, carteira com frase de recuperação, explorador). Eles não fazem parte do consenso.

## Como relatar
- Problemas e revisões: abra uma issue (há modelos para "Relato de teste" e "Revisão de código").
- Vulnerabilidades: use a aba Security, "Report a vulnerability" (relato privado).

## Arquivos que mais mudaram em `src` (sem a biblioteca RandomX)
Mostramos os 40 com mais linhas alteradas (acrescentadas e removidas). A lista completa sai do comando `git diff --numstat` indicado acima.

| Arquivo | Linhas acrescentadas | Linhas removidas |
|---|---|---|
| `src/chainparamsseeds.h` | 0 | 2692 |
| `src/kernel/chainparams.cpp` | 128 | 150 |
| `src/pow.cpp` | 157 | 1 |
| `src/common/args.cpp` | 14 | 9 |
| `src/CMakeLists.txt` | 15 | 0 |
| `src/bitcoin.cpp` | 5 | 5 |
| `src/validation.cpp` | 4 | 4 |
| `src/chainparamsbase.cpp` | 4 | 4 |
| `src/test/util/mining.cpp` | 3 | 3 |
| `src/test/blockencodings_tests.cpp` | 3 | 3 |
| `src/node/blockstorage.cpp` | 3 | 3 |
| `src/test/util/setup_common.cpp` | 2 | 4 |
| `src/test/miner_tests.cpp` | 3 | 2 |
| `src/wallet/walletutil.cpp` | 2 | 2 |
| `src/pow.h` | 2 | 0 |
| `src/consensus/params.h` | 2 | 0 |
| `src/util/threadnames.cpp` | 1 | 1 |
| `src/util/fs_helpers.cpp` | 1 | 1 |
| `src/test/validation_block_tests.cpp` | 1 | 1 |
| `src/test/peerman_tests.cpp` | 1 | 1 |
| `src/test/headers_sync_chainwork_tests.cpp` | 1 | 1 |
| `src/rpc/server.cpp` | 1 | 1 |
| `src/rpc/mining.cpp` | 1 | 1 |
| `src/node/warnings.cpp` | 1 | 1 |
| `src/init.cpp` | 1 | 1 |
| `src/consensus/amount.h` | 1 | 1 |
| `src/clientversion.cpp` | 1 | 1 |

## Biblioteca RandomX
A pasta `src/randomx` é a biblioteca RandomX, código de terceiros incluído no repositório (veja a licença na própria pasta).
