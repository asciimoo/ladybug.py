# This module provides a Table class for CSV files, that works
# similarly to Django models.
from csv import DictReader, DictWriter
import itertools


def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K


class Table(object):
    """A model for handling a CSV file"""
    columns = None

    def __init__(self):
        super(Table, self).__init__()
        self.initalize_fields()
        if self.columns is None:
            self.columns = list(sorted(
                (name for name, _ in self.fields),
                key=lambda f: self.get_field(f)[1].field_order_id
            ))

    @property
    def fields(self):
        return (
            self.get_field(name)
            for name in dir(self)
            if isinstance(getattr(self, name), Field)
        )

    @classmethod
    def get_field(self, name):
        return (name, getattr(self, name))

    def initalize_fields(self):
        for name, member in self.fields:
            if member.column is None:
                member.column = name

    @classmethod
    def manager(cls):
        return Manager(cls)

    @classmethod
    def open(cls, csvfile, **kwargs):
        fieldnames = cls().columns
        manager = Manager(cls)
        with open(csvfile) as csvfile:
            manager.read_data(DictReader(csvfile, fieldnames, **kwargs))
        return manager

    @classmethod
    def create(cls):
        return Manager(cls)

    @property
    def result_class(self):
        other_class = self.__class__

        class result_class(dict):
            def __init__(self, row):
                super(result_class, self).__init__()
                self.row = row
                other = other_class()
                for name in other.columns:
                    value = row[name]
                    self.update({name: other.get_field(name)[1](value)})

            def copy(self):
                return dict(self.iteritems())

        result_class.__name__ = self.__class__.__name__ + "Object"
        return result_class


class BaseField(object):
    """Base class for fields"""
    _counter = itertools.count()

    def __init__(self):
        super(BaseField, self).__init__()
        self.field_order_id = self._counter.next()


class Field(BaseField):
    """A field that's mapped to a column of a CSV file"""
    def __init__(self, format=str, column=None):
        super(Field, self).__init__()
        self.format = format
        self.column = column

    def __call__(self, value):
        return self.format(value)


class Manager(object):
    """A manager for an opened CSV file based on a Table"""
    def __init__(self, model, data=None, include=None):
        super(Manager, self).__init__()
        self.model = model()
        self._data = data
        if include is not None:
            self._include = include
        else:
            self._include = list(range(len(data))) if data else list()

    def read_data(self, reader):
        self._data = list()
        self._include = list()
        index = 0
        for row in reader:
            self._data.append(self.model.result_class(row))
            self._include.append(index)
            index += 1

    @property
    def rows(self):
        return (self._data[i] for i in self._include)

    @property
    def copy(self):
        new_data = list(row.copy() for row in self.rows)
        new_include = list(range(len(new_data)))
        return Manager(
            model=self.model.__class__, data=new_data, include=new_include)

    def __iter__(self):
        return self.rows

    def save(self, csvfile, **kwargs):
        fieldnames = self.model.columns
        with open(csvfile, "w") as csvfile:
            writer = DictWriter(csvfile, fieldnames,  **kwargs)
            for row in self.rows:
                writer.writerow({
                    column: row[column] for column in fieldnames
                })

    def column(self, column):
        return [x[column] for x in self.rows]

    def update(self, **kwargs):
        for index in self._include:
            for name in kwargs:
                self._data[index][name] = kwargs[name]

    def insert(self, **kwargs):
        if len(self._data) == len(self._include):
            self._data.append(self.model.result_class(kwargs))
            self._include.append(len(self._include))
        else:
            raise ValueError("Cannot insert into filtered results")

    def __getitem__(self, key):
        return self.column(key)

    def filter(self, **kwargs):
        new_include = list()
        for index in self._include:
            if all(
                self._data[index][name] == value
                for name, value in kwargs.iteritems()
            ):
                new_include.append(index)
        return Manager(
            self.model.__class__, data=self._data, include=new_include)

    def order_by(self, *args):
        def cmp(a, b):
            a, b = self._data[a], self._data[b]
            for arg in args:
                if a[arg] > b[arg]:
                    return 1
                elif a[arg] < b[arg]:
                    return -1
                else:
                    continue
            return 0

        new_include = list(sorted(
            self._include, key=cmp_to_key(cmp)
        ),)

        return Manager(
            self.model.__class__, data=self._data, include=new_include)

    @property
    def reverse(self):
        new_include = list(self._include)
        new_include.reverse()

        return Manager(
            self.model.__class__, data=self._data, include=new_include)

    def group_by(self, column, function=list, key=None):
        if key:
            def func(rows):
                return function(row[key] for row in rows)
        else:
            func = function
        unique_values = set(row[column] for row in self)
        return {
            row: func(r for r in self if r[column] == row)
            for row in unique_values
        }
