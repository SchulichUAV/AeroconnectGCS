# Define priority levels for messages

from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)

heartbeat_pri = 3
nav_pri = 2
stream_pri = 1
