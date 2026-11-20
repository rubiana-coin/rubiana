package org.rubiana.medidor

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

class Armazem(contexto: Context) {
    private val prefs = contexto.getSharedPreferences("carteira", Context.MODE_PRIVATE)
    private val alias = "rubiana_carteira_v1"

    private fun chave(): SecretKey {
        val ks = KeyStore.getInstance("AndroidKeyStore")
        ks.load(null)
        val existente = ks.getKey(alias, null) as? SecretKey
        if (existente != null) return existente
        val gerador = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        gerador.init(
            KeyGenParameterSpec.Builder(alias, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256)
                .build()
        )
        return gerador.generateKey()
    }

    fun temCarteira(): Boolean = prefs.contains("semente")

    fun guardar(semente: ByteArray) {
        val c = Cipher.getInstance("AES/GCM/NoPadding")
        c.init(Cipher.ENCRYPT_MODE, chave())
        val pacote = c.iv + c.doFinal(semente)
        prefs.edit().putString("semente", Base64.encodeToString(pacote, Base64.NO_WRAP)).apply()
    }

    fun ler(): ByteArray? {
        val b64 = prefs.getString("semente", null) ?: return null
        val pacote = Base64.decode(b64, Base64.NO_WRAP)
        val c = Cipher.getInstance("AES/GCM/NoPadding")
        c.init(Cipher.DECRYPT_MODE, chave(), GCMParameterSpec(128, pacote, 0, 12))
        return c.doFinal(pacote, 12, pacote.size - 12)
    }

    fun apagar() {
        prefs.edit().remove("semente").apply()
    }

    var rede: String
        get() = prefs.getString("rede", "principal") ?: "principal"
        set(valor) {
            prefs.edit().putString("rede", valor).apply()
        }
}
