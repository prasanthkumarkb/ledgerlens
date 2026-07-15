class LedgerLensException(Exception):

    def __init__(
        self,
        message: str,
        status_code: int = 400
    ):
        self.message = message
        self.status_code = status_code


class DocumentNotFoundException(LedgerLensException):

    def __init__(self):
        super().__init__(
            "Document not found.",
            404
        )


class InvalidFileException(LedgerLensException):

    def __init__(self):
        super().__init__(
            "Only JPG, JPEG and PNG files are allowed.",
            400
        )


class AIExtractionException(LedgerLensException):

    def __init__(self):
        super().__init__(
            "Unable to extract invoice.",
            500
        )


class DatabaseException(LedgerLensException):

    def __init__(self):
        super().__init__(
            "Database operation failed.",
            500
        )