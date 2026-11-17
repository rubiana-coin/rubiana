package org.rubiana.medidor.cripto

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Test
import java.io.File
import java.math.BigInteger

class CarteiraTest {
    private fun hex(b: ByteArray): String = b.joinToString("") { String.format("%02x", it) }
    private fun bytes(h: String): ByteArray = ByteArray(h.length / 2) { h.substring(it * 2, it * 2 + 2).toInt(16).toByte() }
    private val lista: List<String> by lazy {
        File("../../tools/bip39-english.txt").readText().split(Regex("\\s+")).filter { it.isNotEmpty() }
    }

    @Test
    fun ripemd160_vetores_oficiais() {
        assertEquals("9c1185a5c5e9fc54612808977ee8f548b2258d31", hex(Ripemd160.hash(ByteArray(0))))
        assertEquals("8eb208f7e05d987a9b044a8e98c6b087f15a0bfc", hex(Ripemd160.hash("abc".toByteArray())))
    }

    @Test
    fun bech32_vetor_bip173() {
        val programa = bytes("751e76e8199196d454941c45d1b3a323f1433bd6")
        assertEquals("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", Bech32.codificarV0("bc", programa))
    }

    @Test
    fun secp256k1_ponto_gerador() {
        val p = Secp256k1.comprimida(Secp256k1.multiplicarG(BigInteger.ONE))
        assertEquals("0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798", hex(p))
    }

    @Test
    fun bip32_vetor_1() {
        val m = Bip32.mestra(bytes("000102030405060708090a0b0c0d0e0f"))
        assertEquals("e8f32e723decf4051aefac8e2c93c9c5b214313817cdb01a1494b917c8436b35", hex(Secp256k1.para32(m.chave)))
        assertEquals("873dff81c02f525623fd1fe5167eac3a55a049de3d314bb42ee227ffed37d508", hex(m.codigoCadeia))
        val f = Bip32.filha(m, 0x80000000L)
        assertEquals("edb2e14f9ee77d26dd93b4ecede8d16ed408ce149b6cd80b0715a2d911a0afea", hex(Secp256k1.para32(f.chave)))
    }

    @Test
    fun frases_invalidas_sao_recusadas() {
        assertNotNull(Bip39.validar("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon", lista))
        assertNotNull(Bip39.validar("abandon", lista))
        assertNotNull(Bip39.validar("zzzz abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about", lista))
    }

    @Test
    fun frases_geradas_sao_validas() {
        for (n in listOf(12, 24)) {
            repeat(20) {
                val f = Bip39.gerar(n, lista)
                assertEquals(n, f.split(" ").size)
                assertNull(Bip39.validar(f, lista))
            }
        }
    }

    @Test
    fun vetores_do_no_da_rubiana() {
        val texto = javaClass.getResourceAsStream("/vetores-carteira.json")!!.readBytes().toString(Charsets.UTF_8)
        val vetores = JSONObject(texto).getJSONArray("vetores")
        for (i in 0 until vetores.length()) {
            val v = vetores.getJSONObject(i)
            val frase = Bip39.deEntropia(bytes(v.getString("entropia_hex")), lista)
            assertEquals(v.getString("frase"), frase)
            assertNull(Bip39.validar(frase, lista))
            val sem = Bip39.semente(frase)
            assertEquals(v.getString("semente_hex"), hex(sem))
            for (rede in listOf("principal", "testnet")) {
                val r = v.getJSONObject(rede)
                val ext = r.getJSONArray("externos")
                val troco = r.getJSONArray("troco")
                for (k in 0 until ext.length()) assertEquals(rede + " recebimento " + k, ext.getString(k), Carteira.endereco(sem, rede, false, k))
                for (k in 0 until troco.length()) assertEquals(rede + " troco " + k, troco.getString(k), Carteira.endereco(sem, rede, true, k))
            }
        }
    }
}
