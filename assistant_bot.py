from collections import UserDict # Імпортуємо UserDict для створення адресної книги
from datetime import datetime, timedelta # Імпортуємо datetime для роботи з датами
import pickle # Імпортуємо pickle для серіалізації та десеріалізації даних
import os # Імпортуємо os для перевірки наявності файлу


# Файл для збереження
DEFAULT_FILENAME = "address_book.pkl"

# Базовий клас для всіх полів
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


# Клас для імені контакту
class Name(Field):
    pass


# Клас для телефонного номера
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


# Клас для дати народження
class Birthday(Field):
    def __init__(self, value):
        try:
            birthday_date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

        if birthday_date > datetime.today().date():
            raise ValueError("Birthday cannot be in the future.")

        super().__init__(value)


# Клас для запису контакту
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # Метод для додавання телефону
    def add_phone(self, phone):
        if self.find_phone(phone):
            return False
        try:
            self.phones.append(Phone(phone))
        except ValueError:
            return False
        return True

    # Метод для видалення телефону
    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
            return True
        return False

    # Метод для редагування телефону
    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            try:
                self.phones.remove(phone_obj)
                self.phones.append(Phone(new_phone))
                return True
            except ValueError:
                return False
        return False

    # Метод для пошуку телефону
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    # Метод для додавання дати народження
    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)

    # Метод для редагування дати народження
    def edit_birthday(self, new_birthday):
        self.birthday = Birthday(new_birthday)

    # Метод для видалення дати народження
    # Якщо дата народження не встановлена, нічого не робимо
    def remove_birthday(self):
        self.birthday = None

    # Метод для отримання дати народження
    def __str__(self):
        phones_str = "; ".join(str(p) for p in self.phones)
        birthday_str = f", Birthday: {self.birthday}" if self.birthday else ""
        return f"{self.name.value}: {phones_str}{birthday_str}"


# Клас для адресної книги, що наслідує UserDict
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    
    # Метод для пошуку контакту за іменем
    def find(self, name):
        name = name.lower()
        for key, record in self.data.items():
            if key.lower() == name:
                return record
        return None
    
    # Метод для перевірки наявності контакту за іменем
    def name_exists(self, name):
        return any(name.lower() == key.lower() for key in self.data)
    
    # Метод для видалення контакту за іменем
    def delete(self, name):
        for key in list(self.data):
            if key.lower() == name.lower():
                del self.data[key]
                return True
        return False
    
    # Метод для пошуку контактів за іменем або телефоном
    def search(self, query):
        result = []
        query = query.lower()
        for record in self.data.values(): 
            name_match = record.name.value.lower().startswith(query)
            phone_match = any(query in phone.value for phone in record.phones)
            if name_match or phone_match:
                result.append(str(record))
        return result
    
    # Метод для отримання майбутніх днів народження
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        end_date = today + timedelta(days=7)
        upcoming = []

        for record in self.data.values():
            if not record.birthday:
                continue
            try:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if today <= birthday_this_year <= end_date: # Перевіряємо, чи день народження в межах наступних 7 днів
                    congratulation_date = birthday_this_year
                    if congratulation_date.weekday() == 5:  # Субота
                        # Якщо день народження припадає на суботу, переносимо на понеділок
                        congratulation_date += timedelta(days=2)
                    elif congratulation_date.weekday() == 6:  # Неділя
                        # Якщо день народження припадає на неділю, переносимо на понеділок
                        congratulation_date += timedelta(days=1)

                    upcoming.append(f"{record.name.value}: {congratulation_date.strftime('%d.%m.%Y')}")
            except ValueError:
                continue

        return upcoming



# Збереження та завантаження

# Функція для збереження адресної книги у файл
def save_address_book(book, filename=DEFAULT_FILENAME):
    try:
        with open(filename, "wb") as file:
            pickle.dump(book, file)
    except Exception as e:
        print(f"Error saving address book to '{filename}': {e}")

