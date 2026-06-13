package com.shoppinglist.mobile.data.local

import android.content.Context

class ProductCatalogStorage(context: Context) {
    private val preferences = context.getSharedPreferences("shopping-list", Context.MODE_PRIVATE)

    fun load(defaultProducts: List<String>): List<String> {
        val stored = preferences.getString("productCatalog", null)
        return stored
            ?.split("\n")
            ?.map { it.trim() }
            ?.filter { it.isNotBlank() }
            ?.distinct()
            ?.sortedWith(String.CASE_INSENSITIVE_ORDER)
            ?: defaultProducts
    }

    fun save(catalog: List<String>) {
        val cleanedCatalog = catalog
            .map { it.trim() }
            .filter { it.isNotBlank() }
            .distinct()
            .sortedWith(String.CASE_INSENSITIVE_ORDER)
        preferences.edit().putString("productCatalog", cleanedCatalog.joinToString("\n")).apply()
    }
}
