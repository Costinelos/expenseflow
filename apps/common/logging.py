import logging


class SensitiveDataFilter(logging.Filter):
    SENSITIVE_KEYS = {"password", "token", "access", "refresh", "authorization", "secret"}

    def filter(self, record):
        if isinstance(record.args, dict):
            record.args = {
                k: "***MASKED***" if k.lower() in self.SENSITIVE_KEYS else v
                for k, v in record.args.items()
            }
        return True