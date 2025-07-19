import contextlib
import inspect
import logging
import os
import sys
from io import StringIO

from flask import Flask
import importlib as implib
from loguru import logger
from dotenv import load_dotenv

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

class StreamToLogger:

    def __init__(self, level="INFO"):
        self._level = level

    def write(self, buffer):
        for line in buffer.rstrip().splitlines():
            logger.opt(depth=1).log(self._level, line.rstrip())

    def flush(self):
        pass

def init_logger():
    logger.remove(0)
    logger.add(sys.__stdout__, level=os.getenv("OBGW_LOGLEVEL", "INFO"),
               format='[<e>{time:YYYY-MM-DD}</> <c>{time:HH:mm:ss}</> <m>{time:zz}</>] [<lvl>{level}</> | <y>{name}</>] {message}')
    logger.add("logs/obgw-log_{time:YYYY-MM-DD_HH:mm:ss}.log", level=os.getenv("OBGW_LOGLEVEL", "INFO"),
               format='[<e>{time:YYYY-MM-DD}</> <c>{time:HH:mm:ss}</> <m>{time:zz}</>] [<lvl>{level}</> | <y>{name}</>] {message}')
    if os.getenv("OBGW_DEBUG_MODE") == "True":
        logger.warning("调试模式已启用。请谨慎在生产环境下使用！")
        logger.add("logs/obgw-log_{time:YYYY-MM-DD_HH-mm-ss}_DEBUG.log", level="TRACE", format='[{time:YYYY-MM-DD HH:mm:ss zz}] [{level} | {name}] <DEBUGMSG:UPTIME({elapsed});MOD({module});LINE({line});PROC:({process:name} [PID {process:id}]);THREAD:({thread:name} [TID {thread:id}])> {message}')

    # 强兼 logging 到 loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

def splash():
    print(r"_______               ________        _____ _________        _____                                   ")
    print(r"__  __ \_______ _____ ___  __ )______ __  /___  ____/______ ___  /______ ___      ________ ______  __")
    print(r"_  / / /__  __ \_  _ \__  __  |_  __ \_  __/_  / __  _  __ `/_  __/_  _ \__ | /| / /_  __ `/__  / / /")
    print(r"/ /_/ / _  / / //  __/_  /_/ / / /_/ // /_  / /_/ /  / /_/ / / /_  /  __/__ |/ |/ / / /_/ / _  /_/ / ")
    print(r"\____/  /_/ /_/ \___/ /_____/  \____/ \__/  \____/   \__,_/  \__/  \___/ ____/|__/  \__,_/  _\__, /  ")
    print("                                                                                            /____/   ")
    print(f"OneBotGateway 版本 {os.getenv('OBGW_VERSION', "[!!! UNKNOWN VERSION | 未知版本 !!!]")}")
    print("正在启动...\n")

def run():
    print(b'114514')
    app.run(port=os.getenv("PORT", 9119), debug=bool(os.getenv("OBGW_DEBUG_MODE")))

if __name__ == '__main__':
    load_dotenv()
    if os.getenv("SUBENV"): load_dotenv(f'.env.{os.getenv("SUBENV")}')
    os.environ["OBGW_VERSION"] = "1.0.0.0-Axiom"
    splash()
    init_logger()
    str2l_out = StreamToLogger()
    with contextlib.redirect_stdout(str2l_out):
        run()
