# Roteiro futuro da Rubiana (decisões e pendências)

Atualizado em 06/11/2026.

## Decisões já tomadas
- Prova de trabalho RandomX, bloco de 5 minutos, dificuldade LWMA-1, fornecimento máximo de 86 milhões, recompensa inicial de 86 moedas e halving a cada 500 mil blocos.
- Lançamento justo, sem pré-mineração, primeiro só para PC; Android logo depois.
- Dificuldade inicial da rede principal: 262.144 tentativas por bloco (0x1e400000), a aplicar no gênesis definitivo.
- Carteira com frase de recuperação BIP39: 12 palavras por padrão e 24 opcionais (recomendação: 24 para quem guardar valores altos).

## Deixado para o futuro (de propósito)
- PoS híbrido: não implementar agora. Motivos: um limite de stake por endereço é contornável dividindo o saldo em várias carteiras; o PoS ampliaria a vantagem de quem minerou primeiro; é código de consenso grande e arriscado. Reavaliar só se surgir um problema real, por hard fork combinado com a comunidade.
- Criptografia pós-quântica: não implementar agora. Plano em etapas: (1) lançar com assinaturas clássicas, usando um endereço novo a cada recebimento; (2) reservar no consenso uma versão de endereço para assinaturas pós-quânticas; (3) manter a frase de recuperação preparada para derivar chaves novas; (4) ativar por soft fork quando os padrões e as bibliotecas amadurecerem (ML-DSA e SLH-DSA, do NIST).
- O hash e a mineração RandomX são pouco afetados por computadores quânticos; o risco principal está nas assinaturas.

## Pendências antes da rede principal
- Número de moeda do caminho de derivação da carteira (hoje só testnet e regtest).
- Gênesis definitivo, IS_RELEASE, hora de início e texto do anúncio.
- Período de revisão aberta (mínimo de 3 semanas) e ensaio final com dois nós.
- Testes unitários: atualizar ou aposentar os que conferem valores do Bitcoin; investigar miner_tests e validation_chainstate (o transaction_tests é esperado: com o teto de 86 milhões, transações que o Bitcoin considera inválidas passam a ser válidas).
- Segundo nó de entrada (outra região ou outra pessoa).
- Migração do repositório para a conta do projeto.
- Depois do PC: Android (medir o RandomX em ARM), explorador público, gráficos na janela e senha da carteira.
