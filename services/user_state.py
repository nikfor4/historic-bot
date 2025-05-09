# services/user_state.py

# Хранение состояния пользователей
user_states = {}

def get_user_state(user_id):
    """Возвращает состояние пользователя по ID."""
    return user_states.get(user_id)

def set_user_state(user_id, state):
    """Устанавливает состояние для пользователя."""
    user_states[user_id] = state

def clear_user_state(user_id):
    """Удаляет состояние пользователя по ID."""
    if user_id in user_states:
        del user_states[user_id]
