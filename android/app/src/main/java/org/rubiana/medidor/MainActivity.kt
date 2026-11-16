package org.rubiana.medidor

import android.app.Activity
import android.content.Intent
import android.content.IntentFilter
import android.graphics.Typeface
import android.os.BatteryManager
import android.os.Build
import android.os.Bundle
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import java.io.BufferedReader
import java.io.InputStreamReader
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit

class MainActivity : Activity() {

    private lateinit var saida: TextView
    private lateinit var rolagem: ScrollView
    private val botoes = ArrayList<Button>()

    @Volatile
    private var medindo = false

    @Volatile
    private var pedidoParar = false

    @Volatile
    private var processo: Process? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        val raiz = LinearLayout(this)
        raiz.orientation = LinearLayout.VERTICAL
        raiz.setPadding(32, 48, 32, 32)

        val titulo = TextView(this)
        titulo.text = "Rubiana: medidor de RandomX"
        titulo.textSize = 22f
        titulo.setTypeface(null, Typeface.BOLD)
        raiz.addView(titulo)

        val aviso = TextView(this)
        aviso.text = "Mede quantos hashes por segundo este celular faz com o RandomX (modo leve). " +
            "Cada teste dura cerca de 30 segundos. Deixe o celular carregando, fora do sol e sem capa grossa. " +
            "O teste para sozinho se a bateria passar de 45 graus."
        aviso.setPadding(0, 16, 0, 16)
        raiz.addView(aviso)

        val linha = LinearLayout(this)
        linha.orientation = LinearLayout.HORIZONTAL
        for (n in intArrayOf(2, 4, 8)) {
            val botao = Button(this)
            botao.text = "$n núcleos"
            botao.setOnClickListener { medir(n) }
            botoes.add(botao)
            linha.addView(botao, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
        }
        raiz.addView(linha)

        val botaoLongo = Button(this)
        botaoLongo.text = "Teste longo: 5 minutos, 8 núcleos"
        botaoLongo.setOnClickListener { medir(8, 5) }
        botoes.add(botaoLongo)
        raiz.addView(botaoLongo)

        val botaoParar = Button(this)
        botaoParar.text = "Parar o teste"
        botaoParar.setOnClickListener { pedidoParar = true }
        raiz.addView(botaoParar)

        saida = TextView(this)
        saida.typeface = Typeface.MONOSPACE
        saida.textSize = 13f
        saida.setPadding(0, 16, 0, 0)
        rolagem = ScrollView(this)
        rolagem.addView(saida)
        raiz.addView(rolagem, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f))

        setContentView(raiz)

