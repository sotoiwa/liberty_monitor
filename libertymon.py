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


# 警告を非表示にする
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

formatter = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(level=logging.WARNING, format=formatter)
logger = logging.getLogger(__name__)


def request_with_retry(url, user, password, timeout, retry):
    """HTTPリクエストを行い、失敗した場合はリトライを行う。

    :param url:
    :param user:
    :param password:
    :param timeout:
    :param retry:
    :return: jsonデータ
    """

    session = requests.Session()

    # backoff_factorが1だとリトライの間のスリープ時間は[0s, 2s, 4s, 8s, ...]となる
    retries = urllib3.util.retry.Retry(total=retry, backoff_factor=1)

    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))

    logger.info('GET {}'.format(url))
    # verify=Falseで証明書のチェックを行わない
    # ただしこれだけだと警告がでるので最初にurllib3.disable_warningsをしている
    response = session.get(url, auth=(user, password), verify=False, timeout=timeout)

    return response.json()


def get_value(name, items):
    """辞書のリストからnameがマッチする辞書を探し、value.valueを返す。

    :param name:
    :param items:
    :return: データの値
    """

    for item in items:
        if item['name'] == name:
            return item['value']['value']

    return None


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


def append_data(filepath, jvmstats, threadpoolstats, sessionstats):
    """性能情報の値を追記する。
    filepathが渡された場合はcsvに書き込み、渡されなかった場合は標準出力に書き込む。

    :param filepath:
    :param jvmstats:
    :param threadpoolstats:
    :param sessionstats:
    :return:
    """

    fieldnames = [
        'Time',
        'Heap', 'UsedMemory',
        'PoolSize', 'ActiveThreads',
        'LiveCount', 'ActiveCount']

    item = {
        'Time': datetime.datetime.now(),
        'Heap': get_value('Heap', jvmstats),
        'UsedMemory': get_value('UsedMemory', jvmstats),
        'PoolSize': get_value('PoolSize', threadpoolstats),
        'ActiveThreads': get_value('ActiveThreads', threadpoolstats),
        'LiveCount': get_value('LiveCount', sessionstats),
        'ActiveCount': get_value('ActiveCount', sessionstats)
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
                        default=9443,
                        help='接続先のポートを指定します default:9443')
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

    # 接続ユーザーとパスワードは環境変数から取得
    # デフォルト値を設定
    user = os.getenv('JMX_USER', 'jmxadmin')
    password = os.getenv('JMX_PASSWORD', 'password')

    # 待機時間
    time.sleep(args.delay)

    # ヘッダーを書く
    write_header(filepath)

    # MBeanのURL
    jvmstats_url = 'https://{}:{}/IBMJMXConnectorREST/mbeans/' \
                   'WebSphere%3Atype%3DJvmStats/' \
                   'attributes'.format(host, port)
    threadpoolstats_url = 'https://{}:{}/IBMJMXConnectorREST/mbeans/' \
                          'WebSphere%3Aname%3DDefault+Executor%2Ctype%3DThreadPoolStats/' \
                          'attributes'.format(host, port)
    sessionstats_url = 'https://{}:{}/IBMJMXConnectorREST/mbeans/' \
                       'WebSphere%3Aname%3Ddefault_host%2FIBMJMXConnectorREST%2Ctype%3DSessionStats/' \
                       'attributes'.format(host, port)

    # モニター
    while True:
        jvmstats = request_with_retry(jvmstats_url, user, password, timeout, retry)
        threadpoolstats = request_with_retry(threadpoolstats_url, user, password, timeout, retry)
        sessionstats = request_with_retry(sessionstats_url, user, password, timeout, retry)
        append_data(filepath, jvmstats, threadpoolstats, sessionstats)
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
