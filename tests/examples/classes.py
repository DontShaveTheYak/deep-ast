class Human:
    pass


class Parent(Human):
    def example_a():
        pass


class Child(Parent):
    def example_a():
        print("foo")
        super().example_a()


class Foo:
    def method_a(self):
        print("foo")

    def method_b(self):
        self.method_a()

    def method_c(self):
        bar = Bar()
        bar.bazz()


class Bar:
    def bazz(self):
        print("bazz")
