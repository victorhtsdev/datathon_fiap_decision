# Arquivo de utilitários para tratamento de erros
from fastapi import HTTPException, status

class APIExceptions:
    @staticmethod
    def not_found(resource: str, resource_id: str = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" with ID: {resource_id}"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )
    
    @staticmethod
    def conflict(message: str = "Resource conflict"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )
    
    @staticmethod
    def internal_error(message: str = "Internal server error"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
