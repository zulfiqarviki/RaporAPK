from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.grade_component import GradeComponent
from models.score import Score
from models.student import Student
from models.user import User
from schemas.analytics import (
    ComponentAverageOut,
    ComponentAveragesOut,
    StudentComparisonItemOut,
    StudentComparisonOut,
    StudentComparisonRequest,
    StudentProgressOut,
    StudentProgressPointOut,
)
from services.grade_table import get_grade_table_by_id


def get_component_averages(
    grade_table_id: int,
    current_user: User,
    db: Session,
) -> ComponentAveragesOut:
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

    students = (
        db.query(Student)
        .filter(Student.grade_table_id == grade_table.id)
        .all()
    )

    if not components:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade table has no components",
        )

    if not students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade table has no students",
        )

    total_students = len(students)

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

    component_averages: list[ComponentAverageOut] = []

    for component in components:
        total_score = 0.0
        filled_scores = 0

        for student in students:
            score_value = score_map.get((student.id, component.id))

            if score_value is not None:
                total_score += score_value
                filled_scores += 1

        missing_scores = total_students - filled_scores

        # Missing scores are treated as 0 for class average consistency.
        average_score = round(total_score / total_students, 2)

        component_averages.append(
            ComponentAverageOut(
                component_id=component.id,
                component_name=component.name,
                weight=component.weight,
                order_index=component.order_index,
                average_score=average_score,
                total_students=total_students,
                filled_scores=filled_scores,
                missing_scores=missing_scores,
            )
        )

    return ComponentAveragesOut(
        grade_table_id=grade_table.id,
        subject_name=grade_table.subject_name,
        component_averages=component_averages,
    )


def get_student_progress(
    grade_table_id: int,
    student_id: int,
    current_user: User,
    db: Session,
) -> StudentProgressOut:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    student = (
        db.query(Student)
        .filter(
            Student.id == student_id,
            Student.grade_table_id == grade_table.id,
        )
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found in this grade table",
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

    scores = (
        db.query(Score)
        .filter(Score.student_id == student.id)
        .all()
    )

    score_map = {
        score.component_id: score.score
        for score in scores
    }

    progress: list[StudentProgressPointOut] = []

    for component in components:
        progress.append(
            StudentProgressPointOut(
                component_id=component.id,
                component_name=component.name,
                weight=component.weight,
                order_index=component.order_index,
                score=score_map.get(component.id),
            )
        )

    return StudentProgressOut(
        grade_table_id=grade_table.id,
        subject_name=grade_table.subject_name,
        student_id=student.id,
        student_name=student.name,
        student_number=student.student_number,
        progress=progress,
    )


def compare_students(
    grade_table_id: int,
    comparison_data: StudentComparisonRequest,
    current_user: User,
    db: Session,
) -> StudentComparisonOut:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    if len(set(comparison_data.student_ids)) != len(comparison_data.student_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate student IDs are not allowed",
        )

    students = (
        db.query(Student)
        .filter(
            Student.grade_table_id == grade_table.id,
            Student.id.in_(comparison_data.student_ids),
        )
        .all()
    )

    if len(students) != len(comparison_data.student_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more students were not found in this grade table",
        )

    student_map = {
        student.id: student
        for student in students
    }

    ordered_students = [
        student_map[student_id]
        for student_id in comparison_data.student_ids
    ]

    if comparison_data.component_id is not None:
        return _compare_students_by_component(
            grade_table_id=grade_table.id,
            subject_name=grade_table.subject_name,
            students=ordered_students,
            component_id=comparison_data.component_id,
            db=db,
        )

    return _compare_students_by_final_grade(
        grade_table_id=grade_table.id,
        subject_name=grade_table.subject_name,
        students=ordered_students,
        db=db,
    )


def _compare_students_by_component(
    grade_table_id: int,
    subject_name: str,
    students: list[Student],
    component_id: int,
    db: Session,
) -> StudentComparisonOut:
    component = (
        db.query(GradeComponent)
        .filter(
            GradeComponent.id == component_id,
            GradeComponent.grade_table_id == grade_table_id,
        )
        .first()
    )

    if component is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component not found in this grade table",
        )

    scores = (
        db.query(Score)
        .filter(
            Score.component_id == component.id,
            Score.student_id.in_([student.id for student in students]),
        )
        .all()
    )

    score_map = {
        score.student_id: score.score
        for score in scores
    }

    comparison_items: list[StudentComparisonItemOut] = []

    for student in students:
        comparison_items.append(
            StudentComparisonItemOut(
                student_id=student.id,
                student_name=student.name,
                student_number=student.student_number,
                value=score_map.get(student.id),
                is_complete=score_map.get(student.id) is not None,
                missing_components=[] if score_map.get(student.id) is not None else [component.name],
            )
        )

    return StudentComparisonOut(
        grade_table_id=grade_table_id,
        subject_name=subject_name,
        comparison_type="component",
        component_id=component.id,
        component_name=component.name,
        students=comparison_items,
    )


def _compare_students_by_final_grade(
    grade_table_id: int,
    subject_name: str,
    students: list[Student],
    db: Session,
) -> StudentComparisonOut:
    components = (
        db.query(GradeComponent)
        .filter(GradeComponent.grade_table_id == grade_table_id)
        .order_by(GradeComponent.order_index.asc(), GradeComponent.id.asc())
        .all()
    )

    if not components:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade table has no components",
        )

    total_weight = sum(component.weight for component in components)

    if total_weight <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total component weight must be greater than 0",
        )

    scores = (
        db.query(Score)
        .filter(Score.student_id.in_([student.id for student in students]))
        .all()
    )

    score_map = {
        (score.student_id, score.component_id): score.score
        for score in scores
    }

    comparison_items: list[StudentComparisonItemOut] = []

    for student in students:
        weighted_total = 0.0
        missing_components: list[str] = []

        for component in components:
            score_value = score_map.get((student.id, component.id))

            if score_value is None:
                missing_components.append(component.name)
                effective_score = 0.0
            else:
                effective_score = score_value

            weighted_total += effective_score * component.weight

        final_grade = round(weighted_total / total_weight, 2)

        comparison_items.append(
            StudentComparisonItemOut(
                student_id=student.id,
                student_name=student.name,
                student_number=student.student_number,
                value=final_grade,
                is_complete=len(missing_components) == 0,
                missing_components=missing_components,
            )
        )

    return StudentComparisonOut(
        grade_table_id=grade_table_id,
        subject_name=subject_name,
        comparison_type="final_grade",
        component_id=None,
        component_name=None,
        students=comparison_items,
    )