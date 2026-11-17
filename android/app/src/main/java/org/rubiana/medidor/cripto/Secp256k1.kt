package org.rubiana.medidor.cripto

import java.math.BigInteger

object Secp256k1 {
    val P: BigInteger = BigInteger("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16)
    val N: BigInteger = BigInteger("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
    private val GX = BigInteger("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798", 16)
    private val GY = BigInteger("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8", 16)
    private val TRES = BigInteger.valueOf(3)

    class Ponto(val x: BigInteger, val y: BigInteger)

    private fun somar(a: Ponto?, b: Ponto?): Ponto? {
        if (a == null) return b
        if (b == null) return a
        val inclinacao: BigInteger
        if (a.x == b.x) {
            if (a.y.add(b.y).mod(P).signum() == 0) return null
            inclinacao = a.x.multiply(a.x).multiply(TRES).multiply(a.y.shiftLeft(1).modInverse(P)).mod(P)
        } else {
            inclinacao = b.y.subtract(a.y).multiply(b.x.subtract(a.x).mod(P).modInverse(P)).mod(P)
        }
        val x = inclinacao.multiply(inclinacao).subtract(a.x).subtract(b.x).mod(P)
        val y = inclinacao.multiply(a.x.subtract(x)).subtract(a.y).mod(P)
        return Ponto(x, y)
    }

    fun multiplicarG(k: BigInteger): Ponto {
        var resultado: Ponto? = null
        var base: Ponto? = Ponto(GX, GY)
        var e = k
        while (e.signum() > 0) {
            if (e.testBit(0)) resultado = somar(resultado, base)
            base = somar(base, base)
            e = e.shiftRight(1)
        }
        return resultado ?: throw IllegalArgumentException("chave invalida")
    }

    fun para32(v: BigInteger): ByteArray {
        val b = v.toByteArray()
        val saida = ByteArray(32)
        if (b.size >= 32) System.arraycopy(b, b.size - 32, saida, 0, 32)
        else System.arraycopy(b, 0, saida, 32 - b.size, b.size)
        return saida
    }

    fun comprimida(p: Ponto): ByteArray {
        val prefixo = if (p.y.testBit(0)) 3 else 2
        return byteArrayOf(prefixo.toByte()) + para32(p.x)
    }
}
