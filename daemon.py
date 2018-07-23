# -*- coding: UTF-8 -*-
import datetime
import os
import random
import re
import subprocess
import time

import config
from setting import *


class Daemon(object):
    config = {}

    def __init__(self, *args, **kwargs):
        self.config.update(kwargs)
        if not self.check_config():
            print('config error')
            return
        if not self.check_process():
            print('not need to start')
            return
        self.check_log()
        self.start_process()

    @staticmethod
    def check_log():
        if not os.path.isdir(LOG_DIR):
            os.makedirs(LOG_DIR)

    def check_config(self):
        script = self.config['script'].strip()
        directory = self.config['directory'].strip()
        if not script:
            print('no script')
            return False
        if re.search(r'.*(%s).*' % SCRIPT_IGNORE, script):
            print('script error')
            return False
        if not os.path.isdir(directory):
            print('directory error')
            return False
        return True

    def check_process(self):
        script = self.config['script'].strip()
        process_num = int(self.config['process_num'])
        command = "ps ax|grep '%s'|grep -ivE '%s'|awk '{print $1}'" % (script, SCRIPT_IGNORE)
        res = ''
        process_arr = []
        try:
            res = subprocess.check_output(command, shell=True)
        except:
            pass
        if res:
            process_arr = map(lambda x: int(x), res.strip().split('\n'))
        process_num_now = len(process_arr)
        process_num_need = process_num - process_num_now
        if process_num_need < 0:
            process_str = ' '.join(map(lambda x: str(x), random.sample(process_arr, abs(process_num_need))))
            command = 'kill -9 %s' % process_str
            subprocess.Popen(command, shell=True)
        self.config.update({
            'process_num_need': process_num_need,
            'pid': process_arr,
        })
        return process_num_need > 0

    def start_process(self):
        process_num_need = self.config['process_num_need']
        directory = self.config['directory'].strip()
        script = self.config['script'].strip()
        name = self.config['name'].strip()
        runtime = self.config['runtime'].strip()
        command = script
        if self.test_cron(runtime):
            for process in range(process_num_need):
                subprocess.Popen(command, shell=True, cwd=directory,
                                 stdout=open(STDOUT_PATH % name, 'a'), stderr=open(STDERR_PATH % name, 'a'))
                time.sleep(SCRIPT_INTERVAL)

    @staticmethod
    def test_time(taget, test):
        time_res = False
        time_test = re.match(r'^\*$', test)
        if time_test:
            time_res = True
        time_test = re.match(r'^\d+$', test)
        if time_test:
            if int(test) == taget:
                time_res = True
        time_test = re.match(r'^\*/(\d+)$', test)
        if time_test:
            ss = time_test.groups()
            if 0 != int(ss[0]) and 0 == taget % int(ss[0]):
                time_res = True
        time_test = re.match(r'^(\d+)-(\d+)$', test)
        if time_test:
            ss = time_test.groups()
            if int(ss[1]) > int(ss[0]) and int(ss[0]) <= taget <= int(
                    ss[1]):
                time_res = True
        time_test = re.match(r'^(\d+)-(\d+)/(\d+)$', test)
        if time_test:
            ss = time_test.groups()
            if 0 != int(ss[2]) and 0 == taget % int(ss[2]) and int(ss[1]) > int(ss[0]) and int(ss[0]) <= taget <= int(
                    ss[1]):
                time_res = True
        time_test = re.match(r'^([\d+,]+\d+)$', test)
        if time_test:
            ss = time_test.groups()
            ss_arr = map(lambda x: int(x), ss[0].split(','))
            if taget in ss_arr:
                time_res = True
        return time_res

    def test_cron(self, cron):
        now = datetime.datetime.now()
        week = now.weekday() + 1
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        cron = re.sub(r'\s+', ' ', cron)
        time_arr = cron.split(' ')
        minute_test = self.test_time(minute, time_arr[0])
        hour_test = self.test_time(hour, time_arr[1])
        day_test = self.test_time(day, time_arr[2])
        month_test = self.test_time(month, time_arr[3])
        week_test = self.test_time(week, time_arr[4])
        if minute_test and hour_test and day_test and month_test and week_test:
            return True
        else:
            return False


def get_config():
    reload(config)
    for item in iter(config.items):
        yield item
        time.sleep(2)


if __name__ == '__main__':
    while 1:
        for i in get_config():
            Daemon(**i)
