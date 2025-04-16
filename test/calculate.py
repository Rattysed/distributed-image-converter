import os
import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# Путь к папке с json-файлами
DATA_DIR = "./data"  

# Папка для сохранения графиков
OUTPUT_DIR = "graphs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

data_by_size = defaultdict(list)

# Чтение всех json-файлов
for file_name in os.listdir(DATA_DIR):
    if file_name.endswith(".json"):
        path = os.path.join(DATA_DIR, file_name)
        with open(path, 'r') as f:
            data = json.load(f)
            size = data["size"]
            count = data["count"]
            times = data["times"]
            data_by_size[size].append((count, times))

for size, batch_data in data_by_size.items():
    batch_data.sort(key=lambda x: x[0])
    
    counts = []
    min_times = []
    max_times = []
    mean_times = []
    median_times = []

    for count, times in batch_data:
        times_np = np.array(times)
        counts.append(count)
        min_times.append(np.min(times_np))
        max_times.append(np.max(times_np))
        mean_times.append(np.mean(times_np))
        median_times.append(np.median(times_np))

    plt.figure(figsize=(10, 6))
    plt.plot(counts, max_times, label="Максимум", color="red")
    plt.plot(counts, min_times, label="Минимум", color="blue")
    plt.plot(counts, mean_times, label="Среднее", color="green")
    plt.plot(counts, median_times, label="Медиана", color="orange")

    plt.fill_between(counts, min_times, max_times, color="gray", alpha=0.2, label="Диапазон (мин-макс)")

    plt.xlabel("Количесвто запросов (count)")
    plt.ylabel("Время обработки (сек)")
    plt.title(f"Размер изображения: {size}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Сохранение графика
    output_path = os.path.join(OUTPUT_DIR, f"{size}.png")
    plt.savefig(output_path)
    plt.close()
