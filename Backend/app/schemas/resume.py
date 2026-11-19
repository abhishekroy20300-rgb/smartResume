from pydantic import BaseModel, Field
from typing import Optional, List


class ResumeData(BaseModel):

    name: Optional[str] = None

    email: Optional[str] = None

    phone: Optional[str] = None

    skills: List[str] = Field(default_factory=list)

    education: List[str] = Field(default_factory=list)

    experience: List[str] = Field(default_factory=list)

    projects: List[str] = Field(default_factory=list)

    experience_years: Optional[float] = None

    score: int = 0

    maximum_score: int = 100

    feedback: List[str] = Field(default_factory=list)