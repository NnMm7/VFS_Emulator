# Команды этапа 1
ls
cd /home
ls -a
ls "some path with spaces"
cd 'another path'

# Проверка ошибок
unknown_command
exit extra_arg
cd
cd /nonexistent

# Комментарий ниже игнорируется
# это комментарий, он не должен выполняться

# Проверка кавычек
ls "a b"

exit
