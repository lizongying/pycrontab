# -*- coding: UTF-8 -*-
SCRIPT_IGNORE = 'vi|tail|more|head|cat|more|less|grep|\/bin\/sh'
LOG_DIR = '/Users/lizongying/IdeaProjects/pycrontab/log'
LOG_PATH = '/Users/lizongying/IdeaProjects/pycrontab/log/crontab.log'
LOG_LEVEL = 'DEBUG'
STDOUT_PATH = '/Users/lizongying/IdeaProjects/pycrontab/log/%s_out.log'
STDERR_PATH = '/Users/lizongying/IdeaProjects/pycrontab/log/%s_err.log'
# 检测配置间隔，注意性能和及时性的平衡
CHECK_INTERVAL = 10
# 多进程运行间隔，避免同时启动多个进程
SCRIPT_INTERVAL = 10
# 最小运行间隔，避免短时间内多次启动，千万不要小于一分钟，或者你知道在做什么
SCRIPT_MIN = 60
