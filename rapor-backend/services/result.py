from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.grade_component import GradeComponent
from models.score import Score
from models.student import Student
from models.user import User
from schemas.result import ComponentScoreOut, GradeTableResultOut, StudentResultOut
from services.grade_table import get_grade_table_by_id


def get_grade_table_results(
    grade_table_id: int,
    current_user: User,
    db: Session,
) -> GradeTableResultOut:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    components = (
        db.query(GradeComponent)
        .filter(GradeComponent.grade_table_id == grade_table.id)
        .order_by(GradeComponent.order_index.asc(), GradeComponent.id.asc())
        .all()
    )

    if not components:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade table has no components",
        )

    students = (
        db.query(Student)
        .filter(Student.grade_table_id == grade_table.id)
        .order_by(Student.id.asc())
        .all()
    )

    total_weight = sum(component.weight for component in components)

    if total_weight <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total component weight must be greater than 0",
        )

    scores = (
        db.query(Score)
        .join(Student, Score.student_id == Student.id)
        .filter(Student.grade_table_id == grade_table.id)
        .all()
    )

    score_map = {
        (score.student_id, score.component_id): score.score
        for score in scores
    }

    student_results: list[StudentResultOut] = []

    for student in students:
        weighted_total = 0.0
        component_scores: list[ComponentScoreOut] = []
        missing_components: list[str] = []

        for component in components:
            score_value = score_map.get((student.id, component.id))

            if score_value is None:
                missing_components.append(component.name)
                effective_score = 0.0
            else:
                effective_score = score_value

            weighted_total += effective_score * component.weight

            component_scores.append(
                ComponentScoreOut(
                    component_id=component.id,
                    component_name=component.name,
                    weight=component.weight,
                    score=score_value,
                )
            )

        final_grade = round(weighted_total / total_weight, 2)

        student_results.append(
            StudentResultOut(
                student_id=student.id,
                student_name=student.name,
                student_number=student.student_number,
                component_scores=component_scores,
                final_grade=final_grade,
                is_complete=len(missing_components) == 0,
                missing_components=missing_components,
            )
        )

    return GradeTableResultOut(
        grade_table_id=grade_table.id,
        subject_name=grade_table.subject_name,
        teacher_id=grade_table.teacher_id,
        teacher_name=grade_table.teacher.name,
        total_weight=total_weight,
        results=student_results,
    )