from __future__ import annotations


class TaskSOL:

    VALID_PRIORITIES: list[str] = ["low", "medium", "high"]

    def __init__(self, task: str, priority: str) -> None:
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {priority}")
        self.task: str = task
        self.priority: str = priority

    def canonical(self) -> dict[str, str]:
        return {
            "task": self.task,
            "priority": self.priority,
        }
