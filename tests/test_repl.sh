# REPL этап 1
# Демонстрирует: ls, cd, кавычки, ошибки

# Работа команды ls с разными аргументами
ls
ls -a
ls "some path"
ls 'single quoted'

# Работа команды cd с разными аргументами
cd /tmp
cd 'dir with spaces'

# Обработка ошибок
unknown_command
exit extra_arg
ls "unclosed quote

exit
