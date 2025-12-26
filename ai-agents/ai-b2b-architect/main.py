

def f(x: float) -> float:
    """f(x)=x^4+x-3"""

    return x ** 4 + x - 3


def dir_f(x: float) -> float:
    return -1 * (3 - x) ** 0.25


print(dir_f(-1.4526))
