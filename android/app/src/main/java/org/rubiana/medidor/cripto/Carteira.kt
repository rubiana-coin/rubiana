package org.rubiana.medidor.cripto

import java.security.MessageDigest

object Carteira {
    private const val ENDURECIDO = 0x80000000L

    fun moeda(rede: String): Long = if (rede == "principal") 8686L else 1L

    fun prefixo(rede: String): String = if (rede == "principal") "rubia" else "trubia"

    // Caminho igual ao da carteira do Windows: m/84'/moeda'/0'/(0 recebimento, 1 troco)/indice
    fun endereco(semente: ByteArray, rede: String, troco: Boolean, indice: Int): String {
        val caminho = listOf(84L + ENDURECIDO, moeda(rede) + ENDURECIDO, ENDURECIDO, if (troco) 1L else 0L, indice.toLong())
        val chave = Bip32.caminho(semente, caminho)
        val pub = Secp256k1.comprimida(Secp256k1.multiplicarG(chave.chave))
        val h160 = Ripemd160.hash(MessageDigest.getInstance("SHA-256").digest(pub))
        return Bech32.codificarV0(prefixo(rede), h160)
    }
}
