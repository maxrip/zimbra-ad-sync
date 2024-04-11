import logging


class MyLogger(logging.Logger):
    def __init__(self,level):
        #formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        #formatter = logging.Formatter('%(name)s.%(funcName)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        super(MyLogger,self).__init__('app-sync')
        self.setLevel(self.getLevel(level))
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.addHandler(ch)
        self.info('curent log level: %s',level)

    
    def getLevel(self,level):
        match level:
            case "debug":
                return logging.DEBUG
            case "warning":
                return logging.WARNING
            case "error":
                return logging.ERROR
            case "critical":
                return logging.CRITICAL
            case _:
                return logging.INFO