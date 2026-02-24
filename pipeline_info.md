Ниже — один и тот же конвейер, но с отдельными командами для Windows и Linux.

## 1. Логика конвейера (общая)

Шаги данных:

1. `motif.fasta` → генерация дизайнов в Chroma → `data/chroma_scaffolds_*.fasta`.  
2. Все FASTA → сводная таблица → `data/sequences_summary_v1.csv`.  
3. Таблица → признаки → `data/features_v1.csv`.  
4. Признаки → скоринг/фильтрация → `results/top_candidates_v1.csv`.

Скрипты (одинаковые имена и на Windows, и на Linux):

- `src/generate_chroma_scaffolds.py`  
- `src/summarize_sequences.py`  
- `src/featurize_sequences.py`  
- `src/score_candidates.py`  

Окружения:

- `chromaenv` — Python 3.10 + Chroma.  
- `bioenv` — анализ (pandas, sklearn, твои скрипты).

***

## 2. Windows: батник `run_pipeline_win.bat`

Создать в корне репозитория файл `run_pipeline_win.bat`:

```bat
@echo off
REM Переходим в корень репозитория
cd /d C:\Users\genna\repository

REM 1. Генерация последовательностей в Chroma
call conda activate chromaenv
python src\generate_chroma_scaffolds.py

REM 2. Анализ в bioenv
call conda activate bioenv
python src\summarize_sequences.py
python src\featurize_sequences.py
python src\score_candidates.py

echo.
echo === PIPELINE FINISHED ===
pause
```

Запуск на Windows:

```bat
run_pipeline_win.bat
```

***

## 3. Linux: скрипт `run_pipeline_linux.sh`

В репозитории создать файл `run_pipeline_linux.sh`:

```bash
#!/bin/bash

# bash run_pipeline_linux.sh запускать из корня репозитория

set -e  # падать при первой ошибке

# Если conda не подхватывается по умолчанию, нужно один раз:
# source ~/miniconda3/etc/profile.d/conda.sh

cd "$(dirname "$0")"   # в каталог скрипта = корень репозитория

echo "=== STEP 1: Chroma generation (окружение chromaenv) ==="
conda activate chromaenv
python src/generate_chroma_scaffolds.py

echo "=== STEP 2: Analysis (окружение bioenv) ==="
conda activate bioenv
python src/summarize_sequences.py
python src/featurize_sequences.py
python src/score_candidates.py

echo "=== PIPELINE FINISHED ==="
```

Сделать исполняемым и запустить:

```bash
chmod +x run_pipeline_linux.sh
bash run_pipeline_linux.sh
```

Если на кластере используют SLURM, можно вместо прямого запуска обернуть это в `sbatch`‑скрипт (добавить `#SBATCH`‑опции, а внутри вызвать `bash run_pipeline_linux.sh`).

***

## 4. Минимально нужная структура репозитория

```text
repository/
  run_pipeline_win.bat
  run_pipeline_linux.sh
  chroma/                # исходники Chroma (с setup.py)
  data/
    motif.fasta
    ...
  results/
  src/
    generate_chroma_scaffolds.py
    summarize_sequences.py
    featurize_sequences.py
    score_candidates.py
```