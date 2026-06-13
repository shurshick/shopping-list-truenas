package com.shoppinglist.mobile.data

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor

internal fun addDebugLogging(builder: OkHttpClient.Builder) {
    val logging = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BASIC
        redactHeader("Authorization")
    }
    builder.addInterceptor(logging)
}
