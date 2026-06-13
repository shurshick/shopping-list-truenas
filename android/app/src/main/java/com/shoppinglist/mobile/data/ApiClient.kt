package com.shoppinglist.mobile.data

import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    fun create(baseUrl: String): ShoppingApi {
        val clientBuilder = OkHttpClient.Builder()
        addDebugLogging(clientBuilder)
        val client = clientBuilder.build()

        return Retrofit.Builder()
            .baseUrl(normalizeBaseUrl(baseUrl))
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ShoppingApi::class.java)
    }

    private fun normalizeBaseUrl(baseUrl: String): String {
        val trimmed = baseUrl.trim()
        return if (trimmed.endsWith("/")) trimmed else "$trimmed/"
    }
}
