package org.rubiana.medidor.cripto

object Bech32 {
    private const val CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    private val GEN = intArrayOf(0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3)

    private fun polymod(valores: IntArray): Int {
        var chk = 1
        for (v in valores) {
            val b = chk ushr 25
            chk = ((chk and 0x1ffffff) shl 5) xor v
            for (i in 0 until 5) if (((b ushr i) and 1) != 0) chk = chk xor GEN[i]
        }
        return chk
    }

    private fun expandir(hrp: String): IntArray {
        val r = IntArray(hrp.length * 2 + 1)
        for (i in hrp.indices) {
            r[i] = hrp[i].code ushr 5
            r[i + hrp.length + 1] = hrp[i].code and 31
        }
        return r
    }

    fun codificarV0(hrp: String, programa: ByteArray): String {
        val dados = IntArray(1 + (programa.size * 8 + 4) / 5)
        var acc = 0
        var bits = 0
        var pos = 1
        for (b in programa) {
            acc = (acc shl 8) or (b.toInt() and 0xFF)
            bits += 8
            while (bits >= 5) {
                bits -= 5
                dados[pos++] = (acc ushr bits) and 31
            }
            acc = acc and ((1 shl bits) - 1)
        }
        if (bits > 0) dados[pos++] = (acc shl (5 - bits)) and 31
        val mod = polymod(expandir(hrp) + dados + IntArray(6)) xor 1
        val sb = StringBuilder(hrp).append('1')
        for (d in dados) sb.append(CHARSET[d])
        for (i in 0 until 6) sb.append(CHARSET[(mod ushr (5 * (5 - i))) and 31])
        return sb.toString()
    }
}
