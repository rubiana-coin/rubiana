# Segurança / Security

A Rubiana é software EXPERIMENTAL. A rede principal ainda não foi lançada e as moedas da rede de teste não têm valor.
Rubiana is EXPERIMENTAL software. The main network has not launched yet and test-network coins have no value.

## Como relatar uma vulnerabilidade / How to report

Use o relato privado do GitHub: aba **Security** do repositório, botão **Report a vulnerability**.
Não abra uma issue pública para falhas de segurança, e não divulgue falhas de consenso (que dividem a rede ou criam moedas) antes de existir uma correção.

Please use GitHub's private vulnerability reporting (Security tab, **Report a vulnerability**).
Do not open public issues for security bugs, and do not disclose consensus bugs before a fix exists.

## O que nos interessa / Scope

- Falhas de consenso: divisão da cadeia, criação indevida de moedas, validação diferente entre sistemas (Linux, Windows, ARM).
- Integração do RandomX (`src/pow.cpp`): hash incorreto, uso excessivo de memória, chave da época.
- Carteira: perda ou vazamento de chaves.
- Rede: travar ou derrubar nós remotamente.

## O que esperar / What to expect

O projeto é mantido por voluntários. Respondemos em base de melhor esforço, não há programa de recompensas por enquanto, e damos crédito a quem quiser.
The project is volunteer-run. Replies are best-effort, there is no bug bounty for now, and we credit reporters who wish it.

## Poder do criador / Creator's power

Não existem chaves especiais, pontos de verificação ou interruptores no código. Mudanças dependem de quem roda os nós.
There are no special keys, checkpoints or kill switches in the code. Changes depend on the people running nodes.

## Código herdado / Inherited code

Falhas que também afetem o Bitcoin Core devem ser reportadas ao projeto Bitcoin Core pelos canais oficiais dele.
Issues that also affect Bitcoin Core should be reported to the Bitcoin Core project through its official channels.
