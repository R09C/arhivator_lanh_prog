
```bash
# Сжать файл в .zst
python main.py compress static/file.txt archive.zst

# Сжать файл в .bz2
python main.py compress static/file.txt archive.bz2

# С прогресс-баром
python main.py compress static/file.txt output.zst -p
```

### Распаковка файла

```bash
# Распаковать
python main.py decompress archive.zst

# Распаковать с указанием выходного файла
python main.py decompress archive.zst static/decompressed.txt

# С прогресс-баром
python main.py decompress archive.bz2 -p
```

### stdlib

```bash
# Сжать с stdlib
python main.py compress static/file.txt archive.zst --impl stdlib

# Распаковать с stdlib
python main.py decompress archive.zst static/output.txt --impl stdlib
```

## Запуск тестов

```bash
python tests/test_algorithms.py

# Кастомная реализация
python tests/test_advanced.py

# Stdlib реализация
python tests/test_advanced.py
```
