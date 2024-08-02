import pickle
from collections import UserDict
import re
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not re.fullmatch(r'\d{10}', value):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if p.value != phone_number]

    def edit_phone(self, old_phone, new_phone):
        for idx, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                return
        raise ValueError("Old phone number not found.")

    def find_phone(self, phone_number):
        for p in self.phones:
            if p.value == phone_number:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        today = datetime.today()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value.replace(year=today.year)
                if today <= birthday <= today + timedelta(days=days):
                    upcoming.append(record)
        return upcoming

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Enter the argument for the command."
    return inner

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Give me name and phone please."
    name, phone = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        return "Give me name and birthday please."
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday for '{name}' added: {birthday}."
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book: AddressBook):
    if len(args) < 1:
        return "Give me name please."
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"Birthday for '{name}': {record.birthday.value.strftime('%d.%m.%Y')}."
    else:
        return "Birthday not found or contact not found."

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return "\n".join(str(record) for record in upcoming)
    else:
        return "No upcoming birthdays."

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip()
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)  # Збереження даних при виході
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            if len(args) == 3:
                name, old_phone, new_phone = args
                record = book.find(name)
                if record:
                    try:
                        record.edit_phone(old_phone, new_phone)
                        print(f"Phone number for '{name}' updated from {old_phone} to {new_phone}.")
                    except ValueError as e:
                        print(e)
                else:
                    print("Contact not found.")
            else:
                print("Give me name, old phone, and new phone please.")

        elif command == "phone":
            if len(args) == 1:
                name = args[0]
                record = book.find(name)
                if record:
                    print(f"Phone numbers for '{name}': {'; '.join(p.value for p in record.phones)}")
                else:
                    print("Contact not found.")
            else:
                print("Give me name please.")

        elif command == "all":
            if book.data:
                for name, record in book.data.items():
                    print(record)
            else:
                print("No contacts found.")

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        elif command == "delete":
            if len(args) == 1:
                name = args[0]
                book.delete(name)
                print(f"Contact '{name}' deleted.")
            else:
                print("Give me name please.")
        else:
            print("Invalid command. Please try again.")

@input_error
def parse_input(command_input):
    parts = command_input.split(maxsplit=1)
    if len(parts) == 0:
        raise IndexError
    command = parts[0]
    args = parts[1].split() if len(parts) > 1 else []
    return command, args

if __name__ == "__main__":
    main()