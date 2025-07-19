import threading
from typing import Set, Dict, Type

class ProcessingRegistryBase:
    """Base singleton para controle de processamento concorrente"""
    _instances: Dict[Type, 'ProcessingRegistryBase'] = {}
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__new__(cls)
                    cls._instances[cls].processing_ids = set()
                    cls._instances[cls].processing_lock = threading.Lock()
        return cls._instances[cls]

    def is_processing(self, entity_id: str) -> bool:
        with self.processing_lock:
            return entity_id in self.processing_ids

    def start_processing(self, entity_id: str) -> bool:
        with self.processing_lock:
            if entity_id in self.processing_ids:
                return False
            self.processing_ids.add(entity_id)
            return True

    def finish_processing(self, entity_id: str) -> None:
        with self.processing_lock:
            self.processing_ids.discard(entity_id)

class VagaProcessingRegistry(ProcessingRegistryBase):
    """Registry específico para vagas"""
    pass

class ApplicantProcessingRegistry(ProcessingRegistryBase):
    """Registry específico para candidatos"""
    pass
