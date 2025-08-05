class ValueNotFoundException(Exception):
    def __init__(self, message="Value not found"):
        self.message = message
        super().__init__(self.message)