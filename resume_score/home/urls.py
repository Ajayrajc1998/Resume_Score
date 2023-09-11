from django.urls import path
from . import views  # Import your views module

urlpatterns = [
    # Other URL patterns
    path("", views.home, name="home"),
    path("resume_score", views.resume_score, name="resume_score"),
    path("test", views.test, name="test"),
    path("upload/", views.upload_file, name="upload_file"),
    path("add_job", views.add_job, name="add_job"),
    path("job_description", views.job_description, name="job_description"),
    path("adminupload/", views.upload_file_admin, name="adminupload"),
    path("login", views.custom_login, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("resume_scores", views.resume_score_HR, name="resume_scores"),
    path("upload_pdf_HR", views.upload_pdf_HR, name="upload_pdf_HR"),
    path("upload_skill_HR", views.upload_skill_HR, name="upload_skill_HR"),
    path("edit_HR", views.edit_HR, name="edit_HR"),
    path("save_skills", views.save_skills, name="save_skills"),
    path("delete_job/<int:job_id>/", views.delete_job, name="delete_job"),
    path("edit_job/<int:job_id>/", views.edit_job, name="edit_job"),
    path("view-pdf/<int:file_id>/", views.view_pdf, name="view_pdf"),
    path("applicants_view", views.applicants_view, name="applicants_view"),
    path("get_job_description/", views.get_job_description, name="get_job_description"),
    path("delete-file/<int:file_id>/", views.delete_file, name="delete_file"),
]
