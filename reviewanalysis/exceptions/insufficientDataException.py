class InsufficientDataException(Exception):
    """Exception raised when insufficient data is scraped for analysis."""
    def __init__(self, message="Not enough data scraped for analysis."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
