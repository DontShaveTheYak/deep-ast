def func_a():
    print("foo")


def func_b():
    func_a()


def func_c():
    print("bar")


def func_d():
    func_a()
    func_c()
