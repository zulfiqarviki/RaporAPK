from datetime import datetime
from io import BytesIO

from fastapi import HTTPException, status
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session

from models.grade_component import GradeComponent
from models.score import Score
from models.student import Student
from models.user import User
from services.grade_table import get_grade_table_by_id


def export_grade_table_to_excel(
    grade_table_id: int,
    current_user: User,
    db: Session,
) -> BytesIO:
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
        .order_by(Student.id.asc())
        .all()
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

    workbook = Workbook()

    metadata_sheet = workbook.active
    metadata_sheet.title = "Metadata"

    _write_metadata_sheet(
        sheet=metadata_sheet,
        grade_table=grade_table,
    )

    components_sheet = workbook.create_sheet("Components")
    _write_components_sheet(
        sheet=components_sheet,
        components=components,
    )

    scores_sheet = workbook.create_sheet("Scores")
    _write_scores_sheet(
        sheet=scores_sheet,
        students=students,
        components=components,
        score_map=score_map,
    )

    results_sheet = workbook.create_sheet("Results")
    _write_results_sheet(
        sheet=results_sheet,
        students=students,
        components=components,
        score_map=score_map,
    )

    for sheet in workbook.worksheets:
        _style_header_row(sheet)
        _auto_fit_columns(sheet)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output


def _write_metadata_sheet(sheet, grade_table) -> None:
    rows = [
        ("Grade Table ID", grade_table.id),
        ("Subject Name", grade_table.subject_name),
        ("Description", grade_table.description or ""),
        ("Teacher ID", grade_table.teacher_id),
        ("Teacher NIP", grade_table.teacher.nip),
        ("Teacher Name", grade_table.teacher.name),
        ("Exported At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    ]

    sheet.append(["Field", "Value"])

    for row in rows:
        sheet.append(list(row))


def _write_components_sheet(
    sheet,
    components: list[GradeComponent],
) -> None:
    sheet.append(
        [
            "Component ID",
            "Component Name",
            "Weight",
            "Max Score",
            "Order Index",
        ]
    )

    for component in components:
        sheet.append(
            [
                component.id,
                component.name,
                component.weight,
                component.max_score,
                component.order_index,
            ]
        )


def _write_scores_sheet(
    sheet,
    students: list[Student],
    components: list[GradeComponent],
    score_map: dict[tuple[int, int], float],
) -> None:
    header = [
        "Student ID",
        "Student Number",
        "Student Name",
    ]

    for component in components:
        header.append(component.name)

    sheet.append(header)

    for student in students:
        row = [
            student.id,
            student.student_number or "",
            student.name,
        ]

        for component in components:
            score_value = score_map.get((student.id, component.id))

            # Raw score is left blank if missing.
            # This preserves the difference between actual 0 and missing score.
            row.append(score_value if score_value is not None else "")

        sheet.append(row)


def _write_results_sheet(
    sheet,
    students: list[Student],
    components: list[GradeComponent],
    score_map: dict[tuple[int, int], float],
) -> None:
    sheet.append(
        [
            "Student ID",
            "Student Number",
            "Student Name",
            "Final Grade",
            "Is Complete",
            "Missing Components",
        ]
    )

    total_weight = sum(component.weight for component in components)

    if components and total_weight <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total component weight must be greater than 0",
        )

    for student in students:
        final_grade, is_complete, missing_components = _calculate_final_grade(
            student=student,
            components=components,
            score_map=score_map,
            total_weight=total_weight,
        )

        sheet.append(
            [
                student.id,
                student.student_number or "",
                student.name,
                final_grade,
                "Yes" if is_complete else "No",
                ", ".join(missing_components),
            ]
        )


def _calculate_final_grade(
    student: Student,
    components: list[GradeComponent],
    score_map: dict[tuple[int, int], float],
    total_weight: float,
) -> tuple[float | None, bool, list[str]]:
    if not components:
        return None, False, []

    weighted_total = 0.0
    missing_components: list[str] = []

    for component in components:
        score_value = score_map.get((student.id, component.id))

        if score_value is None:
            effective_score = 0.0
            missing_components.append(component.name)
        else:
            effective_score = score_value

        weighted_total += effective_score * component.weight

    final_grade = round(weighted_total / total_weight, 2)
    is_complete = len(missing_components) == 0

    return final_grade, is_complete, missing_components


def _style_header_row(sheet) -> None:
    if sheet.max_row < 1:
        return

    for cell in sheet[1]:
        cell.font = Font(bold=True)


def _auto_fit_columns(sheet) -> None:
    for column_cells in sheet.columns:
        max_length = 0
        column_letter = get_column_letter(column_cells[0].column)

        for cell in column_cells:
            if cell.value is None:
                continue

            value_length = len(str(cell.value))

            if value_length > max_length:
                max_length = value_length

        adjusted_width = max_length + 2
        sheet.column_dimensions[column_letter].width = adjusted_width