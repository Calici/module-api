from .base import TestBase

class TestRefresh(TestBase):
    def action(self):
        to_remove = [
            id 
            for id, entry in enumerate(self.lock.testing.get())
            if not entry.path.get().exists()
        ]
        for id in reversed(to_remove): self.lock.testing.remove(id)
        self.lock.save()
                