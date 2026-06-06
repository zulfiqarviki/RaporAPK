from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth_dependency import get_current_user
from models.user import User
from services.excel import export_grade_table_to_excel


router = APIRouter(tags=["Excel"])


@router.get("/grade-tables/{grade_table_id}/export/excel")
def export_grade_table_excel(
    grade_table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    excel_file = export_grade_table_to_excel(
        grade_table_id=grade_table_id,
        current_user=current_user,
        db=db,
    )

    filename = f"grade-table-{grade_table_id}.xlsx"
    encoded_filename = quote(filename)

    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
    }

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )