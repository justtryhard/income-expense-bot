def is_positive_int(value: str) -> bool:
    """
    Валидатор
    Проверка, что строка состоит только из цифр и число положительное
    """
    return value.isdigit() and int(value) > 0