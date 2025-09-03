# -*- coding: utf-8 -*-
"""
로깅 시스템 모듈
파일 로깅과 에러 알림을 통합 관리
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional

from .config import Config


class DiscordErrorHandler(logging.Handler):
    """에러 발생 시 Discord로 알림을 보내는 핸들러"""
    
    def __init__(self):
        super().__init__()
        self.setLevel(logging.ERROR)
        self._notifier = None
    
    @property
    def notifier(self):
        """notifier를 지연 임포트 (순환 참조 방지)"""
        if self._notifier is None:
            from .notifier import ErrorNotifier
            self._notifier = ErrorNotifier()
        return self._notifier
    
    def emit(self, record: logging.LogRecord) -> None:
        """에러 로그를 Discord로 전송"""
        if not Config.is_error_notification_enabled():
            return
        
        try:
            error_info = {
                'level': record.levelname,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'message': record.getMessage(),
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            }
            
            if record.exc_info:
                error_info['traceback'] = ''.join(
                    traceback.format_exception(*record.exc_info)
                )
            
            self.notifier.send_error(error_info)
        except Exception:
            # Discord 알림 실패 시 조용히 넘어감
            pass


def setup_logger(
    name: str = "news_bot",
    level: Optional[str] = None,
    log_dir: Optional[str] = None
) -> logging.Logger:
    """로거 설정 및 반환
    
    Args:
        name: 로거 이름
        level: 로그 레벨 (기본값: Config.LOG_LEVEL)
        log_dir: 로그 디렉토리 (기본값: Config.LOG_DIR)
    
    Returns:
        설정된 로거 인스턴스
    """
    logger = logging.getLogger(name)
    
    # 이미 설정된 경우 반환
    if logger.handlers:
        return logger
    
    # 로그 레벨 설정
    log_level = getattr(logging, (level or Config.LOG_LEVEL).upper())
    logger.setLevel(log_level)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러
    log_directory = log_dir or Config.LOG_DIR
    os.makedirs(log_directory, exist_ok=True)
    
    log_file = os.path.join(
        log_directory,
        f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Discord 에러 핸들러
    if Config.is_error_notification_enabled():
        discord_handler = DiscordErrorHandler()
        logger.addHandler(discord_handler)
    
    return logger


# 기본 로거 인스턴스
logger = setup_logger()


def log_execution_time(func):
    """함수 실행 시간을 로깅하는 데코레이터"""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"{func.__name__} 실행 시작")
        
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.info(f"{func.__name__} 완료 (소요시간: {elapsed_time:.2f}초)")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(
                f"{func.__name__} 실패 (소요시간: {elapsed_time:.2f}초): {str(e)}",
                exc_info=True
            )
            raise
    
    return wrapper