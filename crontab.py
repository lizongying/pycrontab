# -*- coding: UTF-8 -*-
import datetime
import json
import logging
import os
import random
import re
import subprocess
import time

import config
from setting import *

time_log = {}

logging.basicConfig(
    filename=LOG_PATH,
    level=LOG_LEVEL, format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()


class Crontab(object):
    config = {}

    def __init__(self, *args, **kwargs):
        self.config.update(kwargs)
        name = self.config['name'].strip()
        if not name:
            logger.info('no name')
            return
        logger.debug('%s config: %s' % (name, json.dumps(self.config)))
        if not self.check_config():
            logger.info('%s config error' % name)
            return
        if not self.check_process():
            logger.info('%s not need to start' % name)
            return
        self.check_log()
        self.start_process()

    @staticmethod
    def check_log():
        if not os.path.isdir(LOG_DIR):
            os.makedirs(LOG_DIR)

    def check_config(self):
        name = self.config['name'].strip()
        script = self.config['script'].strip()
        directory = self.config['directory'].strip()
        if not script:
            logger.info('%s no script' % name)
            return False
        if re.search(r'.*(%s).*' % SCRIPT_IGNORE, script):
            logger.info('%s script error' % name)
            return False
        if not os.path.isdir(directory):
            logger.info('%s directory error' % name)
            return False
        return True

    def check_process(self):
        name = self.config['name'].strip()
        process_num = int(self.config['process_num'])
        command = "ps ax|grep '%s'|grep -ivE '%s'|awk '{print $1}'" % (name, SCRIPT_IGNORE)
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
        logger.debug('%s process num need %s' % (name, process_num_need))
        if process_num_need < 0:
            process_str = ' '.join(map(lambda x: str(x), random.sample(process_arr, abs(process_num_need))))
            command = 'kill -9 %s' % process_str
            subprocess.Popen(command, shell=True)
            logger.info('%s kill process: %s' % (name, process_str))
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
            if name not in time_log:
                time_log[name] = {
                    'start_time': time.time(),
                }
            else:
                last_time = time_log[name]['last_time']
                now = time.time()
                if now - last_time < SCRIPT_MIN:
                    return
            time_log[name].update({
                'last_time': time.time(),
            })
            for process in range(process_num_need):
                subprocess.Popen(command, shell=True, cwd=directory,
                                 stdout=open(STDOUT_PATH % name, 'a'), stderr=open(STDERR_PATH % name, 'a'))
                logger.info('%s start process' % name)
                time.sleep(SCRIPT_INTERVAL)

    @staticmethod
    def test_time(target, test):
        time_test = re.match(r'^\*$', test)
        if time_test:
            return True
        time_test = re.match(r'^\d+$', test)
        if time_test:
            if int(test) == target:
                return True
        time_test = re.match(r'^\*/(\d+)$', test)
        if time_test:
            ss = time_test.groups()
            if 0 != int(ss[0]) and 0 == target % int(ss[0]):
                return True
        time_test = re.match(r'^(\d+)-(\d+)$', test)
        if time_test:
            ss = time_test.groups()
            if int(ss[1]) > int(ss[0]) and int(ss[0]) <= target <= int(
                    ss[1]):
                return True
        time_test = re.match(r'^(\d+)-(\d+)/(\d+)$', test)
        if time_test:
            ss = time_test.groups()
            if 0 != int(ss[2]) and 0 == target % int(ss[2]) and int(ss[1]) > int(ss[0]) and int(ss[0]) <= target <= int(
                    ss[1]):
                return True
        time_test = re.match(r'^([\d+,]+\d+)$', test)
        if time_test:
            ss = time_test.groups()
            ss_arr = map(lambda x: int(x), ss[0].split(','))
            if target in ss_arr:
                return True
        return False

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
        if not minute_test:
            return False
        hour_test = self.test_time(hour, time_arr[1])
        if not hour_test:
            return False
        day_test = self.test_time(day, time_arr[2])
        if not day_test:
            return False
        month_test = self.test_time(month, time_arr[3])
        if not month_test:
            return False
        week_test = self.test_time(week, time_arr[4])
        if not week_test:
            return False
        return True


def get_config():
    reload(config)
    for item in iter(config.items):
        yield item
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    while 1:
        for i in get_config():
            Crontab(**i)
