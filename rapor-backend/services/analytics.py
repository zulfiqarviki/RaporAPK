from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.grade_component import GradeComponent
from models.score import Score
from models.student import Student
from models.user import User
from schemas.analytics import (
    AnalyticsSummaryOut,
    ComponentSummaryOut,
    DistributionBucketOut,
    DistributionOut,
    DistributionRange,
    DistributionRequest,
    StudentComparisonItemOut,
    StudentComparisonOut,
    StudentComparisonRequest,
    StudentComponentScoreOut,
    StudentFinalGradeOut,
    StudentProgressOut,
    StudentProgressPointOut,
)
from services.grade_table import get_grade_table_by_id


def _get_components(grade_table_id: int, db: Session) -> list[GradeComponent]:
    return (
        db.query(GradeComponent)
        .filter(GradeComponent.grade_table_id == grade_table_id)
        .order_by(GradeComponent.order_index.asc(), GradeComponent.id.asc())
        .all()
    )


def _get_students(grade_table_id: int, db: Session) -> list[Student]:
    return (
        db.query(Student)
        .filter(Student.grade_table_id == grade_table_id)
        .order_by(Student.id.asc())
        .all()
    )


def _get_score_map(grade_table_id: int, db: Session) -> dict[tuple[int, int], float]:
    scores = (
        db.query(Score)
        .join(Student, Score.student_id == Student.id)
        .filter(Student.grade_table_id == grade_table_id)
        .all()
    )

    return {
        (score.student_id, score.component_id): score.score
        for score in scores
    }


def _validate_grade_table_has_data(
    components: list[GradeComponent],
    students: list[Student],
) -> None:
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


def _calculate_final_grade_for_student(
    student: Student,
    components: list[GradeComponent],
    score_map: dict[tuple[int, int], float],
) -> StudentFinalGradeOut:
    total_weight = sum(component.weight for component in components)

    if total_weight <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total component weight must be greater than 0",
        )

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

    return StudentFinalGradeOut(
        student_id=student.id,
        student_name=student.name,
        student_number=student.student_number,
        final_grade=final_grade,
        is_complete=len(missing_components) == 0,
        missing_components=missing_components,
    )


