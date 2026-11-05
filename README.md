# Rubiana

Moeda digital experimental, de código aberto, derivada do Bitcoin Core, com mineração por prova de trabalho (RandomX) pensada para computadores comuns e, no futuro, celulares.

**STATUS: rede de teste em preparação.** A rede principal (mainnet) ainda NÃO foi lançada. As moedas da rede de teste não têm valor. Software experimental, sem garantias.

## Parâmetros

| | |
|---|---|
| Prova de trabalho | RandomX (a chave muda a cada 2 dias) |
| Tempo entre blocos | 5 minutos |
| Dificuldade | ajustada a cada bloco (LWMA, janela de 60 blocos) |
| Recompensa inicial | 86 moedas por bloco |
| Halving | a cada 500.000 blocos (cerca de 4,8 anos) |
| Total de moedas | 86.000.000 |
| Endereços | começam com `rubia1` (rede de teste: `trubia1`) |
| Portas | P2P 8686 (teste: 18686), RPC 8690 (teste: 18690) |

## Princípios

- Código aberto e regras iguais para todos.
- Sem ICO, sem venda de moedas, sem pré-mineração, sem marketing.
- O criador não tem chaves especiais, pontos de verificação nem interruptores no código. Pool, explorador e nós de entrada devem poder ser substituídos por qualquer pessoa.
- Nenhuma promessa de ganho ou de valor.

## Como testar

**Windows:** um pacote de clique duplo (`minerar.bat`), que será publicado na página de Releases.

**Linux (compilando):**

    sudo apt-get install build-essential cmake pkgconf python3 libevent-dev libboost-dev libsqlite3-dev
    cmake -B build -DCMAKE_BUILD_TYPE=Release -DENABLE_IPC=OFF
    cmake --build build -j $(nproc) --target bitcoind bitcoin-cli
    g++ -O2 -std=c++17 -o build/bin/rubiana-miner tools/rubiana-miner.cpp -I src/randomx/src $(find build -name librandomx.a | head -1) -lpthread
    python3 tools/rubiana-mine.py

## Plano

Primeiro computadores (Windows e Linux), depois um aplicativo de celular com minerador, carteira e explorador. O celular é o objetivo da moeda e vem logo em seguida.

## Segurança

Veja [SECURITY.md](SECURITY.md). Quer ajudar com um nó de entrada? Veja [docs/NO-DE-ENTRADA.md](docs/NO-DE-ENTRADA.md).

## In English

Rubiana is an experimental open-source cryptocurrency forked from Bitcoin Core, using RandomX proof of work so that ordinary computers (and later phones) can mine. 5-minute blocks, 86 coins per block, halving every 500,000 blocks, 86,000,000 maximum supply, per-block difficulty adjustment (LWMA). No ICO, no premine, no special keys for the creator. **The main network has not launched; test-network coins have no value; no warranties.**

## Créditos e licença / Credits and license

Licença MIT (veja COPYING). Baseada no Bitcoin Core (The Bitcoin Core developers) e usa o RandomX (BSD 3-Clause). Projeto independente, sem vínculo com o Bitcoin Core.
MIT license. Based on Bitcoin Core and uses RandomX (BSD 3-Clause). Independent project, not affiliated with Bitcoin Core.
