from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    def extract_section(self, section_name: str, schema_snippet: str, cv_text: str) -> dict:
        pass
