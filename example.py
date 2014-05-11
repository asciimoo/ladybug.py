from ladybug.model import Table, Field


class ExampleTable(Table):
    columns = ("name", "salary")

    name = Field()
    salary = Field(format=int)

print sum(ExampleTable.open("example.csv").column("salary"))
