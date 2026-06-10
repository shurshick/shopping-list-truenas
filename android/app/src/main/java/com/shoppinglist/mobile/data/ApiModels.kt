package com.shoppinglist.mobile.data

data class AuthRequest(val email: String, val password: String)
data class TokenResponse(val access_token: String, val token_type: String)

data class ListCreate(val name: String)
data class ItemCreate(val name: String, val quantity: String = "")
data class ItemUpdate(val name: String? = null, val quantity: String? = null, val is_checked: Boolean? = null)
data class ShareRequest(val email: String)

data class SyncResponse(val lists: List<ShoppingListDto>)
data class ShoppingListDto(
    val id: Int,
    val name: String,
    val owner_id: Int,
    val updated_at: String,
    val items: List<ShoppingItemDto>
)

data class ShoppingItemDto(
    val id: Int,
    val name: String,
    val quantity: String,
    val is_checked: Boolean,
    val updated_at: String
)