def get_analytics_summary(
    grade_table_id: int,
    current_user: User,
    db: Session,
) -> AnalyticsSummaryOut:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    components = _get_components(grade_table.id, db)
    students = _get_students(grade_table.id, db)

    _validate_grade_table_has_data(
        components=components,
        students=students,
    )

    score_map = _get_score_map(grade_table.id, db)

    final_grade_items = [
        _calculate_final_grade_for_student(
            student=student,
            components=components,
            score_map=score_map,
        )
        for student in students
    ]

    final_grade_average = round(
        sum(item.final_grade for item in final_grade_items) / len(final_grade_items),
        2,
    )

    highest_final_grade = max(
        final_grade_items,
        key=lambda item: item.final_grade,
        default=None,
    )

    lowest_final_grade = min(
        final_grade_items,
        key=lambda item: item.final_grade,
        default=None,
    )

    component_summaries: list[ComponentSummaryOut] = []

    for component in components:
        component_score_items: list[StudentComponentScoreOut] = []
        filled_scores = 0
        total_score_with_missing_as_zero = 0.0

        for student in students:
            score_value = score_map.get((student.id, component.id))

            if score_value is None:
                effective_score = 0.0
                is_missing = True
            else:
                effective_score = score_value
                is_missing = False
                filled_scores += 1

            component_score_items.append(
                StudentComponentScoreOut(
                    student_id=student.id,
                    student_name=student.name,
                    student_number=student.student_number,
                    score=effective_score,
                    is_missing=is_missing,
                )
            )

            total_score_with_missing_as_zero += effective_score

        missing_scores = len(students) - filled_scores

        average_score = round(
            total_score_with_missing_as_zero / len(students),
            2,
        )

        highest_score = max(
            component_score_items,
            key=lambda item: item.score,
            default=None,
        )

        lowest_score = min(
            component_score_items,
            key=lambda item: item.score,
            default=None,
        )

        component_summaries.append(
            ComponentSummaryOut(
                component_id=component.id,
                component_name=component.name,
                weight=component.weight,
                order_index=component.order_index,
                average_score=average_score,
                highest_score=highest_score,
                lowest_score=lowest_score,
                total_students=len(students),
                filled_scores=filled_scores,
                missing_scores=missing_scores,
            )
        )

    return AnalyticsSummaryOut(
        grade_table_id=grade_table.id,
        subject_name=grade_table.subject_name,
        total_students=len(students),
        total_components=len(components),
        final_grade_average=final_grade_average,
        highest_final_grade=highest_final_grade,
        lowest_final_grade=lowest_final_grade,
        component_summaries=component_summaries,
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

    components = _get_components(grade_table.id, db)

    if not components:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade table has no components",
        )

    scores = db.query(Score).filter(Score.student_id == student.id).all()

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
        score_value = score_map.get(student.id)

        comparison_items.append(
            StudentComparisonItemOut(
                student_id=student.id,
                student_name=student.name,
                student_number=student.student_number,
                value=score_value,
                is_complete=score_value is not None,
                missing_components=[] if score_value is not None else [component.name],
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
    components = _get_components(grade_table_id, db)

    if not components:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade table has no components",
        )

    score_map = _get_score_map(grade_table_id, db)

    comparison_items: list[StudentComparisonItemOut] = []

    for student in students:
        result = _calculate_final_grade_for_student(
            student=student,
            components=components,
            score_map=score_map,
        )

        comparison_items.append(
            StudentComparisonItemOut(
                student_id=result.student_id,
                student_name=result.student_name,
                student_number=result.student_number,
                value=result.final_grade,
                is_complete=result.is_complete,
                missing_components=result.missing_components,
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


def get_distribution(
    grade_table_id: int,
    distribution_data: DistributionRequest,
    current_user: User,
    db: Session,
) -> DistributionOut:
    grade_table = get_grade_table_by_id(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    if distribution_data.target == "component":
        return _get_component_distribution(
            grade_table_id=grade_table.id,
            subject_name=grade_table.subject_name,
            distribution_data=distribution_data,
            db=db,
        )

    return _get_final_grade_distribution(
        grade_table_id=grade_table.id,
        subject_name=grade_table.subject_name,
        distribution_data=distribution_data,
        db=db,
    )


def _get_final_grade_distribution(
    grade_table_id: int,
    subject_name: str,
    distribution_data: DistributionRequest,
    db: Session,
) -> DistributionOut:
    components = _get_components(grade_table_id, db)
    students = _get_students(grade_table_id, db)

    _validate_grade_table_has_data(
        components=components,
        students=students,
    )

    score_map = _get_score_map(grade_table_id, db)

    final_grade_values = [
        _calculate_final_grade_for_student(
            student=student,
            components=components,
            score_map=score_map,
        ).final_grade
        for student in students
    ]

    buckets = _count_distribution(
        values=final_grade_values,
        ranges=distribution_data.ranges,
    )

    return DistributionOut(
        grade_table_id=grade_table_id,
        subject_name=subject_name,
        target="final_grade",
        component_id=None,
        component_name=None,
        total_counted=len(final_grade_values),
        missing_count=0,
        distribution=buckets,
    )


def _get_component_distribution(
    grade_table_id: int,
    subject_name: str,
    distribution_data: DistributionRequest,
    db: Session,
) -> DistributionOut:
    if distribution_data.component_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="component_id is required when target is component",
        )

    component = (
        db.query(GradeComponent)
        .filter(
            GradeComponent.id == distribution_data.component_id,
            GradeComponent.grade_table_id == grade_table_id,
        )
        .first()
    )

    if component is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component not found in this grade table",
        )

    students = _get_students(grade_table_id, db)

    if not students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade table has no students",
        )

    scores = (
        db.query(Score)
        .join(Student, Score.student_id == Student.id)
        .filter(
            Student.grade_table_id == grade_table_id,
            Score.component_id == component.id,
        )
        .all()
    )

    score_map = {
        score.student_id: score.score
        for score in scores
    }

    score_values: list[float] = []
    missing_count = 0

    for student in students:
        score_value = score_map.get(student.id)

        if score_value is None:
            score_values.append(0.0)
            missing_count += 1
        else:
            score_values.append(score_value)

    buckets = _count_distribution(
        values=score_values,
        ranges=distribution_data.ranges,
    )

    return DistributionOut(
        grade_table_id=grade_table_id,
        subject_name=subject_name,
        target="component",
        component_id=component.id,
        component_name=component.name,
        total_counted=len(score_values),
        missing_count=missing_count,
        distribution=buckets,
    )


def _count_distribution(
    values: list[float],
    ranges: list[DistributionRange],
) -> list[DistributionBucketOut]:
    bucket_counts = {
        range_item.label: 0
        for range_item in ranges
    }

    for value in values:
        for index, range_item in enumerate(ranges):
            is_last_range = index == len(ranges) - 1

            if is_last_range:
                is_inside_range = range_item.min <= value <= range_item.max
            else:
                is_inside_range = range_item.min <= value < range_item.max

            if is_inside_range:
                bucket_counts[range_item.label] += 1
                break

    return [
        DistributionBucketOut(
            label=range_item.label,
            min=range_item.min,
            max=range_item.max,
            count=bucket_counts[range_item.label],
        )
        for range_item in ranges
    ]