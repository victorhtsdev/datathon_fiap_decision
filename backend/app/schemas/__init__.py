from .applicant import ApplicantIn
from .vaga import VagaBase, VagaCreate
from .workbook import WorkbookBase, WorkbookCreate, WorkbookUpdate, WorkbookResponse
from .processed_applicant import (
    ProcessedApplicantBase, 
    ProcessedApplicantCreate, 
    ProcessedApplicantUpdate, 
    ProcessedApplicantResponse, 
    ProcessedApplicantSummary
)
from .match_prospect import (
    MatchProspectBase, 
    MatchProspectCreate, 
    MatchProspectResponse, 
    MatchProspectsUpdate
)
