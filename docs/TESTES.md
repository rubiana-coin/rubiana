# Testes unitários: situação conhecida

Os testes unitários vêm do Bitcoin Core. Em 06/11/2026, no GitHub Actions (workflow "Testes unitarios", uma suíte por vez), 131 das 157 suítes passavam e 26 falhavam. Esta página lista cada uma das 26, com o motivo e o quanto já foi confirmado.

Como rodar: Actions, Testes unitarios, Run workflow. O campo "Suites a rodar" aceita uma lista separada por espaço (vazio = todas). O resultado fica no arquivo resumo.txt, dentro do artefato logs-testes.

## Valores fixos do Bitcoin (esperado)
bip32_tests, bip328_tests, bip352_tests, bloom_tests, descriptor_tests, key_io_tests, key_tests, psbt_wallet_tests, rpc_tests, script_standard_tests, util_tests, walletload_tests.
Os vetores de teste usam chaves, endereços (bc1, 1..., 3...) e prefixos do Bitcoin. A Rubiana usa outros prefixos (endereços rubia1 e trubia1, chaves estendidas próprias).

## Identidade da rede (esperado)
argsman_tests e testnet4_miner_tests (a testnet4 foi removida), bip324_tests (bytes de identificação da rede), net_peer_connection_tests (espera a porta 8333).

## Regras da Rubiana (esperado: os testes conferem regras do Bitcoin)
pow_tests (dificuldade LWMA-1 em vez do reajuste do Bitcoin), validation_tests (recompensa de 86 moedas e halving a cada 500 mil blocos), rescan_tests, spend_tests e wallet_tests (valores calculados com a recompensa de 50 moedas), transaction_tests (o teto de 86 milhões torna válidas transações que o Bitcoin considera inválidas).
txpackage_tests: causa provável semelhante (valores de dinheiro), ainda não confirmada.

## Em investigação
miner_tests (trava depois de trocar o hash dos geradores de bloco pelo RandomX; causa ainda desconhecida), validation_chainstate_tests e validation_chainstatemanager_tests (criam um retrato do conjunto de moedas, recurso assumeutxo que a Rubiana não usa; provavelmente dados fixos do Bitcoin).

## O que já foi corrigido
Os geradores de bloco dos testes usavam o hash do Bitcoin; agora usam o RandomX, como o nó. Isso fez 15 suítes passarem de falha para sucesso.