# Функція для завантаження адресної книги з файлу
def load_address_book(filename=DEFAULT_FILENAME):
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as file:
             return pickle.load(file)
        except Exception as e:
            print(f"Error while loading address book from '{filename}': {e}")
            print("Creating a new empty address book instead.")
            return AddressBook()
    return AddressBook()


# Функція для розбору введення користувача
def parse_input(user_input):
    cmd, *args = user_input.strip().split()
    return cmd.strip().lower(), args


# Функція для нормалізації імені контакту
def normalize_name(name):
    def fix_part(part):
        return "-".join(subpart.capitalize() for subpart in part.split("-"))

    return " ".join(fix_part(word) for word in name.strip().split())


# Декоратор для обробки помилок введення, які можуть виникнути під час виконання функцій
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Missing input. Please provide valid arguments."
    return inner


# Декоратор для обробки помилок введення
@input_error
def add_contact(args, book): # Функція для додавання нового контакту
    if len(args) < 2:
        raise ValueError("Please enter name and at least one phone number.")

    # Шукаємо перший телефон — число з 10 цифрами
    phone_start_index = None
    for i, arg in enumerate(args):
        if arg.isdigit() and len(arg) == 10:
            phone_start_index = i
            break

    if phone_start_index is None: # Якщо не знайдено жодного телефону з 10 цифрами
        raise ValueError("At least one valid phone number required (10 digits).")

    name_parts = args[:phone_start_index]
    phones = args[phone_start_index:]

    if not name_parts: # Якщо ім'я не вказано
        raise ValueError("Name is missing.")

    name = normalize_name(" ".join(name_parts))

    if book.name_exists(name):
        return "Contact with this name already exists."

    record = Record(name)

    for phone in phones:
        try:
            if not record.add_phone(phone):
                return f"Phone number '{phone}' already exists."
        except ValueError:
            return f"Invalid phone number '{phone}'. Must contain exactly 10 digits."

    book.add_record(record)
    return "Contact added."


@input_error
def edit_contact_name(args, book): # Функція для зміни імені контакту
    if len(args) < 2:
        raise ValueError("Please provide old and new full names.")

    # Знаходимо позицію першого імені, що вже є в книзі
    for i in range(1, len(args)):
        old_name_try = normalize_name(" ".join(args[:i]))
        if book.name_exists(old_name_try):
            old_name = old_name_try
            new_name = normalize_name(" ".join(args[i:]))
            break
    else:
        raise KeyError("Contact not found.")

    record = book.find(old_name)
    book.delete(old_name)
    record.name = Name(new_name)
    book.add_record(record)

    return f"Contact name changed to '{new_name}'."


@input_error
def change_contact(args, book): # Функція для зміни телефону контакту
    if len(args) < 3:
        raise ValueError("Please provide full name, old phone, and new phone.")
    
    old_phone = args[-2]
    new_phone = args[-1]

    if not (old_phone.isdigit() and len(old_phone) == 10):
        raise ValueError("Old phone number must be 10 digits.")
    if not (new_phone.isdigit() and len(new_phone) == 10):
        raise ValueError("New phone number must be 10 digits.")

    name = normalize_name(" ".join(args[:-2]))

    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")

    if not record.edit_phone(old_phone, new_phone):
        return f"Old phone number '{old_phone}' not found or new number invalid."

    return "Phone number updated."


@input_error
def add_phone_to_contact(args, book): # Функція для додавання телефону до контакту
    if len(args) < 2:
        raise ValueError("Please provide name and phone number to add.")
    
    possible_phone = args[-1] # Останній аргумент вважаємо телефоном
    if not possible_phone.isdigit() or len(possible_phone) != 10:
        raise ValueError("Please provide a valid phone number (10 digits).")

    name = normalize_name(" ".join(args[:-1])) # Все, що перед останнім аргументом, вважаємо іменем
    phone = possible_phone

    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")

    if record.add_phone(phone):
        return "Phone number added."
    else:
        return f"Phone number '{phone}' already exists for this contact."