        escrever("Aparelho: ${Build.MANUFACTURER} ${Build.MODEL} (${Build.HARDWARE})")
        escrever("Android ${Build.VERSION.RELEASE}, ABI ${Build.SUPPORTED_ABIS.joinToString()}")
        escrever("Núcleos visíveis: ${Runtime.getRuntime().availableProcessors()}")
        val (temp, nivel) = bateria()
        escrever("Bateria: $nivel%, $temp °C")
        escrever("")
    }

    override fun onDestroy() {
        pedidoParar = true
        processo?.destroyForcibly()
        super.onDestroy()
    }

    private fun escrever(texto: String) {
        runOnUiThread {
            saida.append(texto + "\n")
            rolagem.post { rolagem.fullScroll(ScrollView.FOCUS_DOWN) }
        }
    }

    private fun bateria(): Pair<Int, Int> {
        val i = registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val temp = (i?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, 0) ?: 0) / 10
        val nivel = i?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        return Pair(temp, nivel)
    }

    private fun medir(threads: Int, minutos: Int = 0) {
        if (medindo) return
        medindo = true
        pedidoParar = false
        runOnUiThread { botoes.forEach { it.isEnabled = false } }
        Thread {
            try {
                executarTeste(threads, minutos)
            } catch (e: Exception) {
                escrever("  erro: ${e.javaClass.simpleName}: ${e.message}")
            } finally {
                processo?.destroyForcibly()
                processo = null
                medindo = false
                runOnUiThread { botoes.forEach { it.isEnabled = true } }
            }
        }.start()
    }

    private fun executarTeste(threads: Int, minutos: Int) {
        val (tempIni, nivelIni) = bateria()
        escrever("== Teste com $threads thread(s) ==")
        escrever("Preparando o motor (pode levar alguns segundos)...")
        val caminho = applicationInfo.nativeLibraryDir + "/libminer.so"
        val p = ProcessBuilder(caminho, "--threads", threads.toString())
            .redirectErrorStream(true)
            .start()
        processo = p

        val fila = LinkedBlockingQueue<String>()
        val leitor = Thread {
            try {
                BufferedReader(InputStreamReader(p.inputStream)).forEachLine { fila.put(it) }
            } catch (e: Exception) {
            }
        }
        leitor.isDaemon = true
        leitor.start()

        val escritor = p.outputStream.bufferedWriter()
        fun enviar(linha: String) {
            escritor.write(linha + "\n")
            escritor.flush()
        }

        val outras = ArrayList<String>()
        var pronto = false
        val limite = System.currentTimeMillis() + 180_000L
        while (!pedidoParar && System.currentTimeMillis() < limite) {
            val l = fila.poll(1, TimeUnit.SECONDS)
            if (l == null) {
                if (!p.isAlive) break
                continue
            }
            if (l.trim() == "READY") {
                pronto = true
                break
            }
            outras.add(l)
        }
        if (!pronto) {
            escrever("  falhou: o motor não ficou pronto. Mensagens: " + outras.takeLast(5).joinToString(" | "))
            return
        }

        escrever("Motor pronto. Medindo (6 s de aquecimento + 20 s de medida)...")
        enviar("JOB 1 " + "00".repeat(76) + " " + "00".repeat(32))

        fun estatistica(): Pair<Long, Double>? {
            enviar("STATS")
            val fim = System.currentTimeMillis() + 8000L
            while (System.currentTimeMillis() < fim) {
                val l = fila.poll(1, TimeUnit.SECONDS) ?: continue
                val partes = l.trim().split(" ")
                if (partes.size >= 3 && partes[0] == "STATS") {
                    return Pair(partes[1].toLong(), partes[2].toDouble())
                }
            }
            return null
        }

        fun esperar(segundos: Int): Boolean {
            for (i in 0 until segundos) {
                Thread.sleep(1000)
                if (pedidoParar) {
                    escrever("  teste interrompido.")
                    return false
                }
                if (i % 5 == 4) {
                    val (t, _) = bateria()
                    if (t >= 45) {
                        escrever("  parei: a bateria chegou a $t °C.")
                        return false
                    }
                }
            }
            return true
        }

        if (!esperar(6)) return
        if (minutos > 0) {
            escrever("Teste longo: $minutos minuto(s), uma medida a cada 30 s.")
            var anterior: Pair<Long, Double> = estatistica() ?: run {
                escrever("  falhou: o motor não respondeu ao STATS.")
                return
            }
            for (k in 1..(minutos * 2)) {
                if (!esperar(30)) return
                val atual = estatistica() ?: break
                val dt = atual.second - anterior.second
                val taxaK = if (dt > 0.0) (atual.first - anterior.first) / dt else 0.0
                val (tK, nK) = bateria()
                escrever("  +" + (k * 30) + " s: " + String.format("%.1f", taxaK) + " H/s, " + tK + " °C, carga " + nK + "%")
                anterior = atual
            }
            enviar("QUIT")
            p.waitFor(5, TimeUnit.SECONDS)
            escrever("Fim do teste longo.")
            escrever("")
            return
        }
        val a = estatistica()
        if (a == null) {
            escrever("  falhou: o motor não respondeu ao STATS.")
            return
        }
        if (!esperar(20)) return
        val b = estatistica()
        if (b == null) {
            escrever("  falhou: o motor não respondeu ao STATS.")
            return
        }

        val dh = b.first - a.first
        val ds = b.second - a.second
        val taxa = if (ds > 0.0) dh / ds else 0.0
        val (tempFim, nivelFim) = bateria()
        escrever("  Resultado: " + String.format("%.1f", taxa) + " H/s com $threads thread(s)")
        escrever("  Temperatura da bateria: $tempIni -> $tempFim °C; carga $nivelIni% -> $nivelFim%")
        enviar("QUIT")
        p.waitFor(5, TimeUnit.SECONDS)
        escrever("")
    }
}
