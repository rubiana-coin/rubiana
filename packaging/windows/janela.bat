@echo off
setlocal
cd /d "%~dp0"
title Rubiana - janela (REDE DE TESTE)
echo ================================================
echo   RUBIANA - janela (REDE DE TESTE)
echo   As moedas desta rede de teste NAO tem valor.
echo ================================================
echo.
echo O navegador vai abrir sozinho com a janela da Rubiana.
echo Para ENCERRAR: use o botao "Sair" na pagina (ou Ctrl+C aqui).
echo Se voce fechar esta janela pelo X, de dois cliques em parar.bat.
echo.
python\python.exe tools\rubiana-app.py --rede testnet --config configuracao.txt
echo.
echo A janela da Rubiana foi encerrada.
pause
