from ladybug.model import Table, Field


class ExampleTable(Table):
    name = Field()
    salary = Field(format=int)
    department = Field()

table = ExampleTable.open("example.csv")
print table.group_by("department")
print table.group_by("department", key="name")
print table.group_by("department", key="name", function=lambda g: len(list(g)))
print table.group_by("department", function=sum, key="salary")
table.filter(department="IT").update(salary=2700)
print table.group_by("department", function=sum, key="salary")

table.insert(name="Carlos", salary=6000, department="Management")
table.save("example_output.csv", delimiter=";")
print table.group_by("department", key="name")
try:
    table.filter(department="Management").insert(
        name="Carlos", salary=6000, department="Management")
except ValueError:
    print "Inserting like that is not possible"

cc_table = table.copy
print list(table.filter(name="Maria").rows)
print list(cc_table.filter(name="Maria").rows)
cc_table.filter(name="Maria").update(department="IT")
print list(table.filter(name="Maria").rows)
print list(cc_table.filter(name="Maria").rows)

additional_rows = [
    {"first_name": "James", "cost": 6000, "department": "Management"},
    {"first_name": "Cecilia", "cost": 5000, "department": "Marketing"},
]

table.append_rows(
    additional_rows, name="first_name", salary="cost", department="department")
print table.group_by("department", key="name")
