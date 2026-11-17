package org.rubiana.medidor.cripto

import java.math.BigInteger
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

class ChaveBip32(val chave: BigInteger, val codigoCadeia: ByteArray)

object Bip32 {
    private fun hmac512(chave: ByteArray, dados: ByteArray): ByteArray {
        val mac = Mac.getInstance("HmacSHA512")
        mac.init(SecretKeySpec(chave, "HmacSHA512"))
        return mac.doFinal(dados)
    }

    private fun ser32(v: Long): ByteArray =
        byteArrayOf((v ushr 24).toByte(), (v ushr 16).toByte(), (v ushr 8).toByte(), v.toByte())

    fun mestra(semente: ByteArray): ChaveBip32 {
        val i = hmac512("Bitcoin seed".toByteArray(Charsets.UTF_8), semente)
        val k = BigInteger(1, i.copyOfRange(0, 32))
        if (k.signum() == 0 || k >= Secp256k1.N) throw IllegalArgumentException("semente invalida")
        return ChaveBip32(k, i.copyOfRange(32, 64))
    }

    fun filha(pai: ChaveBip32, indice: Long): ChaveBip32 {
        val endurecido = indice >= 0x80000000L
        val dados = if (endurecido) {
            byteArrayOf(0) + Secp256k1.para32(pai.chave) + ser32(indice)
        } else {
            Secp256k1.comprimida(Secp256k1.multiplicarG(pai.chave)) + ser32(indice)
        }
        val i = hmac512(pai.codigoCadeia, dados)
        val il = BigInteger(1, i.copyOfRange(0, 32))
        val k = il.add(pai.chave).mod(Secp256k1.N)
        if (il >= Secp256k1.N || k.signum() == 0) throw IllegalArgumentException("indice invalido")
        return ChaveBip32(k, i.copyOfRange(32, 64))
    }

    fun caminho(semente: ByteArray, indices: List<Long>): ChaveBip32 {
        var c = mestra(semente)
        for (i in indices) c = filha(c, i)
        return c
    }
}
