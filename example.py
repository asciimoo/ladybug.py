from ladybug.model import Table, Field


class ExampleTable(Table):
    name = Field()
    salary = Field(format=int)
    department = Field()

table = ExampleTable.open("example.csv")
print table.group_by("department")
print table.group_by("department", key="name")
print table.group_by("department", function=sum, key="salary")
table.filter(department="IT").update(salary=2700)
print table.group_by("department", function=sum, key="salary")
