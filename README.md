# Webcam → ASCII Art

Преобразует видеопоток с веб-камеры в ASCII-графику в реальном времени.

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python src/main.py
```

Управление: `ESC` / `Q` — выход.

## Конфигурация

Все настройки в `src/config.py`:
- `COLS` — ширина ASCII-полотна (по умолч. 120)
- `FPS_LIMIT` — ограничение кадров в секунду
- `CHAR_SET` — набор символов от тёмного к светлому
- `FONT_NAME`, `FONT_SIZE` — шрифт окна
- `CAMERA_INDEX` — индекс камеры (0 = основная)

## Тесты

```bash
python -m pytest tests/
```

## Структура проекта

```
src/
├── main.py                 # точка входа
├── config.py               # настройки
├── camera/webcam.py        # захват камеры
├── converter/ascii_converter.py  # конвертация в ASCII
└── renderer/pygame_display.py    # отрисовка окна
```
