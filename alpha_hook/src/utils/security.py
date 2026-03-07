# alpha_hook/src/utils/security.py
import hmac
import hashlib
from typing import Dict


def verify_alfa_callback_signature(
        params: Dict[str, str],
        secret_key: str,
        received_checksum: str
) -> bool:
    """
    Валидация подписи callback от Альфа-Банка (симметричная криптография).

    Алгоритм:
    1. Удалить checksum и sign_alias из параметров
    2. Отсортировать по ключу (алфавит)
    3. Сформировать строку: key1;value1;key2;value2;...;
    4. HMAC-SHA256 от строки с secret_key
    5. Сравнить с received_checksum (верхний регистр)
    """
    if not received_checksum:
        return False

    # 1. Исключаем служебные поля
    filtered = {
        k: v for k, v in params.items()
        if k not in ('checksum', 'sign_alias')
    }

    # 2. Сортировка по ключу
    sorted_items = sorted(filtered.items(), key=lambda x: x[0])

    # 3. Формирование строки для хеша
    signature_string = ";".join(
        f"{k};{v}" for k, v in sorted_items
    ) + ";"  # ← важно: точка с запятой в конце!

    # 4. Вычисление HMAC-SHA256
    expected = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=signature_string.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest().upper()  # ← верхний регистр!

    # 5. Сравнение (constant-time)
    return hmac.compare_digest(expected, received_checksum.upper())