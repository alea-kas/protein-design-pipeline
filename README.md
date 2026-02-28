# Protein Design Pipeline

Учебный проект для диплома: конвейер для анализа и дизайна белков с использованием инструментов структурного поиска и методов машинного обучения.

## Структура проекта

- `env/` – файлы окружения (`environment.yml`).
- `src/` – Python-скрипты (чтение FASTA, подготовка данных, ML-модели).
- `data/` – входные и выходные данные (FASTA, CSV и т.п.).
- `notebooks/` – эксперименты в Jupyter (пока пусто или по мере появления).

## Установка окружения Miniconda и Bioconda на кластер

### Установка Miniconda в домашний каталог

На логин-узле:

```bash
cd ~
bash Miniconda3-latest-Linux-x86_64.sh
```

В установщике:

- принять лицензию (`yes`);
- оставить путь по умолчанию `/home/$USER/miniconda3` (нажать Enter);
- согласиться на инициализацию `conda init`.

После установки перезапустить shell:

```bash
exec bash
conda --version
```

### Настройка Bioconda

Однократно настроить каналы (создаётся/обновляется `~/.condarc`):

```bash
conda config --add channels bioconda
conda config --add channels conda-forge
conda config --set channel_priority strict
```

### Окружение для проекта

Создать окружение и установить зависимости:

```bash
conda create -n chrommaenv python=3.10 -y
conda activate chrommaenv

conda install biopython pandas numpy scikit-learn -y
```

Проверка:

```bash
python -c "import Bio, pandas, numpy, sklearn; print('ok')"
```

Если выводит `ok`, окружение готово.

В минимальном варианте README для шага 1 можно оформить так.

## Шаг 1. Вырезание мотива из PDB и создание FASTA

Скрипт `make_motif_config_and_fasta.py` берёт структуру OsLsi1 (7NL4), вырезает сегмент с мотивом и создаёт FASTA‑файл для дальнейших шагов.

### Вход

- `data/7nl4.pdb` — PDB‑структура OsLsi1 (цепь A).

### Выход

- `config/motifs.yaml` — описание мотива:
  - PDB‑ID, цепь,
  - диапазон остатков (65–222),
  - ключевые позиции (65 T, 88 G, 207 S, 216 G, 222 R).
- `data/raw/oslsi1_segment_65_222.fasta` — аминокислотная последовательность сегмента 65–222 цепи A.

### Запуск

Из корня репозитория:

```bash
python make_motif_config_and_fasta.py
```

После успешного запуска эти два файла используются как вход для следующего шага — генерации последовательностей в Chroma.

## План развития

- добавить векторизацию последовательностей (признаковые векторы/one-hot);
- реализовать простые ML-модели (случайный лес);
- автоэнкодер для снижения размерности;
- интерпретируемые модели (сети Колмогорова–Арнольда) на латентных признаках.
