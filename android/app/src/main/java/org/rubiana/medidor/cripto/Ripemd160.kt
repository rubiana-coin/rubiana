package org.rubiana.medidor.cripto

object Ripemd160 {
    private val R1 = intArrayOf(
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
        7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8,
        3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12,
        1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2,
        4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13
    )
    private val R2 = intArrayOf(
        5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12,
        6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2,
        15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13,
        8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14,
        12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11
    )
    private val S1 = intArrayOf(
        11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
        7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12,
        11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5,
        11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12,
        9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6
    )
    private val S2 = intArrayOf(
        8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6,
        9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11,
        9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5,
        15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8,
        8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11
    )
    private val K1 = intArrayOf(0x00000000, 0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC.toInt(), 0xA953FD4E.toInt())
    private val K2 = intArrayOf(0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x7A6D76E9, 0x00000000)

    private fun f(j: Int, x: Int, y: Int, z: Int): Int = when (j / 16) {
        0 -> x xor y xor z
        1 -> (x and y) or (x.inv() and z)
        2 -> (x or y.inv()) xor z
        3 -> (x and z) or (y and z.inv())
        else -> x xor (y or z.inv())
    }

    private fun rol(x: Int, n: Int): Int = (x shl n) or (x ushr (32 - n))

    fun hash(dados: ByteArray): ByteArray {
        val h = intArrayOf(0x67452301, 0xEFCDAB89.toInt(), 0x98BADCFE.toInt(), 0x10325476, 0xC3D2E1F0.toInt())
        val total = ((dados.size + 8) / 64 + 1) * 64
        val msg = ByteArray(total)
        System.arraycopy(dados, 0, msg, 0, dados.size)
        msg[dados.size] = 0x80.toByte()
        val bits = dados.size.toLong() * 8
        for (i in 0 until 8) msg[total - 8 + i] = (bits ushr (8 * i)).toByte()
        val x = IntArray(16)
        for (bloco in 0 until total / 64) {
            for (i in 0 until 16) {
                val o = bloco * 64 + i * 4
                x[i] = (msg[o].toInt() and 0xFF) or ((msg[o + 1].toInt() and 0xFF) shl 8) or
                    ((msg[o + 2].toInt() and 0xFF) shl 16) or ((msg[o + 3].toInt() and 0xFF) shl 24)
            }
            var a1 = h[0]
            var b1 = h[1]
            var c1 = h[2]
            var d1 = h[3]
            var e1 = h[4]
            var a2 = h[0]
            var b2 = h[1]
            var c2 = h[2]
            var d2 = h[3]
            var e2 = h[4]
            for (j in 0 until 80) {
                var t = rol(a1 + f(j, b1, c1, d1) + x[R1[j]] + K1[j / 16], S1[j]) + e1
                a1 = e1
                e1 = d1
                d1 = rol(c1, 10)
                c1 = b1
                b1 = t
                t = rol(a2 + f(79 - j, b2, c2, d2) + x[R2[j]] + K2[j / 16], S2[j]) + e2
                a2 = e2
                e2 = d2
                d2 = rol(c2, 10)
                c2 = b2
                b2 = t
            }
            val t = h[1] + c1 + d2
            h[1] = h[2] + d1 + e2
            h[2] = h[3] + e1 + a2
            h[3] = h[4] + a1 + b2
            h[4] = h[0] + b1 + c2
            h[0] = t
        }
        val saida = ByteArray(20)
        for (i in 0 until 5) for (k in 0 until 4) saida[i * 4 + k] = (h[i] ushr (8 * k)).toByte()
        return saida
    }
}
