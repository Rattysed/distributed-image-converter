import argparse
import concurrent.futures
import itertools
import json
import os
import requests
import time


def get_correct_image_path(size):
    for filename in os.listdir("./assets"):
        if size in filename:
            return f"./assets/{filename}"
    
    print(f"Невозможно найти изображение, содержащее {size} в названии")
    exit(0)

def post_image(size):
    url_upload = 'https://distributed-text-converter.vdi.mipt.ru/api/upload/'
    files = {'files': open(get_correct_image_path(size), 'rb')}
    response_upload = requests.post(url_upload, files=files, allow_redirects=True)
    request_id = json.loads(response_upload.text)['id']
    print(response_upload.content)
    return request_id

def get_request_ids(size, count):
    print("[1] Отправление изображений")

    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        request_ids = list(executor.map(post_image, itertools.repeat(size, count)))

    print("[1] Изображения отправлены")
    
    return request_ids

def get_exec_times(request_ids):
    print("[2] Получение времени обработки изображений")

    exec_times = []

    for request_id in request_ids:
        # Waiting till the end of image proccesing
        url_status = f'https://distributed-text-converter.vdi.mipt.ru/api/status/{request_id}/'
        sleep_duration = 0.0
        sleep_addition = 0.5
        while json.loads(requests.get(url_status).text)['status'] != 'ready':
            print(requests.get(url_status).content)
            sleep_duration += sleep_addition
            time.sleep(min(5, sleep_duration))

        # Get the processing time
        url_exec_time = f'https://distributed-text-converter.vdi.mipt.ru/request/exec_time/{request_id}/'
        response_exec_time = requests.get(url_exec_time)
        exec_time = json.loads(response_exec_time.text)['seconds']
        exec_times.append(exec_time)

    print("[2] Информация по всем изображениям получена")

    return exec_times

def save_data(count_workers, count, size, exec_times):
    filename = f'./data/workers-{count_workers}_size-{size}_count-{count}.json'
    dirname = os.path.dirname(filename)

    if not os.path.exists(dirname):
        os.mkdir(dirname)

    data = {
        'workers-count': count_workers,
        'count': count,
        'size': size,
        'times': exec_times
    }

    with open(filename, 'w') as file:
        json.dump(data, file)

    print(f'[3] Время обработки изображений записано в {filename}\n')
    

def main():
    parser = argparse.ArgumentParser(description='Получить время выполнения --count POST-запросов с изображениями размера --size в секундах')

    parser.add_argument('--workers-count', required=True, type=int, help='Количество воркеров')
    parser.add_argument('--count', required=True, type=int, help='Количество запросов')
    parser.add_argument('--size', required=True, choices=['small', 'big'], help='Размер изображения')

    args = parser.parse_args()

    print(f"[0] {args.count} {args.size}".upper())

    request_ids = get_request_ids(size=args.size, count=args.count)
    exec_times = get_exec_times(request_ids=request_ids)

    save_data(count_workers=args.workers_count, count=args.count, size=args.size, exec_times=exec_times)
    

if __name__ == '__main__':
    main()