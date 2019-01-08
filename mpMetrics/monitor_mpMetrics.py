#!/usr/bin/env python3

import argparse
import csv
import datetime
import logging
import os
import sys
import time

import requests
import urllib3


formatter = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(level=logging.WARNING, format=formatter)
logger = logging.getLogger(__name__)


def request_with_retry(url, timeout, retry):
    """HTTPリクエストを行い、失敗した場合はリトライを行う。

    :param url:
    :param timeout:
    :param retry:
    :return: jsonデータ
    """

    session = requests.Session()

    # backoff_factorが1だとリトライの間のスリープ時間は[0s, 2s, 4s, 8s, ...]となる
    retries = urllib3.util.retry.Retry(total=retry, backoff_factor=1)

    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))

    headers = {'Accept': 'application/json'}

    logger.info('GET {}'.format(url))
    response = session.get(url, headers=headers, timeout=timeout)

    return response.json()


def write_header(filepath):
    """ヘッダー書き込む。
    filepathが指定され、ファイルが存在しなかった場合はファイルを作成してヘッダーを書く。
    filepathが指定され、ファイルが空の場合もヘッダーを書く。
    filepathが指定されなかった場合は標準出力にヘッダーを書く。

    :param filepath:
    :return:
    """

    fieldnames = [
        'Time',
        'Heap', 'UsedMemory',
        'PoolSize', 'ActiveThreads',
        'LiveCount', 'ActiveCount']

    # filepathが指定された場合
    if filepath:
        # ファイルが存在しない場合はファイルを作成してヘッダーを書く
        if not os.path.isfile(filepath):
            with open(filepath, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
        # ファイルが存在する場合
        else:
            with open(filepath, 'r+') as csv_file:
                # ファイルが空の場合はヘッダーを書く
                if not csv_file.read():
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
    # filepathが指定されなかった場合は標準出力にヘッダーを書く
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()


def append_data(filepath, metrics):
    """性能情報の値を追記する。
    filepathが渡された場合はcsvに書き込み、渡されなかった場合は標準出力に書き込む。

    :param filepath:
    :param metrics:
    :return:
    """

    fieldnames = [
        'Time',
        'Heap', 'UsedMemory',
        'PoolSize', 'ActiveThreads',
        'LiveCount', 'ActiveCount']

    item = {
        'Time': datetime.datetime.now(),
        'Heap': metrics['base']['memory.committedHeap'],
        'UsedMemory': metrics['base']['memory.usedHeap'],
        'PoolSize': metrics['vendor']['threadpool.Default_Executor.size'],
        'ActiveThreads': metrics['vendor']['threadpool.Default_Executor.activeThreads'],
        'LiveCount': metrics['vendor']['session.default_host_metrics.liveSessions'],
        'ActiveCount': metrics['vendor']['session.default_host_metrics.activeSessions']
    }

    if filepath:
        # データをファイルに追記する
        with open(filepath, 'a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow(item)
    else:
        # 標準出力に出力する
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writerow(item)


def main():

    # コマンド引数の処理
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',
                        action='store',
                        type=str,
                        default='localhost',
                        help='接続先のホスト名を指定します default:localhost')
    parser.add_argument('--port',
                        action='store',
                        type=int,
                        default=9080,
                        help='接続先のポートを指定します default:9080')
    parser.add_argument('--interval',
                        action='store',
                        type=int,
                        default=60,
                        help='データの取得間隔（秒）を指定します default:60')
    parser.add_argument('--delay',
                        action='store',
                        type=int,
                        default=30,
                        help='モニターを開始するまでの待機時間（秒）を指定します default:30')
    parser.add_argument('--timeout',
                        action='store',
                        type=int,
                        default=2,
                        help='モニターリクエストのタイムアウト時間（秒）を指定します default:2')
    parser.add_argument('--retry',
                        action='store',
                        type=int,
                        default=10,
                        help='モニターのリトライ回数を指定します default:10')
    parser.add_argument('-f', '--filename',
                        action='store',
                        type=str,
                        help='出力先のファイル名を指定します default:未指定（標準出力）')
    args = parser.parse_args()
    host = args.host
    port = args.port
    timeout = args.timeout
    retry = args.retry
    filepath = args.filename

    # 待機時間
    time.sleep(args.delay)

    # ヘッダーを書く
    write_header(filepath)

    # MicroProfile MetricsのURL
    url = 'http://{}:{}/metrics'.format(host, port)

    # モニター
    while True:
        metrics = request_with_retry(url, timeout, retry)
        append_data(filepath, metrics)
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
