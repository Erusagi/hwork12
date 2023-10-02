from datetime import datetime
import pickle
import os

def save_address_book(address_book, filename):
    try:
        with open(filename, "wb") as file:
            pickle.dump(address_book, file)
        print(f"Address book saved to {filename}.")
    except Exception as e:
        print(f"Error saving address book: {e}")

def load_address_book(filename):
    try:
        if os.path.exists(filename):
            with open(filename, "rb") as file:
                return pickle.load(file)
        else:
            print(f"File '{filename}' not found. Creating a new address book.")
            return AddressBook()
    except Exception as e:
        print(f"Error loading address book: {e}")
        return AddressBook()
class Field:
    def __init__(self, value=None):
        self.value = value

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value=None):
        if value and not self.validate_phone(value):
            raise ValueError("Invalid phone number format")
        super().__init__(value)

    def validate_phone(self, phone):
        return len(phone) == 10 and phone.isdigit()

    def set_value(self, value):
        if not self.validate_phone(value):
            raise ValueError("Invalid phone number format")
        super().set_value(value)


class Birthday(Field):
    def __init__(self, value=None):
        if value and not self.validate_birthday(value):
            raise ValueError("Invalid birthday format")
        super().__init__(value)

    def validate_birthday(self, birthday):
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def set_value(self, value):
        if not self.validate_birthday(value):
            raise ValueError("Invalid birthday format")
        super().set_value(value)


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        if Phone.validate_phone(new_phone):
            for phone in self.phones:
                if phone.value == old_phone:
                    phone.value = new_phone
                    return
            raise ValueError("Phone not found")
        else:
            raise ValueError("Invalid phone number format")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def days_to_birthday(self):
        if self.birthday.get_value():
            today = datetime.today()
            birthdate = datetime.strptime(self.birthday.get_value(), "%Y-%m-%d")
            next_birthday = datetime(today.year, birthdate.month, birthdate.day)
            if today > next_birthday:
                next_birthday = next_birthday.replace(year=today.year + 1)
            days_until_birthday = (next_birthday - today).days
            return days_until_birthday
        else:
            return None


from collections import UserDict


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.page_size = 10

    def add_record(self, record):
        self.data[record.name.get_value()] = record

    def find(self, name):
        if name in self.data:
            return self.data[name]
        else:
            return None

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self):
        records = list(self.data.values())
        total_records = len(records)
        current_index = 0

        while current_index < total_records:
            yield records[current_index:current_index + self.page_size]
            current_index += self.page_size


def main():
    address_book = load_address_book("address_book.pkl")

    while True:
        user_input = input("Enter a command: ").strip().lower()

        if user_input == "hello":
            print("How can I help you?")
        elif user_input.startswith("add"):
            _, name, *phones = user_input.split()
            birthday = None
            for item in phones:
                if "-" in item:
                    birthday = item
                    phones.remove(item)
                    break
            if name in address_book:
                record = address_book[name]
                for phone in phones:
                    record.add_phone(phone)
                if birthday:
                    record.birthday.set_value(birthday)
            else:
                record = Record(name, birthday)
                for phone in phones:
                    record.add_phone(phone)
                address_book.add_record(record)
            print(f"Record for {name} added.")
        elif user_input.startswith("change"):
            _, name, old_phone, new_phone = user_input.split()
            if name in address_book:
                record = address_book[name]
                if record.find_phone(old_phone):
                    record.edit_phone(old_phone, new_phone)
                    print(f"Phone number for {name} changed to {new_phone}")
                else:
                    print(f"Phone number {old_phone} not found in {name}'s record.")
            else:
                print(f"Record for {name} not found.")
        elif user_input.startswith("phone"):
            _, name = user_input.split()
            if name in address_book:
                record = address_book[name]
                if record.phones:
                    print(f"The phone numbers for {name} are:")
                    for phone in record.phones:
                        print(phone.value)
                else:
                    print(f"No phone numbers found for {name}.")
            else:
                print(f"Record for {name} not found.")
        elif user_input == "show all":
            if address_book:
                print("All contacts:")
                for name, record in address_book.items():
                    print(f"{name}:")
                    if record.phones:
                        for phone in record.phones:
                            print(f"  {phone.value}")
                    birthday = record.birthday.get_value()
                    if birthday:
                        print(f"  Birthday: {birthday}")
            else:
                print("The contact book is empty.")
        elif user_input.startswith("delete"):
            _, name = user_input.split()
            if name in address_book:
                address_book.delete(name)
                print(f"Record for {name} deleted.")
            else:
                print(f"Record for {name} not found.")
        elif user_input.startswith("birthday"):
            _, name = user_input.split()
            if name in address_book:
                record = address_book[name]
                days = record.days_to_birthday()
                if days is not None:
                    print(f"Days until {name}'s next birthday: {days}")
                else:
                    print(f"{name} doesn't have a birthday date set.")
            else:
                print(f"Record for {name} not found.")
        elif user_input == "show pages":
            for i, page in enumerate(address_book.iterator(), start=1):
                print(f"Page {i}:")
                for record in page:
                    print(f"  {record.name.get_value()}")
        elif user_input in ["good bye", "close", "exit"]:
            print("Good bye!")
            break
        else:
            print("Invalid command. Please try again.")


if __name__ == "__main__":
    main()