from pydantic import BaseModel


class ExcelImportOut(BaseModel):
    grade_table_id: int
    subject_name: str
    teacher_id: int
    imported_components: int
    imported_students: int
    imported_scores: int