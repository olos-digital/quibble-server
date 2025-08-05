class LinkedInConnectionException(Exception):
    def __init__(self, message="Failed to connect to LinkedIn"):
        self.message = message
        super().__init__(self.message)