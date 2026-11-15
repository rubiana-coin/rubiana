# Roteiro do dia da largada (12/12/2026)

Horários de Brasília (UTC-3). A largada é às 12:00 de Brasília, que são 15:00 UTC.

## Nos dias anteriores
- 5 a 8/12: Release final pública com o arquivo SHA256SUMS.txt; conferir que baixa e abre sem login; enviar o pacote ao VirusTotal; nós de entrada da rede principal no ar (dois no Railway e, se possível, um de outra pessoa) e NOS_PRINCIPAL preenchido no código. O código fica congelado em 8/12: depois disso, só correção de erro grave.
- 9 e 10/12: teste do pacote final por outra pessoa; publicar o anúncio (GitHub e Bitcointalk).
- 11/12 (véspera): checklist. Os nós de entrada respondem? A Release abre e o SHA-256 confere? O PC está atualizado, com energia e relógio sincronizado? As 12 palavras da carteira estão no papel?

## Dia 12/12
- 10:00: conferir os nós de entrada (abrir o pacote e ver "Conexões" maior que 0; no Railway, ver que o serviço está ativo).
- 11:30: sincronizar o relógio do Windows (Configurações, Hora e idioma, Sincronizar agora).
- 11:50: abrir o janela.bat da rede principal, abrir a carteira e clicar em "Iniciar mineração". Vai aparecer "aguardando o início da rede". Deixar assim.
- 12:00 (15:00 UTC): o programa começa a minerar sozinho. Nos primeiros blocos a dificuldade é fixa (262.144 tentativas por bloco), então o tempo por bloco depende só do poder de cada um.
- 12:00 a 13:00: acompanhar Altura e Conexões. Se não houver nenhum bloco depois de 1 hora e o poder do PC for compatível, investigar (relógio, conexões, mensagens do programa).
- 21:00 (00:00 UTC de 13/12): troca da chave do RandomX (época 10399 para 10400). É normal o minerador pausar de 30 a 60 segundos. Conferir que os blocos continuam.
- 24 horas depois: balanço (altura, tempo médio entre blocos, dificuldade, relatos recebidos).

## Se algo der errado
- Nó de entrada caiu: reiniciar o serviço no Railway (Deployments, Redeploy) e usar o outro; quem estiver minerando pode acrescentar nós no arquivo nos.txt.
- Sem blocos ou blocos rejeitados: conferir Conexões e o relógio do computador (um relógio errado em mais de 10 minutos recusa blocos válidos); reiniciar o programa.
- Falha séria: não improvisar. Anotar, avisar numa issue fixada no GitHub e consultar antes de agir. Reiniciar a rede com novo bloco inicial é só a última hipótese e está dito no anúncio.
- Comunicação: um canal oficial (Releases e Issues do GitHub) e o tópico do Bitcointalk, com mensagens curtas e sem promessas.
