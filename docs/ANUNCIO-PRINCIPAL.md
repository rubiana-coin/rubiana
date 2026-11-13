# RASCUNHO. Nao publicar antes do checklist no final deste arquivo.

## Rubiana: a rede principal comeca em 12/12/2026, 15:00 UTC

A Rubiana e uma moeda digital experimental, de codigo aberto, derivada do Bitcoin Core, com mineracao RandomX feita para computadores comuns e, no futuro, celulares. A ideia: as mesmas regras de sempre, para qualquer pessoa poder minerar.

**Regras:** 86 moedas por bloco, halving a cada 500 mil blocos, um bloco a cada 5 minutos, no maximo 86 milhoes de moedas. Sem ICO, sem venda, sem pre-mineracao, sem promessas de ganho. O criador minera como qualquer outra pessoa, a partir do mesmo bloco inicial. Nao ha empresa, fundacao nem dono da rede: quem quiser pode copiar o codigo e rodar a propria versao.

**Bloco inicial (para conferir):** hora 1797087600 (12/12/2026, 15:00:00 UTC, 12:00 em Brasilia), nonce 161, hash bbbc5c41c749213b84e0d846aafa18720144dff411b87c122ac48d1715fb4677. Mensagem gravada nele: CNN 30/Oct/2026 Hackers just stole $6 billion in crypto | Not your keys, not your coins.

**O que existe:** pacote de Windows de clique duplo, com uma janela no navegador (minerar, carteira com frase de recuperacao de 12 ou 24 palavras e explorador de blocos), mineracao solo, nos de entrada. **O que NAO existe ainda:** aplicativo de celular (vem logo depois do lancamento), pools publicas, explorador publico, auditoria externa, programa assinado digitalmente.

**Como participar:** Windows: [LINK DA RELEASE]. Confira o SHA-256 do .zip em SHA256SUMS.txt. Linux: veja o README para compilar.

**Estado dos testes (sem maquiagem):** 26 das 157 suites de testes unitarios herdadas do Bitcoin Core falham. A maioria confere valores do Bitcoin que a Rubiana mudou de proposito, e 3 ainda estao em investigacao. A lista completa esta em docs/TESTES.md. O guia para quem quer revisar o codigo esta em docs/REVISAO.md.

**Avisos:**
- Esta e a rede real, mas o software e experimental e sem auditoria. Nao existe garantia de valor nem de funcionamento.
- Anote a frase de recuperacao da carteira no papel: sem ela nao ha como recuperar as moedas.
- O Windows pode mostrar o aviso azul (SmartScreen) e antivirus podem marcar programas de mineracao como suspeitos.
- O seu endereco IP fica visivel aos nos aos quais voce conecta.
- Nao minere em computador de terceiros ou do trabalho sem permissao.

**Contato:** issues no GitHub. Vulnerabilidades: relato privado (aba Security).

---

## Rubiana: main network starts on 12 Dec 2026, 15:00 UTC

Rubiana is an experimental, open source digital currency derived from Bitcoin Core, with RandomX mining built for ordinary computers and, later, phones. Same rules as always, so anyone can mine.

**Rules:** 86 coins per block, halving every 500,000 blocks, one block every 5 minutes, at most 86 million coins. No ICO, no sale, no premine, no promises of profit. The creator mines like everyone else, from the same first block. There is no company, foundation or owner of the network: anyone can copy the code and run their own version.

**Genesis block (to verify):** time 1797087600 (12 Dec 2026, 15:00:00 UTC), nonce 161, hash bbbc5c41c749213b84e0d846aafa18720144dff411b87c122ac48d1715fb4677. Message embedded in it: CNN 30/Oct/2026 Hackers just stole $6 billion in crypto | Not your keys, not your coins.

**What exists:** one-click Windows package with a browser window (mining, wallet with a 12 or 24 word recovery phrase, block explorer), solo mining, entry nodes. **What does not exist yet:** phone app (coming soon after launch), public pools, public explorer, external audit, digitally signed program.

**How to join:** Windows: [RELEASE LINK]. Check the .zip SHA-256 in SHA256SUMS.txt. Linux: see the README to build.

**Test status (no sugar-coating):** 26 of the 157 unit test suites inherited from Bitcoin Core fail. Most check Bitcoin values that Rubiana changed on purpose, and 3 are still under investigation. The full list is in docs/TESTES.md. The guide for code reviewers is docs/REVISAO.md.

**Warnings:**
- This is the real network, but the software is experimental and unaudited. There is no guarantee of value or of correct operation.
- Write your wallet recovery phrase on paper: without it the coins cannot be recovered.
- Windows may show the blue SmartScreen warning and antivirus may flag mining programs.
- Your IP address is visible to the nodes you connect to.
- Do not mine on computers that are not yours or your workplace's without permission.

**Contact:** GitHub issues. Vulnerabilities: private report (Security tab).

---

## Checklist antes de publicar

- [ ] NOS_PRINCIPAL preenchido em tools/rubiana-mine.py (2 nos de entrada da rede principal, porta 8686)
- [ ] Ensaio final da rede principal com dois computadores
- [ ] Release da rede principal criada, link e SHA-256 conferidos sem login
- [ ] Decidido o que fazer com mineracao antes das 15:00 UTC (ver observacao na conversa)
- [ ] Link da Release no lugar de [LINK DA RELEASE] e [RELEASE LINK]
- [ ] Revisao externa aberta por pelo menos 3 semanas (decisao sua: manter ou nao)
