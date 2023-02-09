

class DownloadIllustError(Exception):
    """
    Basic custom error for downloading illust
    """
    def __init__(self, reason):
        super(DownloadIllustError, self).__init__(reason)
        self.reason = reason


class RetryMaxError(DownloadIllustError):
    """
    download retry time over the setting
    """
    pass


class InterruptError(DownloadIllustError):
    """
    download illust failed
    """
    pass


class CannotVerifyError(DownloadIllustError):
    """
    download illust cannot be verified
    """
    pass
