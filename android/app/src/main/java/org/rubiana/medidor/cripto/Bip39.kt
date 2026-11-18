package org.rubiana.medidor.cripto

import java.math.BigInteger
import java.security.MessageDigest
import java.security.SecureRandom
import java.text.Normalizer
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

object Bip39 {
    private fun fixo(v: BigInteger, n: Int): ByteArray {
        val b = v.toByteArray()
        val saida = ByteArray(n)
        if (b.size >= n) System.arraycopy(b, b.size - n, saida, 0, n)
        else System.arraycopy(b, 0, saida, n - b.size, b.size)
        return saida
    }

    fun normalizar(frase: String): String =
        Normalizer.normalize(frase, Normalizer.Form.NFKD).lowercase().trim().split(Regex("\\s+")).joinToString(" ")

    fun deEntropia(ent: ByteArray, lista: List<String>): String {
        require(ent.size == 16 || ent.size == 32) { "a entropia deve ter 16 ou 32 bytes" }
        require(lista.size == 2048) { "lista de palavras invalida" }
        val cs = ent.size * 8 / 32
        val hash = MessageDigest.getInstance("SHA-256").digest(ent)
        val extra = (hash[0].toInt() and 0xFF) ushr (8 - cs)
        val valor = BigInteger(1, ent).shiftLeft(cs).or(BigInteger.valueOf(extra.toLong()))
        val n = (ent.size * 8 + cs) / 11
        val palavras = ArrayList<String>()
        for (i in 0 until n) {
            palavras.add(lista[valor.shiftRight(11 * (n - 1 - i)).toInt() and 0x7FF])
        }
        return palavras.joinToString(" ")
    }

    fun gerar(quantidade: Int, lista: List<String>): String {
        require(quantidade == 12 || quantidade == 24) { "use 12 ou 24 palavras" }
        val ent = ByteArray(if (quantidade == 12) 16 else 32)
        SecureRandom().nextBytes(ent)
        return deEntropia(ent, lista)
    }

    fun validar(frase: String, lista: List<String>): String? {
        val pal = normalizar(frase).split(" ")
        if (pal.size != 12 && pal.size != 24) return "a frase deve ter 12 ou 24 palavras (esta tem " + pal.size + ")"
        val indice = HashMap<String, Int>()
        for ((i, w) in lista.withIndex()) indice[w] = i
        var valor = BigInteger.ZERO
        for (w in pal) {
            val i = indice[w] ?: return "palavra desconhecida: " + w.take(20)
            valor = valor.shiftLeft(11).or(BigInteger.valueOf(i.toLong()))
        }
        val total = pal.size * 11
        val cs = total / 33
        val ent = fixo(valor.shiftRight(cs), (total - cs) / 8)
        val esperado = (MessageDigest.getInstance("SHA-256").digest(ent)[0].toInt() and 0xFF) ushr (8 - cs)
        val mascara = (1 shl cs) - 1
        if (esperado != (valor.toInt() and mascara)) {
            return "frase invalida: a conferencia final nao bate (alguma palavra esta errada ou fora de ordem)"
        }
        return null
    }

    fun semente(frase: String, senha: String = ""): ByteArray {
        val p = normalizar(frase).toByteArray(Charsets.UTF_8)
        val sal = ("mnemonic" + Normalizer.normalize(senha, Normalizer.Form.NFKD)).toByteArray(Charsets.UTF_8)
        val mac = Mac.getInstance("HmacSHA512")
        mac.init(SecretKeySpec(p, "HmacSHA512"))
        mac.update(sal)
        mac.update(byteArrayOf(0, 0, 0, 1))
        var u = mac.doFinal()
        val t = u.copyOf()
        for (i in 1 until 2048) {
            u = mac.doFinal(u)
            for (k in t.indices) t[k] = (t[k].toInt() xor u[k].toInt()).toByte()
        }
        return t
    }
}
