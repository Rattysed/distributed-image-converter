import os
import json
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def read_data(data_dir):
    # Хранилища
    data_by_worker_and_size = defaultdict(list)
    summary_by_size = defaultdict(lambda: defaultdict(list))

    # Регулярка для парсинга имени файла
    pattern = re.compile(r"workers-(\d+)_size-(\w+)_count-(\d+)\.json")

    # Чтение файлов
    for file_name in os.listdir(data_dir):
        match = pattern.match(file_name)
        if not match:
            continue

        workers = int(match.group(1))
        size = match.group(2)
        count = int(match.group(3))

        with open(os.path.join(data_dir, file_name), "r") as f:
            data = json.load(f)
            times = data["times"]

            data_by_worker_and_size[(workers, size)].append((count, times))
            mean_time = np.mean(times)
            summary_by_size[size][workers].append((count, mean_time))
    
    return (data_by_worker_and_size, summary_by_size)

def draw_graph_for_one_experiment(batch_data, size, workers, output_dir):
    counts, mins, maxs, means, medians = [], [], [], [], []

    for count, times in batch_data:
        times_np = np.array(times)
        counts.append(count)
        mins.append(np.min(times_np))
        maxs.append(np.max(times_np))
        means.append(np.mean(times_np))
        medians.append(np.median(times_np))

    plt.figure(figsize=(10, 6))
    plt.plot(counts, maxs, label="Максимум", color="red")
    plt.plot(counts, mins, label="Минимум", color="blue")
    plt.plot(counts, means, label="Среднее", color="green")
    plt.plot(counts, medians, label="Медиана", color="orange")
    plt.fill_between(counts, mins, maxs, color="gray", alpha=0.2, label="Диапазон (мин-макс)")

    plt.xlabel("Количество запросов")
    plt.ylabel("Время обработки (сек)")
    plt.title(f"Размер: {size}, Воркеры: {workers}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    filename = f"size-{size}_workers-{workers}.png"
    plt.savefig(os.path.join(output_dir, filename))
    plt.close()

def draw_graph_for_multiply_experiments(summary_by_size, output_dir):
    for size, workers_data in summary_by_size.items():
        plt.figure(figsize=(10, 6))
        for workers, datapoints in sorted(workers_data.items()):
            datapoints.sort(key=lambda x: x[0])
            counts = [x[0] for x in datapoints]
            means = [x[1] for x in datapoints]
            plt.plot(counts, means, label=f"{workers} workers")

        plt.xlabel("Количество запросов)")
        plt.ylabel("Среднее время обработки (сек)")
        plt.title(f"Сравнение по воркерам. Размер изображения: {size}")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        filename = f"size-{size}_summary.png"
        plt.savefig(os.path.join(output_dir, filename))
        plt.close()

def main():
    # Путь к папке с файлами
    DATA_DIR = "./data"
    OUTPUT_DIR = "graphs"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    data_by_worker_and_size, summary_by_size = read_data(DATA_DIR)

    for (workers, size), batch_data in data_by_worker_and_size.items():
        batch_data.sort(key=lambda x: x[0])
        draw_graph_for_one_experiment(batch_data, size, workers, OUTPUT_DIR)
        

    # Сводные графики: сравнение воркеров (только среднее время)
    draw_graph_for_multiply_experiments(summary_by_size, OUTPUT_DIR)

if __name__ == '__main__':
    main()