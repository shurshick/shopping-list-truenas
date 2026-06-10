package com.shoppinglist.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.shoppinglist.mobile.ui.ShoppingUiState
import com.shoppinglist.mobile.ui.ShoppingViewModel

class MainActivity : ComponentActivity() {
    private val viewModel: ShoppingViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    val state by viewModel.state.collectAsState()
                    if (state.token == null) {
                        LoginScreen(state, viewModel::setEmail, viewModel::setPassword, viewModel::login)
                    } else {
                        ShoppingScreen(
                            state,
                            viewModel::sync,
                            viewModel::selectList,
                            viewModel::createList,
                            viewModel::createItem,
                            viewModel::toggleItem,
                            viewModel::shareList
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun LoginScreen(
    state: ShoppingUiState,
    onEmail: (String) -> Unit,
    onPassword: (String) -> Unit,
    onLogin: (Boolean) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(20.dp),
        verticalArrangement = Arrangement.Center
    ) {
        Text("Список покупок", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(24.dp))
        OutlinedTextField(state.email, onEmail, label = { Text("Email") }, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(8.dp))
        OutlinedTextField(
            state.password,
            onPassword,
            label = { Text("Пароль") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(Modifier.height(16.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { onLogin(false) }, enabled = !state.isLoading) { Text("Войти") }
            Button(onClick = { onLogin(true) }, enabled = !state.isLoading) { Text("Регистрация") }
        }
        state.message?.let {
            Spacer(Modifier.height(12.dp))
            Text(it, color = MaterialTheme.colorScheme.error)
        }
    }
}

@Composable
private fun ShoppingScreen(
    state: ShoppingUiState,
    onSync: () -> Unit,
    onSelectList: (Int) -> Unit,
    onCreateList: (String) -> Unit,
    onCreateItem: (String, String) -> Unit,
    onToggleItem: (Int, Boolean) -> Unit,
    onShareList: (String) -> Unit
) {
    var listName by remember { mutableStateOf("") }
    var itemName by remember { mutableStateOf("") }
    var quantity by remember { mutableStateOf("") }
    var shareEmail by remember { mutableStateOf("") }
    val selectedList = state.lists.firstOrNull { it.id == state.selectedListId }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
            Text("Покупки", style = MaterialTheme.typography.headlineSmall)
            Button(onClick = onSync, enabled = !state.isLoading) { Text("Обновить") }
        }

        Spacer(Modifier.height(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            OutlinedTextField(listName, { listName = it }, label = { Text("Новый список") }, modifier = Modifier.weight(1f))
            Button(onClick = {
                if (listName.isNotBlank()) {
                    onCreateList(listName.trim())
                    listName = ""
                }
            }) { Text("+") }
        }

        Spacer(Modifier.height(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            state.lists.forEach { list ->
                FilterChip(
                    selected = list.id == state.selectedListId,
                    onClick = { onSelectList(list.id) },
                    label = { Text(list.name) }
                )
            }
        }

        Spacer(Modifier.height(12.dp))
        if (selectedList != null) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                OutlinedTextField(shareEmail, { shareEmail = it }, label = { Text("Email для доступа") }, modifier = Modifier.weight(1f))
                Button(onClick = {
                    if (shareEmail.isNotBlank()) {
                        onShareList(shareEmail.trim())
                        shareEmail = ""
                    }
                }) { Text("Открыть") }
            }

            Spacer(Modifier.height(12.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                OutlinedTextField(itemName, { itemName = it }, label = { Text("Товар") }, modifier = Modifier.weight(1f))
                OutlinedTextField(quantity, { quantity = it }, label = { Text("Кол-во") }, modifier = Modifier.weight(0.7f))
                Button(onClick = {
                    if (itemName.isNotBlank()) {
                        onCreateItem(itemName.trim(), quantity.trim())
                        itemName = ""
                        quantity = ""
                    }
                }) { Text("+") }
            }

            LazyColumn(modifier = Modifier.fillMaxWidth().padding(top = 12.dp)) {
                items(selectedList.items) { item ->
                    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                        Checkbox(
                            checked = item.is_checked,
                            onCheckedChange = { checked -> onToggleItem(item.id, checked) }
                        )
                        Text(
                            text = listOf(item.name, item.quantity).filter { it.isNotBlank() }.joinToString(" - "),
                            style = MaterialTheme.typography.bodyLarge
                        )
                    }
                }
            }
        } else {
            Text("Создайте первый список покупок.")
        }

        state.message?.let {
            Spacer(Modifier.height(8.dp))
            Text(it, color = MaterialTheme.colorScheme.error)
        }
    }
}
