from collections import UserDict
from typing import List, Tuple
import re
from datetime import datetime, date


class Field:
    def __init__(self, value) -> None:
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Name(Field):
    @Field.value.setter
    def value(self, name: str):
        if not isinstance(name, str):
            raise TypeError('Name must be a string')
        if not re.match(r'^[a-zA-Z]{1,20}$', name):
            raise ValueError('Name must contain only letters and be 1-20 symbols long')
        self._value = name


class Phone(Field):
    @Field.value.setter
    def value(self, phone: str):
        if not isinstance(phone, str):
            raise TypeError('Phone must be a string')
        if not re.match(r'^[0-9]{10}$', phone):
            raise ValueError('Phone must contain only digits and be 10 symbols long')
        self._value = phone


class Birthday(Field):
    @Field.value.setter
    def value(self, value: str):
        try:
            self._value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError or TypeError:
            raise ValueError('Birthday must contain date in format DD.MM.YYYY!')

    def __repr__(self):
        return f'{self.value}'


class Record:
    def __init__(self, name: Name, phones: List[Phone] = [], birthday: Birthday = None) -> None:
        self.name = name
        self.phones = phones
        self.birthday = birthday

    def add_phone(self, phone: Phone) -> Phone | None:
        if phone.value not in [p.value for p in self.phones]:
            self.phones.append(phone)
            return phone

    def del_phone(self, phone: Phone) -> Phone | None:
        for p in self.phones:
            if p.value == phone.value:
                self.phones.remove(p)
                return p

    def change_phone(self, phone, new_phone) -> tuple[Phone, Phone] | None:
        if self.del_phone(phone):
            self.add_phone(new_phone)
            return phone, new_phone

    def add_birthday(self, birthday: Birthday):
        if birthday:
            self.birthday = birthday

    def days_to_birthday(self):
        date_today = date.today()
        birthday_date = date(date_today.year, self.birthday.value.month, self.birthday.value.day)
        if birthday_date < date_today:
            birthday_date = date(date_today.year + 1, self.birthday.value.month, self.birthday.value.day)
        return (birthday_date - date_today).days

    def __repr__(self):
        if self.birthday:
            return f'{", ".join([p.value for p in self.phones])} Birthday: {self.birthday}'
        return f'{", ".join([p.value for p in self.phones])}'


class AddressBook(UserDict):
    def add_record(self, record: Record) -> Record | None:
        if not self.data.get(record.name.value):
            self.data[record.name.value] = record
            return record

    def del_record(self, key: str) -> Record | None:
        rec = self.data.get(key)
        if rec:
            self.data.pop(key)
            return rec

    def iterator(self, n):
        count = 0
        for i in self.data:
            if count < n:
                yield self.data[i]
                count += 1
        else:
            raise StopIteration


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Please enter the contact like this:\nName: number"
        except KeyError:
            return "This contact doesn't exist."
        except ValueError:
            return "Phone must contain only digits and be 10 symbols long"

    return inner


def greeting(*args):
    return "How can I help you?"


def to_exit(*args):
    return "Good bye"


notebook = AddressBook()


@input_error
def add_contact(*args):
    rec = Record(Name(args[0]), [Phone(args[1])])
    notebook.add_record(rec)
    try:
        rec.add_birthday(Birthday(args[2]))
    except IndexError:
        birthday = None
    return f"Contact {rec.name.value} has added successfully."


@input_error
def change_number(*args):
    rec = notebook.get(args[0])
    if rec:
        rec.change_phone(Phone(args[1]), Phone(args[2]))
        return f'Contact {rec.name.value} has changed successfully.'
    return f'Contact, with name {args[0]} not in notebook.'


@input_error
def del_number(*args):
    rec = notebook.get(args[0])
    if rec:
        rec.del_phone(Phone(args[1]))
        return f'Contact {args[1]} has deleted successfully from contact {rec.name.value}.'
    return f'Contact, with name {args[0]} not in notebook.'


@input_error
def print_phone(*args):
    return notebook[args[0]]


@input_error
def del_contact(*args):
    rec = notebook.del_record(args[0])
    if rec:
        return f'Contact {rec.name.value} has deleted successfully.'
    return f'Contact, with name {args[0]} not in notebook.'


def show_all(*args):
    return "\n".join([f"{k.title()}: {v}" for k, v in notebook.items()]) if len(notebook) > 0 else 'Contacts are empty'


@input_error
def days_to_births(*args):
    rec = notebook.get(args[0])
    if rec:
        return f'{rec.name.value.title()} has {rec.days_to_birthday()} days to birthday.'
    return f'Contact, with name {args[0]} not in notebook.'


all_commands = {
    greeting: ["hello", "hi"],
    add_contact: ["add", "new", "+"],
    change_number: ["change", ],
    print_phone: ["phone", "number"],
    show_all: ["show all", "show"],
    to_exit: ["good bye", "close", "exit", ".", "bye"],
    del_number: ["del", "delete", "-"],
    del_contact: ["remove", ],
    days_to_births: ["days", "birthday"]
}


def command_parser(user_input: str):
    for key, value in all_commands.items():
        for i in value:
            if user_input.lower().startswith(i.lower()):
                return key, user_input[len(i):].strip().split()


def main():
    while True:
        user_input = input(">>> ")
        command, parser_data = command_parser(user_input)
        print(command(*parser_data))
        if command is to_exit:
            break


if __name__ == "__main__":
    main()
