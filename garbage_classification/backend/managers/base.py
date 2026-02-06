from abc import ABC, abstractmethod

class BaseManager(ABC):
    """Base class for all admin functional managers."""
    
    @abstractmethod
    def get_data(self, **kwargs):
        """Standard method to retrieve data managed by this manager."""
        pass