@input_error
def remove_phone(args, book): # Функція для видалення телефону з контакту
    if len(args) < 2:
        raise ValueError("Please provide full name and phone number to remove.")
    
    possible_phone = args[-1]
    if not possible_phone.isdigit() or len(possible_phone) != 10:
        raise ValueError("Please provide a valid phone number (10 digits).")

    name = normalize_name(" ".join(args[:-1]))
    phone = possible_phone
    
    record = book.find(name)
    if not record:
        raise KeyError
    
    if not record.remove_phone(phone):
        return f"Phone number '{phone}' not found for this contact."

    return "Phone number removed."


@input_error
def remove_contact(args, book): # Функція для видалення контакту
    if not args:
        raise ValueError("Please provide the contact name to remove.")
    
    name = normalize_name(" ".join(args))
    
    if not book.delete(name):
        raise KeyError("Contact not found.")
    
    return f"Contact '{name}' removed."


@input_error
def add_birthday(args, book): # Функція для додавання дати народження до контакту
    if len(args) < 2:
        raise ValueError("Please provide name and birthday (DD.MM.YYYY).")
    name = normalize_name(" ".join(args[:-1]))
    birthday = args[-1]
    record = book.find(name)
    if not record:
        raise KeyError
    if record.birthday:
        return "Birthday already exists. Use 'editbday' to change it."
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book): # Функція для показу дати народження контакту
    if not args:
        raise ValueError("Please provide the contact name.")
    
    name = normalize_name(" ".join(args))
     # Знаходимо всі потенційні збіги
    matches = [record for key, record in book.data.items() if name.lower() in key.lower()]

    if not matches:
        raise KeyError("Contact not found.")

    # Якщо один збіг — повертаємо одразу
    if len(matches) == 1:
        record = matches[0]
        if record.birthday:
            return f"{record.name.value}'s birthday is {record.birthday.value}"
        else:
            return "Birthday is not set for this contact."

    # Якщо знайдено кілька контактів з заданим ім’ям
    matches_with_birthday = [r for r in matches if r.birthday]

    if not matches_with_birthday:
        return "None of the matching contacts have a birthday set."

    # Якщо знайдено кілька контактів з днем народження
    result = ["Found multiple contacts:"]
    result += [f"{record.name.value}: {record.birthday.value}" for record in matches]
    result.append("Please enter the full name to get an exact match.")
    return "\n".join(result)


@input_error
def edit_birthday(args, book): # Функція для редагування дати народження контакту
    if len(args) < 2:
        raise ValueError("Please provide name and new birthday (DD.MM.YYYY).")
    name = normalize_name(" ".join(args[:-1]))
    birthday = args[-1]
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_birthday(birthday)
    return "Birthday updated."


@input_error
def remove_birthday(args, book): # Функція для видалення дати народження контакту
    if not args:
        raise ValueError("Please provide name to remove birthday.")
    name = normalize_name(" ".join(args))
    record = book.find(name)
    if not record:
        raise KeyError
    record.remove_birthday()
    return "Birthday removed."


@input_error
def show_phone(args, book): # Функція для показу телефону контакту
    if not args:
        raise ValueError("Please provide the contact name.")

    name = normalize_name(" ".join(args))
    
     # Знаходимо всі потенційні збіги
    matches = [record for key, record in book.data.items() if name.lower() in key.lower()]

    if not matches:
        raise KeyError

    # Якщо один збіг — повертаємо одразу
    if len(matches) == 1:
        return str(matches[0])

    # Якщо кілька — повертаємо всі
    result = ["Found multiple contacts:"]
    result += [f"{str(r)}" for r in matches]
    return "\n".join(result)

