package com.shoppinglist.mobile.ui

import android.app.Application
import android.content.Context
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.shoppinglist.mobile.data.ApiClient
import com.shoppinglist.mobile.data.AuthRequest
import com.shoppinglist.mobile.data.ItemCreate
import com.shoppinglist.mobile.data.ItemUpdate
import com.shoppinglist.mobile.data.ListCreate
import com.shoppinglist.mobile.data.ShareRequest
import com.shoppinglist.mobile.data.ShoppingListDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class ShoppingUiState(
    val token: String? = null,
    val serverUrl: String = "",
    val email: String = "",
    val password: String = "",
    val lists: List<ShoppingListDto> = emptyList(),
    val productCatalog: List<String> = emptyList(),
    val selectedListId: Int? = null,
    val message: String? = null,
    val isLoading: Boolean = false
)

class ShoppingViewModel(application: Application) : AndroidViewModel(application) {
    private val preferences = application.getSharedPreferences("shopping-list", Context.MODE_PRIVATE)
    private val defaultProducts = listOf(
        "Хлеб",
        "Молоко",
        "Сыр",
        "Яйца",
        "Масло",
        "Курица",
        "Говядина",
        "Рыба",
        "Картофель",
        "Морковь",
        "Лук",
        "Помидоры",
        "Огурцы",
        "Яблоки",
        "Бананы",
        "Рис",
        "Макароны",
        "Сахар",
        "Соль",
        "Чай",
        "Кофе"
    )
    private val _state = MutableStateFlow(
        ShoppingUiState(
            token = preferences.getString("token", null),
            serverUrl = preferences.getString("serverUrl", "") ?: "",
            productCatalog = loadProductCatalog()
        )
    )
    val state: StateFlow<ShoppingUiState> = _state.asStateFlow()

    init {
        if (_state.value.token != null) {
            sync()
        }
    }

    fun setServerUrl(value: String) = update { copy(serverUrl = value) }
    fun setEmail(value: String) = update { copy(email = value) }
    fun setPassword(value: String) = update { copy(password = value) }

    fun login(register: Boolean = false) = viewModelScope.launch {
        runRequest {
            val current = _state.value
            val api = api()
            val response = if (register) {
                api.register(AuthRequest(current.email, current.password))
            } else {
                api.login(AuthRequest(current.email, current.password))
            }
            preferences.edit()
                .putString("token", response.access_token)
                .putString("serverUrl", current.serverUrl.trim())
                .apply()
            _state.value = current.copy(token = response.access_token, password = "", message = null)
            sync()
        }
    }

    fun sync() = viewModelScope.launch {
        val token = _state.value.token ?: return@launch
        runRequest {
            val api = api()
            val response = api.sync("Bearer $token")
            val selectedListId = _state.value.selectedListId
            val nextSelected = response.lists.firstOrNull { it.id == selectedListId }?.id ?: response.lists.firstOrNull()?.id
            _state.value = _state.value.copy(
                lists = response.lists,
                selectedListId = nextSelected,
                message = null
            )
        }
    }

    fun createList(name: String) = viewModelScope.launch {
        val token = _state.value.token ?: return@launch
        runRequest {
            val api = api()
            api.createList("Bearer $token", ListCreate(name))
            sync()
        }
    }

    fun createItem(name: String, quantity: String) = viewModelScope.launch {
        val token = _state.value.token ?: return@launch
        val listId = _state.value.selectedListId ?: return@launch
        runRequest {
            val api = api()
            api.createItem("Bearer $token", listId, ItemCreate(name, quantity))
            sync()
        }
    }

    fun toggleItem(itemId: Int, checked: Boolean) = viewModelScope.launch {
        val token = _state.value.token ?: return@launch
        runRequest {
            val api = api()
            api.updateItem("Bearer $token", itemId, ItemUpdate(is_checked = checked))
            sync()
        }
    }

    fun shareList(email: String) = viewModelScope.launch {
        val token = _state.value.token ?: return@launch
        val listId = _state.value.selectedListId ?: return@launch
        runRequest {
            val api = api()
            api.shareList("Bearer $token", listId, ShareRequest(email))
            _state.value = _state.value.copy(message = "Список открыт для $email")
        }
    }

    fun addCatalogProduct(name: String) {
        val normalizedName = name.trim()
        if (normalizedName.isBlank()) return
        val catalog = _state.value.productCatalog
        if (catalog.any { it.equals(normalizedName, ignoreCase = true) }) return
        saveProductCatalog((catalog + normalizedName).sortedWith(String.CASE_INSENSITIVE_ORDER))
    }

    fun removeCatalogProduct(name: String) {
        saveProductCatalog(_state.value.productCatalog.filterNot { it == name })
    }

    fun selectList(listId: Int) = update { copy(selectedListId = listId) }

    private suspend fun runRequest(block: suspend () -> Unit) {
        _state.value = _state.value.copy(isLoading = true, message = null)
        try {
            block()
        } catch (error: Exception) {
            _state.value = _state.value.copy(message = error.message ?: "Ошибка")
        } finally {
            _state.value = _state.value.copy(isLoading = false)
        }
    }

    private fun update(block: ShoppingUiState.() -> ShoppingUiState) {
        _state.value = _state.value.block()
    }

    private fun api() = ApiClient.create(_state.value.serverUrl)

    private fun loadProductCatalog(): List<String> {
        val stored = preferences.getString("productCatalog", null)
        return stored
            ?.split("\n")
            ?.map { it.trim() }
            ?.filter { it.isNotBlank() }
            ?.distinct()
            ?.sortedWith(String.CASE_INSENSITIVE_ORDER)
            ?: defaultProducts
    }

    private fun saveProductCatalog(catalog: List<String>) {
        val cleanedCatalog = catalog
            .map { it.trim() }
            .filter { it.isNotBlank() }
            .distinct()
            .sortedWith(String.CASE_INSENSITIVE_ORDER)
        preferences.edit().putString("productCatalog", cleanedCatalog.joinToString("\n")).apply()
        _state.value = _state.value.copy(productCatalog = cleanedCatalog)
    }
}
