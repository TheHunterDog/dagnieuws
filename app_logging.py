class Logging:
    def __init__(self, write_to_file: bool = False, source: str = None, verbosity: int = 0):
        self.write_to_file = write_to_file
        self.source = source
        self.log_history = []
        self.verbosity = verbosity

    def __write_to_file__(self, message):
        if self.write_to_file:
            with open("log.txt", "a") as log_file:
                log_file.write(message + "\n")

    def __add_log_history__(self, message):
        # Limit amount of logs to keep in memory
        if len(self.log_history) > 100:
            self.log_history.pop(0)
        self.log_history.append(message)

    def get_log_history(self):
        return self.log_history

    def __log__(self, message, verbosity: int = 0):
        # if a message is lower or equal to the loggings verbosisty we can print and log it. If not we can skip it
        if verbosity <= self.verbosity:
            log_str = f"[{self.source}]: {message}"
            print(log_str)
            self.__add_log_history__(log_str)
            self.__write_to_file__(log_str)

    def error(self, message):
        self.__log__(f"ERROR: {message}", 0)

    def warn(self, message):
        self.__log__(f"WARNING: {message}", 1)

    def info(self, message):
        self.__log__(f"INFO: {message}", 2)
