# RASCUNHO. Não publicar antes do checklist no final deste arquivo.

## Convite: ajude a testar a rede de teste da Rubiana

A Rubiana é uma moeda digital experimental, de código aberto, derivada do Bitcoin Core, com mineração RandomX feita para computadores comuns e, no futuro, celulares. Regras iguais para todos: sem ICO, sem venda, sem pré-mineração, sem promessas de ganho. O criador minera como qualquer outro.

**O que existe hoje:** rede de teste pública, pacote de Windows de clique duplo com uma janela no navegador (minerar, carteira com frase de recuperação de 12 ou 24 palavras e explorador de blocos), mineração solo, nó de entrada. **O que NÃO existe ainda:** rede principal, aplicativo de celular (vem logo depois), pools públicas, auditoria externa.

**Como participar:** Windows: https://github.com/rubiana-coin/rubiana/releases/tag/testnet-v0.1. Linux: veja o README para compilar.

**O que queremos saber:** problemas de instalação, avisos de antivírus, travamentos, falhas de sincronização, comportamento da dificuldade, uso de processador e memória, e revisão do código (consenso e RandomX).

**Avisos:**
- As moedas da rede de teste não têm valor, mas anote a frase de recuperação da sua carteira no papel e guarde: sem ela não há como recuperar a carteira.
- O programa não é assinado digitalmente: o Windows pode mostrar o aviso azul do SmartScreen, e antivírus podem marcar programas de mineração como suspeitos.
- O seu endereço IP fica visível ao nó ao qual você se conecta.
- Não minere em computador de terceiros ou do trabalho sem permissão.

**Contato:** issues no GitHub. Vulnerabilidades: relato privado (aba Security).

---

## Invitation: help test the Rubiana test network

Rubiana is an experimental open-source cryptocurrency forked from Bitcoin Core, using RandomX so ordinary computers (and later phones) can mine. Same rules for everyone: no ICO, no sale, no premine, no promises of profit. The creator mines like anyone else.

**Exists today:** public test network, one-click Windows package with a browser window (mining, wallet with a 12 or 24 word recovery phrase, block explorer), solo mining, an entry node. **Does not exist yet:** main network, phone app (coming soon after), public pools, external audit.

**How to join:** Windows: https://github.com/rubiana-coin/rubiana/releases/tag/testnet-v0.1. Linux: see the README to build.

**What we want to hear:** install problems, antivirus warnings, crashes, sync failures, difficulty behaviour, CPU and memory use, and code review (consensus and RandomX).

**Warnings:** test coins have no value (but write down your wallet recovery phrase and keep it safe); the program is unsigned (SmartScreen and antivirus warnings are likely); the node you connect to can see your IP address; do not mine on someone else's or your employer's computer without permission.

**Contact:** GitHub issues. Vulnerabilities: private report (Security tab).

---

## Checklist antes de publicar

- [ ] Release no GitHub com o pacote de Windows e o arquivo de verificação (SHA-256)
- [ ] Relato privado de vulnerabilidades ativado
- [ ] Pelo menos um segundo nó de entrada (de outra pessoa; se ninguém aceitar, no Railway em outra região)
- [ ] Testnet4, signet e regtest limpos no código
- [ ] Teste do pacote em outro computador Windows, de outra pessoa
