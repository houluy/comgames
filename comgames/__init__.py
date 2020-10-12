import logging

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
fmtter = logging.Formatter("%(name)s--%(levelname)s: %(message)s")
handler.setFormatter(fmtter)

#logger = logging.getLogger(__name__)
#logger.addHandler(handler)
#logger.setLevel(logging.DEBUG)
