# Тестовый скрипт этапа 3: проверка кавычек
# Двойные кавычки
ls "some path"
ls "a b" c

# Одинарные кавычки
ls 'single quoted'
cd 'another dir'

# Смешанные случаи
cd "dir with spaces"
unknown "a b"

# Незакрытая кавычка — ошибка парсера
ls "unclosed

exit
