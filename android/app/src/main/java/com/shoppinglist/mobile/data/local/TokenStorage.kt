package com.shoppinglist.mobile.data.local

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class TokenStorage(context: Context) {
    private val legacyPreferences = context.getSharedPreferences("shopping-list", Context.MODE_PRIVATE)
    private val securePreferences = createSecurePreferences(context)

    fun loadToken(): String? {
        val encryptedToken = securePreferences.getString("token", null)
        val legacyToken = legacyPreferences.getString("token", null)
        if (!legacyToken.isNullOrBlank()) {
            if (encryptedToken.isNullOrBlank()) {
                securePreferences.edit().putString("token", legacyToken).apply()
            }
            legacyPreferences.edit().remove("token").apply()
            return encryptedToken ?: legacyToken
        }
        return encryptedToken
    }

    fun saveToken(token: String) {
        securePreferences.edit().putString("token", token).apply()
        legacyPreferences.edit().remove("token").apply()
    }

    fun clearToken() {
        securePreferences.edit().remove("token").apply()
        legacyPreferences.edit().remove("token").apply()
    }

    private fun createSecurePreferences(context: Context): SharedPreferences {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        return EncryptedSharedPreferences.create(
            context,
            "shopping-list-secure",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }
}
