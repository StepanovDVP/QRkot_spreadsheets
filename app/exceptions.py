class MaxRowsExceededError(Exception):
    """
    Исключение для случаев,
    когда количество строк
    превышает допустимое значение.
    """
    pass


class MaxColumnsExceededError(Exception):
    """
    Исключение для случаев,
    когда количество столбцов в строке
    превышает допустимое значение.
    """
    pass