@input_error
def search_contacts(args, book): # Функція для пошуку контактів за іменем або телефоном
    if not args:
        raise ValueError("Please enter a name or phone to search.")
    results = book.search(args[0])
    return "\n".join(results) if results else "No matching contacts found."


# Функція для отримання майбутніх днів народження
def upcoming_birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    return "\n".join(upcoming) if upcoming else "No upcoming birthdays in the next 7 days."


# Функція для показу всіх контактів у алфавітному порядку
def show_all(book):
    if not book.data:
        return "No contacts saved."
    
    # Сортування контактів за іменем (незалежно від регістру)
    sorted_records = sorted(book.data.items(), key=lambda item: item[0].lower())
    return "\n".join(str(record) for _, record in sorted_records)


# Функція для виведення доступних команд
def print_available_commands():
    command_groups = {
        "General": ["hello", "exit", "close"],
        "Contacts": ["addcontact", "editname", "removecontact", "search", "all"],
        "Phones": ["addphone", "changephone", "removephone", "showphone"],
        "Birthdays": ["addbday", "showbday", "editbday", "removebday", "birthdays"]
    }

    print("Unknown command. Try one of the following:\n")
    for group, commands in command_groups.items():
        print(f"   {group}: {', '.join(commands)}\n")
    


# Головна функція для запуску бота
# Після всіх функцій, які змінюють адресну книгу -->
# (результат містить “added”, “removed”, “updated”) виконується автозбереження.
# Файл .pkl буде оновлюватися відразу після кожної операції.
def main():
    filename = DEFAULT_FILENAME
    book = load_address_book(filename)
    print("Welcome to the assistant bot!")

    try:
        while True:
            user_input = input("Enter a command: ")
            if not user_input.strip():
                continue

            command, args = parse_input(user_input)

            if command in ["exit", "close"]:
                save_address_book(book, filename)
                print("Good bye!")
                break

            elif command == "hello":
                print("How can I help you?")

            elif command == "addcontact":
                result = add_contact(args, book)
                print(result)
                if "added" in result.lower():
                    save_address_book(book, filename)
                    
            elif command == "editname":
                result = edit_contact_name(args, book)
                print(result)
                if "changed" in result.lower():
                    save_address_book(book, filename)
                
            elif command == "removecontact":
                result = remove_contact(args, book)
                print(result)
                if "removed" in result.lower():
                    save_address_book(book, filename)

            elif command == "addphone":
                result = add_phone_to_contact(args, book)
                print(result)
                if "added" in result.lower():
                    save_address_book(book, filename)

            elif command == "changephone":
                result = change_contact(args, book)
                print(result)
                if "updated" in result.lower():
                    save_address_book(book, filename)

            elif command == "removephone":
                result = remove_phone(args, book)
                print(result)
                if "removed" in result.lower():
                    save_address_book(book, filename)
                    
            elif command == "showphone":
                print(show_phone(args, book))

            elif command == "addbday":
                result = add_birthday(args, book)
                print(result)
                if "added" in result.lower():
                    save_address_book(book, filename)
                    
            elif command == "showbday":
                result = show_birthday(args, book)
                print(result)

            elif command == "editbday":
                result = edit_birthday(args, book)
                print(result)
                if "updated" in result.lower():
                    save_address_book(book, filename)

            elif command == "removebday":
                result = remove_birthday(args, book)
                print(result)
                if "removed" in result.lower():
                    save_address_book(book, filename)

            elif command == "birthdays":
                print(upcoming_birthdays(book))

            elif command == "search":
                print(search_contacts(args, book))

            elif command == "all":
                print(show_all(book))

            else:
                print_available_commands()
                
    except KeyboardInterrupt: # Збереження без явного виходу з програми (exit, close)
        print("\nGood bye!")
        save_address_book(book, filename)
        print("Address book saved successfully.")

# Можна ще ввести окремий клас для обробки команд
# Це дозволить уникнути довгого if-elif блоку в main()

if __name__ == "__main__":
    main()