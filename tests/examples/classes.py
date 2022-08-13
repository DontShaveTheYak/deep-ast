class Human:
    pass


class Parent(Human):
    def example_a():
        pass


class Child(Parent):
    def example_a():
        print("foo")
        super().example_a()
