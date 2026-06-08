# Конвейер для создания белков *de novo*

Современные генеративные нейросети способны создавать новые белки, но на практике многие из этих структур оказываются нестабильными. Без строгого контроля качества генерация создаёт много неудачных вариантов.

Данный репозиторий решает эту проблему. Здесь представлен автоматизированный конвейер для *de novo* дизайна белков (на примере кремний-транспортирующего белка). Конвейер генерирует структуры и проводит их строгий отбор с помощью алгоритмов машинного обучения. Проект разработан в рамках магистерского диплома.

Скрипты адаптированы для публичного использования: личные пути заменены на относительные.

### Режимы работы

Конвейер можно запустить в двух режимах (пусковые скрипты лежат в корневой папке):

**1. Воспроизведение результатов диплома (`run_diploma.sh`)**
Полный цикл для сбора данных и обучения алгоритмов.
* **Как работает:** Сначала идёт генерация структур (RFdiffusion, Chai-1). Затем для **всех** десятков тысяч белков выполняется процесс структурного выравнивания (Foldseek).
* **Итог:** На собранных данных обучаются модели (Random Forest и KAN) и строятся графики для дипломной работы.
* **Команда:** `bash run_diploma.sh`

**2. Быстрый дизайн новых белков (`run_fast_design.sh`)**
Режим для быстрого создания новых белков на практике.
* **Как работает:** После генерации структур сразу применяется обученная модель Random Forest. Она работает как быстрый фильтр и отсекает до 85% неудачных белковых структур.
* **Итог:** Ресурсоёмкий Foldseek запускается **только для лучших кандидатов**, что экономит время и вычислительные мощности кластера.
* **Команда:** `bash run_fast_design.sh`

### Настройка
Перед запуском укажите путь к программе `foldseek` на вашем кластере. Для этого измените переменную `FOLDSEEK_BIN` внутри файлов `slurm/06_createdb.slurm` и `slurm/08_foldseek_search.slurm`.

### Благодарности
Исследование выполнено с использованием суперкомпьютерного комплекса ЦКП «Биоинформатика» ИЦиГ СО РАН.

--------------------------

# Pipeline for *de novo* protein design

Modern generative neural networks can create new proteins, but in practice, many of these structures turn out to be unstable. Without strict quality control, generation creates many unsuccessful variants.

This repository solves this problem. It presents an automated pipeline for *de novo* protein design (using a silicon transporter protein as an example). The pipeline generates structures and performs their strict selection using machine learning algorithms. The project was developed as part of a master's thesis.

The scripts are adapted for public use: personal paths are replaced with relative ones.

### Execution Modes

The pipeline can be run in two modes (the execution scripts are located in the root folder):

**1. Reproducing the diploma results (`run_diploma.sh`)**
The full cycle for data collection and algorithm training.
* **How it works:** First, structures are generated (RFdiffusion, Chai-1). Then, the structural alignment process (Foldseek) is performed for **all** tens of thousands of proteins.
* **Result:** Models (Random Forest and KAN) are trained on the collected data, and plots for the thesis are created.
* **Command:** `bash run_diploma.sh`

**2. Fast design of new proteins (`run_fast_design.sh`)**
A mode for the fast creation of new proteins in practice.
* **How it works:** After structure generation, the trained Random Forest model is applied immediately. It acts as a fast filter and discards up to 85% of unsuccessful protein structures.
* **Result:** The resource-intensive Foldseek is run **only for the best candidates**, which saves time and cluster computing power.
* **Command:** `bash run_fast_design.sh`

### Setup
Before running the pipeline, specify the path to the `foldseek` program on your cluster. To do this, change the `FOLDSEEK_BIN` variable inside the `slurm/06_createdb.slurm` and `slurm/08_foldseek_search.slurm` files.

### Acknowledgments
This research was supported in part through computational resources of HPC facilities at collaborative center "Bioinformatics" ICG SB RAS.
