import logging
import time
from functools import wraps


def b62(number):
    """
    将非负整数转换为 62 进制字符串

    参数：
        number：要转换的非负整数

    返回值：
        转换后的 62 进制字符串

    使用示例：
        >>> b62(999999) = '21b8xv'
    """
    if number < 10 and number > -10:
        return str(number)

    # 62 进制字符集
    characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # 判断输入是否为非负整数
    if not isinstance(number, int) or number < 0:
        raise ValueError("Input must be a non-negative integer")

    # 特殊情况：如果输入为0，则直接返回第一个字符
    if number == 0:
        return characters[0]

    base62 = ""
    while number:
        number, remainder = divmod(number, 62)
        base62 = characters[remainder] + base62

    return base62


def log_execution_time(min_time=0, log_level=logging.INFO):
    """装饰器：记录函数执行时间并打印日志信息

    Args:
        min_time (float, optional): 最小记录时间. Defaults to 0.
        log_level (int, optional): 日志级别. Defaults to logging.INFO.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error executing {func.__name__}: {str(e)}")
                raise
            end_time = time.time()
            execution_time = end_time - start_time
            if execution_time >= min_time:
                logging.log(
                    log_level,
                    f"Function {func.__name__} executed in {execution_time:.4f} seconds",
                )
            return result

        return wrapper

    return decorator
