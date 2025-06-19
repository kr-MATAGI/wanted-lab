import logging


def setup_logger(name: str, log_level: int = logging.DEBUG):
    """
    Application 에서 사용할 Logger 설정

    Args:
        name (str): Logger 이름
    
    Returns:
        logging.Logger: Logger 인스턴스
    """
    
    logger = logging.getLogger(name)
    logger.setLevel(log_level) # DEBUG 레벨이후 모두 캡처

    if logger.handlers:
        # Handler가 이미 있는 경우
        return logger
    
    # Format 설정
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set Handler
    log_handler =  logging.StreamHandler()
    log_handler.setFormatter(log_format)
    log_handler.setLevel(log_level)
    
    logger.addHandler(log_handler)

    return logger


    
    