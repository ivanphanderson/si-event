from django.urls import path
from .views import (
    create_event,
    input_employee_to_event,
    get_options,
    get_events,
    riwayat_events,
    detail_event,
    update_event,
    submit_update_event,
    update_event_employee_by_id,
    update_employee_to_event_by_id,
    delete_event_employee_by_id,
    submit_input_employee_to_existing_event,
    input_employee_to_existing_event,
    generate_docs,
    form_surat_tugas,
    validate_event,
    reject_event,
    upload_surat_tugas,
    reupload_surat_tugas
)

urlpatterns = [
    path("", get_events, name="get_events"),
    path("create", create_event, name="create_event"),
    path("input_employee", input_employee_to_event, name="input_employee_to_event"),
    path("get-options/", get_options, name="get_options"),
    path("my-event", riwayat_events, name="riwayat_events"),
    path("detail/<id>", detail_event, name="detail_event"),
    path("update/<id>", update_event, name="update_event"),
    path("submit-update/<id>", submit_update_event, name="submit_update_event"),
    path(
        "add-employee/<id>",
        input_employee_to_existing_event,
        name="input_employee_to_existing_event",
    ),
    path(
        "submit-add-employee/<id>",
        submit_input_employee_to_existing_event,
        name="submit_input_employee_to_existing_event",
    ),
    path(
        "update-employee/<id>",
        update_event_employee_by_id,
        name="update_event_employee_by_id",
    ),
    path(
        "submit-update-employee/<id>",
        update_employee_to_event_by_id,
        name="submit_update_employee_by_id",
    ),
    path(
        "delete-employee/<id>",
        delete_event_employee_by_id,
        name="delete_Event_employee_by_id",
    ),
    path(
        "download-docx/<event_id>", generate_docs, name="download_as_docx"
    ),
    path("form-surat-tugas/<event_id>", form_surat_tugas, name="form_surat_tugas"),
    path(
        "validate-event/<id>",
        validate_event,
        name="validate_event",
    ),
    path(
        "reject-event/<id>",
        reject_event,
        name="reject_event",
    ),
    path(
        "upload-surat-tugas/<id>",
        upload_surat_tugas,
        name="upload_surat_tugas",
    ),
    path(
        "reupload-surat-tugas/<id>/<file_id>",
        reupload_surat_tugas,
        name="reupload_surat_tugas",
    ),
]
