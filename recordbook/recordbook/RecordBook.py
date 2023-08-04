# 
from collections import UserDict
from collections.abc import Iterator
import re
import datetime
import pickle

# батьківський клас
class Field():
    def __init__(self, value) -> None:
        self.__value = None
        self.value = value
    
    
# клас Ім'я
class Name(Field):
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, new_value):
        self.__value = new_value

  

# клас Телефон
class Phone(Field): 
    @property
    def value(self):
        return self.__value 
    
    @value.setter
    def value(self, new_value):
        if new_value.lower() == "none": 
            self.__value = "None"
            return ""   # не видаляти
        
        result = re.sub("\D", "", new_value) # \D - Matches any character which is not a decimal digit. 
        if not result:
            raise PhoneException("Incorrect phone format")   # введені символи замість телефона
        
        if len(result) == 12 and result.startswith("38"): self.__value = f"+{result}"
        elif len(result) == 10 and result[:3] in ["093", "073", "063",\
                                                "050", "066", "099", "095", "097", "067",\
                                                "039", "068", "096", "098"]: self.__value = f"+38{result}"
        elif len(result) != 12: 
            raise PhoneException("Incorrect phone format")   # невірний формат телефона
    
    
# клас День народження        
class Birthday(Field):
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, new_birthday:str):
        pattern = r"^\d{2}(\.|\-|\/)\d{2}\1\d{4}$"  # дозволені дати формату DD.MM.YYYY 
        if re.match(pattern, new_birthday):         # альтернатива для крапки: "-" "/"
            self.__value = re.sub("[-/]", ".", new_birthday)  # комбінувати символи ЗАБОРОНЕНО DD.MM-YYYY 
        else: 
            self.__value = "None"
            raise BirthdayException("Unauthorized birthday format")
            
      
        
#========================================================
# Класс Record, который отвечает за логику 
#  - добавления/удаления/редактирования
# необязательных полей и хранения обязательного поля Name
#=========================================================
class Record():
    def __init__(self, name: Name, birthday: Birthday=None, phones: list[Phone]=None) -> None:
        self.name = name            
        self.birthday = birthday
        self.phones = []            
        self.phones.extend(phones)
    
    def __str__(self) -> str:
        return f"{self.name.value}|{self.birthday.value}|{', '.join(map(lambda phone: phone.value, self.phones))}" 
    
    # Done - розширюємо існуючий список телефонів особи - Done
    # НОВИМ телефоном або декількома телефонами для особи - Done
    def add_phone(self, new_phone: list[Phone]) -> str:
        self.phones.extend(new_phone)
        return f"The phones was/were added - [bold green]success[/bold green]"
    
    # Done - видаляємо телефони із списку телефонів особи - Done!
    def del_phone(self, del_phone: Phone) -> str:
        error = True
        for phone in self.phones:
                if phone.value == del_phone.value: 
                    self.phones.remove(phone) 
                    self.phones.append(Phone("None")) if self.phones == [] else self.phones 
                    error = False  #видалення пройшло з успіхом
                    break
        if error: return f"The error has occurred. You entered an incorrect phone number."
        else: return f"The phone {phone.value} was deleted - [bold green]success[/bold green]"
    
    # Done = редагування запису(телефону) у книзі особи - Done
    def edit_phone(self, old_phone: Phone, new_phone: Phone) -> str:
        index = next((i for i, obj in enumerate(self.phones) if obj.value == old_phone.value), -1)
        self.phones[index]= new_phone
        return f"The person {self.name.value} has a new phone {new_phone.value} - [bold green]success[/bold green]"
    
    # повертає кількість днів до наступного дня народження
    def days_to_birthday(self):
        if self.birthday.value:
            now_date = datetime.datetime.now()
            now_year = now_date.year
            
             # Определяем формат строки для Даты
            date_format = "%d.%m.%Y %H:%M:%S"
            # Строка с Датой народження
            date_string = f"{self.birthday.value} 00:00:00"  
            dt = datetime.datetime.strptime(date_string, date_format)
            
            birthday = datetime.datetime(day=dt.day, month=dt.month, year=now_year)
            
            if now_date > birthday:
                birthday = birthday.replace(year=now_date.year + 1)
                dif = birthday - now_date
                return f"до {birthday.strftime('%d.%m.%Y')} залишилося = {dif}"
            else:
                dif = birthday - now_date
                return f"до {birthday.strftime('%d.%m.%Y')} залишилося = {dif}"
        else: return f"We have no information about {self.name.value}'s birthday."
    
    # змінює день народження для особи
    def change_birthday(self, birthday: Birthday):
        self.birthday = birthday
        return f"Birthday for {self.name.value} is changed - [bold green]success[/bold green]"
    
    # перевіряє наявність 1(одного)телефону у списку
    def check_dublicate_phone(self, search_phone: str) ->bool:  
        result = list(map(lambda phone: any(phone.value == search_phone), self.data[self.name.value].phones))
        return True if result else False
    
class AddressBook(UserDict):
       
    def add_record(self, record):
        self.data[record.name.value] = record
    
    # завантаження записів книги із файлу
    def load_database(self, path):
        with open(path, "rb") as fr_bin:
            self.data = pickle.load(fr_bin)  # копирование Словника   load_data = pickle.load(fr_bin)
                                                                    # self.data = {**load_data}
        return f"The database has been loaded = {len(self.data)} records"
    
    #-----------------------------------------
    # збереження записів книги у файл  
    # формат збереження даних:
    #
    # Lisa|15.08.1984|+380739990022, +380677711122
    # Alex|None|+380954448899, +380506667788   
    #-------------------------------------------
    def save_database(self, path):
        with open(path, "wb") as f_out:
            pickle.dump(self.data, f_out)
        return f"The database is saved = {len(self.data)} records"    
            
    # генератор посторінкового друку
    def _record_generator(self, N=10):
        records = list(self.data.values())
        total_records = len(records)
        current_index = 0
        
        while current_index < total_records:
            batch = records[current_index: current_index + N]
            current_index += N
            yield batch

class PhoneException(Exception):
    def __init__(self, message):
        self.__message = None
        self.message = message
        #super().__init__(self.message)
    
    def __str__(self):
        return f"Attention: {self.message}"


class BirthdayException(Exception):
    def __init__(self, message):
        self.__message = None
        self.message = message
    
    def __str__(self):
        return f"Attention: {self.message}"
    
