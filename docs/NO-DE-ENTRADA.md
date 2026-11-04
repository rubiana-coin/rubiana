# Rodar um nó de entrada da Rubiana

Um nó de entrada é um nó comum que fica ligado 24 horas e aceita conexões de fora. Ele é o ponto de encontro de quem acabou de instalar a Rubiana. Ele não tem poder especial sobre a rede. Quanto mais pessoas diferentes rodarem nós de entrada, menos a rede depende de qualquer uma delas.

## O que precisa

- Um computador ou servidor ligado 24 horas, com uns 1 GB de memória livre.
- A porta TCP **18686** (rede de teste) aberta para a internet. Em casa, isso exige redirecionar a porta no roteador.
- Aviso: o endereço IP do nó fica público.

## Com Docker (o jeito mais simples)
docker run -d --name rubiana-no --restart unless-stopped -p 18686:18686 -v rubiana-dados:/data ghcr.io/worm186/rubiana-no:rede2
docker logs -f rubiana-no

Nos logs procure `Done loading` e `Bound to 0.0.0.0:18686`.

## Sem Docker
rubianad -testnet -disablewallet -listen=1 -dnsseed=0 -fixedseeds=0 -listenonion=0 -dbcache=64

Não exponha a porta RPC (18690) e não use carteira num nó de entrada.

## Conferir de fora

De OUTRO computador: `nc -vz SEU_ENDERECO 18686`. Se conectar, a porta está aberta.

## Entrar na lista

Abra uma issue no repositório com o endereço (`nome-ou-IP:18686`). Quem quiser usar o seu nó antes disso pode colocar uma linha com o endereço no arquivo `nos.txt` do pacote de Windows.
