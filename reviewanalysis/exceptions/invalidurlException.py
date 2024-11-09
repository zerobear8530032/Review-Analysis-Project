# custom_exceptions.py

class InvalidURLException(Exception):
    """Exception raised for errors in the input URL."""
    def __init__(self, url, message="The entered URL is not valid."):
        self.url = url
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: '{self.url}'"

