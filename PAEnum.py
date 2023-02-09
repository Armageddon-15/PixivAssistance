from enum import Enum


class DownloadState(Enum):
    successful = 0
    cannot_verify = 1
    failed = 2
    downloading = 3
    wait_to_download = 4
    unexpected_error = 5
    hint = 999


class NSFWState(Enum):
    all = 0
    sfw = 1
    nsfw = 2


class LikeDislike(Enum):
    like = 0
    dislike = 1
    hint = 2
