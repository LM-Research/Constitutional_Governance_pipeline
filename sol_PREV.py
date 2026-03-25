class TaskSOL:
    VALID_PRIORITIES = ["low", "medium", "high"]

    def __init__(self, task, priority):
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {priority}")

        self.task = task
        self.priority = priority

    def canonical(self):
        return {
            "task": self.task,
            "priority": self.priority
        }
