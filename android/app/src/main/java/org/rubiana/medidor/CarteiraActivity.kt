package org.rubiana.medidor

import android.app.Activity
import android.app.AlertDialog
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.graphics.Typeface
import android.os.Bundle
import android.text.InputType
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import org.rubiana.medidor.cripto.Bip39
import org.rubiana.medidor.cripto.Carteira
import java.security.MessageDigest
import java.security.SecureRandom

class CarteiraActivity : Activity() {
    private lateinit var armazem: Armazem
    private lateinit var lista: List<String>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        armazem = Armazem(this)
        try {
            lista = carregarLista()
        } catch (e: Exception) {
            val c = coluna()
            c.addView(texto("Erro: " + e.message, 16f))
            mostrar(c)
            return
        }
        if (armazem.temCarteira()) telaEnderecos() else telaInicio()
    }

    private fun carregarLista(): List<String> {
        val dados = assets.open("bip39-english.txt").readBytes()
        val hash = MessageDigest.getInstance("SHA-256").digest(dados).joinToString("") { String.format("%02x", it) }
        if (hash != "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda") {
            throw IllegalStateException("a lista de palavras esta alterada ou corrompida")
        }
        return dados.toString(Charsets.UTF_8).split(Regex("\\s+")).filter { it.isNotEmpty() }
    }

    private fun coluna(): LinearLayout {
        val c = LinearLayout(this)
        c.orientation = LinearLayout.VERTICAL
        c.setPadding(32, 48, 32, 32)
        return c
    }

    private fun texto(t: String, tamanho: Float = 15f, negrito: Boolean = false): TextView {
        val v = TextView(this)
        v.text = t
        v.textSize = tamanho
        if (negrito) v.setTypeface(null, Typeface.BOLD)
        v.setPadding(0, 12, 0, 12)
        return v
    }

    private fun botao(t: String, acao: () -> Unit): Button {
        val b = Button(this)
        b.text = t
        b.setOnClickListener { acao() }
        return b
    }

    private fun mostrar(c: LinearLayout, seguro: Boolean = false) {
        if (seguro) {
            window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)
        } else {
            window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE)
        }
        val rolagem = ScrollView(this)
        rolagem.addView(c)
        setContentView(rolagem)
    }

    private fun nomeRede(): String =
        if (armazem.rede == "principal") "principal (moedas reais, a partir de 12/12/2026)" else "teste (as moedas não têm valor)"

    private fun campoSeguro(multilinha: Boolean): EditText {
        val e = EditText(this)
        var tipo = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS or InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD
        if (multilinha) tipo = tipo or InputType.TYPE_TEXT_FLAG_MULTI_LINE
        e.inputType = tipo
        e.importantForAutofill = View.IMPORTANT_FOR_AUTOFILL_NO
        if (multilinha) e.minLines = 4
        return e
    }

    private fun telaInicio() {
        val c = coluna()
        c.addView(texto("Carteira Rubiana", 22f, true))
        c.addView(texto("Rede: " + nomeRede(), 14f))
        c.addView(texto("A carteira usa uma frase de recuperação de 12 ou 24 palavras. Quem tiver a frase controla as moedas: anote no papel, em ordem, e guarde em lugar seguro. Nunca digite a frase em sites, não tire foto e não envie a ninguém. Sem a frase não há como recuperar a carteira. Não existe suporte nem recuperação por e-mail."))
        c.addView(botao("Criar carteira nova (12 palavras)") { telaFrase(Bip39.gerar(12, lista)) })
        c.addView(botao("Criar carteira nova (24 palavras)") { telaFrase(Bip39.gerar(24, lista)) })
        c.addView(botao("Já tenho uma frase (restaurar)") { telaRestaurar() })
        mostrar(c)
    }

    private fun telaFrase(frase: String) {
        val c = coluna()
        c.addView(texto("Sua frase de recuperação", 22f, true))
        c.addView(texto("Anote as palavras no papel, na ordem. Esta é a única vez que ela aparece. Esta tela não permite captura de tela.", 14f))
        val sb = StringBuilder()
        for ((i, w) in frase.split(" ").withIndex()) sb.append(String.format("%2d. %s\n", i + 1, w))
        val t = texto(sb.toString(), 18f)
        t.typeface = Typeface.MONOSPACE
        c.addView(t)
        c.addView(botao("Já anotei, continuar") { telaConfirmar(frase) })
        c.addView(botao("Cancelar") { telaInicio() })
        mostrar(c, true)
    }

    private fun telaConfirmar(frase: String) {
        val pal = frase.split(" ")
        val posicoes = (1..pal.size).shuffled(kotlin.random.Random(SecureRandom().nextLong())).take(3).sorted()
        val c = coluna()
        c.addView(texto("Conferir a frase", 22f, true))
        c.addView(texto("Digite as palavras pedidas para provar que você anotou a frase.", 14f))
        val campos = ArrayList<EditText>()
        for (p in posicoes) {
            c.addView(texto("Palavra nº " + p, 16f))
            val e = campoSeguro(false)
            campos.add(e)
            c.addView(e)
        }
        val aviso = texto("", 14f)
        c.addView(aviso)
        c.addView(botao("Confirmar e criar a carteira") {
            var ok = true
            for ((i, p) in posicoes.withIndex()) {
                if (campos[i].text.toString().trim().lowercase() != pal[p - 1]) ok = false
            }
            if (!ok) {
                aviso.text = "Alguma palavra não confere. Confira o papel e tente de novo, ou veja a frase outra vez."
            } else {
                armazem.guardar(Bip39.semente(frase))
                telaEnderecos()
            }
        })
        c.addView(botao("Ver as palavras de novo") { telaFrase(frase) })
        mostrar(c, true)
    }

    private fun telaRestaurar() {
        val c = coluna()
        c.addView(texto("Restaurar carteira", 22f, true))
        c.addView(texto("Digite as 12 ou 24 palavras, separadas por espaço, na ordem.", 14f))
        val campo = campoSeguro(true)
        c.addView(campo)
        val aviso = texto("", 14f)
        c.addView(aviso)
        c.addView(botao("Restaurar") {
            val frase = Bip39.normalizar(campo.text.toString())
            val erro = Bip39.validar(frase, lista)
            if (erro != null) {
                aviso.text = erro
            } else {
                armazem.guardar(Bip39.semente(frase))
                telaEnderecos()
            }
        })
        c.addView(botao("Voltar") { telaInicio() })
        mostrar(c, true)
    }

    private fun telaEnderecos() {
        val c = coluna()
        c.addView(texto("Minha carteira", 22f, true))
        c.addView(texto("Rede: " + nomeRede(), 14f))
        c.addView(texto("Endereços para receber (mesmo caminho da carteira do Windows). Esta versão ainda não mostra saldo nem envia moedas: isso depende de um servidor, que vem em versões futuras.", 13f))
        val lugar = LinearLayout(this)
        lugar.orientation = LinearLayout.VERTICAL
        lugar.addView(texto("Calculando os endereços...", 14f))
        c.addView(lugar)
        c.addView(botao("Trocar rede (principal / teste)") {
            armazem.rede = if (armazem.rede == "principal") "testnet" else "principal"
            telaEnderecos()
        })
        c.addView(botao("Apagar a carteira deste celular") { confirmarApagar() })
        mostrar(c)
        val rede = armazem.rede
        Thread {
            val enderecos = ArrayList<String>()
            var erro: String? = null
            try {
                val semente = armazem.ler() ?: throw IllegalStateException("carteira nao encontrada")
                for (i in 0 until 5) enderecos.add(Carteira.endereco(semente, rede, false, i))
            } catch (e: Exception) {
                erro = e.message
            }
            runOnUiThread {
                lugar.removeAllViews()
                if (erro != null) {
                    lugar.addView(texto("Erro: " + erro, 14f))
                } else {
                    for ((i, a) in enderecos.withIndex()) {
                        lugar.addView(texto("Endereço " + i, 13f))
                        val t = texto(a, 15f)
                        t.typeface = Typeface.MONOSPACE
                        t.setTextIsSelectable(true)
                        lugar.addView(t)
                        lugar.addView(botao("Copiar") { copiar(a) })
                    }
                }
            }
        }.start()
    }

    private fun confirmarApagar() {
        AlertDialog.Builder(this)
            .setTitle("Apagar a carteira?")
            .setMessage("Sem a frase de recuperação anotada você perde o acesso às moedas. Esta ação não pode ser desfeita.")
            .setPositiveButton("Apagar") { _, _ ->
                armazem.apagar()
                telaInicio()
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }

    private fun copiar(valor: String) {
        val cm = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        cm.setPrimaryClip(ClipData.newPlainText("endereco", valor))
        Toast.makeText(this, "Endereço copiado", Toast.LENGTH_SHORT).show()
    }
}
