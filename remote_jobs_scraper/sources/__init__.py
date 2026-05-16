"""Registry of available job board source adapters."""

from .arbeitnow import Arbeitnow
from .base import Source
from .himalayas import Himalayas
from .remoteok import RemoteOK
from .remotive import Remotive
from .weworkremotely import WeWorkRemotely

ALL_SOURCES: dict[str, type[Source]] = {
    cls.name: cls
    for cls in (Remotive, RemoteOK, Himalayas, WeWorkRemotely, Arbeitnow)
}

__all__ = ["ALL_SOURCES", "Source"]
