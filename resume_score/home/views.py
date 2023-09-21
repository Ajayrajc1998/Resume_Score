from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, authenticate
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseNotFound, FileResponse
from home.models import UploadedFile, Job, Resume,Application_result
from django.contrib import messages
import requests
import json
import spacy
import en_core_web_lg
from spacy.matcher import PhraseMatcher
from skillNer.skill_extractor_class import SkillExtractor
from skillNer.general_params import SKILL_DB
import PyPDF2
import io
import string
import nltk
from nltk.corpus import stopwords
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from django.contrib.auth import authenticate, login
from thefuzz import fuzz
from django.views.decorators.csrf import csrf_exempt
from polyfuzz import PolyFuzz
from polyfuzz.models import Embeddings
from flair.embeddings import TransformerWordEmbeddings
from django.contrib.auth import login, logout
from .forms import SkillEditForm
from urllib.parse import quote

# home page
def home(request):
    if request.method == "POST":
        # Handle login form submission here
        # Validate user input, authenticate, and handle login logic
        pass
    else:
        is_score_check_show = True
        # If GET request, render the login form
        return render(
            request, "home.html", {"is_score_check_show": is_score_check_show}
        )


def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  # Use Django's login method to log in the user
            return redirect(
                "home"
            )  # Redirect to a protected page (adjust 'home' to your URL name)
        else:
            # Handle incorrect login credentials
            pass

    return render(request, "login.html")


# logout function for admin/HR
def logout_view(request):
    logout(request)
    return redirect("home")


# HR side resume score checking function
def resume_score_HR(request):
    jobs = Job.objects.all()
    context = {"jobs": jobs}
    return render(request, "resume_score_HR.html", context)


# Function for multiple PDF uploading and score checking
def upload_pdf_HR(request):
    if request.method == "POST" and request.FILES.getlist("pdf_files"):
        pdf_files = request.FILES.getlist("pdf_files")
        job_id = request.POST.get("job_id")
        score_req = int(request.POST.get("score_req"))
        matching_resume = Resume.objects.filter(title=job_id)
        job_skill = []
        for job in matching_resume:
            job_skill.append(job.skills)

        applicant_skills = []
        for pdf_file in pdf_files:
            text = extract_text_from_pdf(pdf_file)
            applicant_skill = list(skill_extraction(text))
            applicant_skills.append(applicant_skill)

        scores = []
        status = []
        for applicant_skill in applicant_skills:
            score = score_check(job_skill, applicant_skill)
            scores.append(score)
            if score >= score_req:
                status.append("Passed")
            else:
                status.append("Failed")
        result_data = {}
        # Create and save Application_result objects for each applicant
        for idx, pdf_file in enumerate(pdf_files):
            score = score_check(job_skill, applicant_skills[idx])
            status = "Passed" if score >= score_req else "Failed"

            # Create and save Application_result object for each applicant
            Application_result.objects.create(
                status=status,
                title=job_id,
                score_threshold=score_req
            )

            # Add data to the result_data dictionary
            result_data[pdf_file.name] = {"score": score, "status": status}


        # Count the number of applicants who passed

        return JsonResponse(
            {"message": "PDFs uploaded successfully.", "results": result_data}
        )

    return JsonResponse({"message": "Upload failed."}, status=400)

    # Process each uploaded PDF file (save to storage, database, etc.)
    # You can access each file using `for pdf_file in pdf_files:`


def resume_score(request):
    if request.method == "POST":
        pass
    else:
        return render(request, "resume_score.html")


def test(request):
    jobs = Job.objects.all()
    # Replace with your actual skills data
    is_score_check_show = True
    context = {"jobs": jobs}
    return render(request, "test.html", context)


# user side resume uploading
# def upload_file(request):
#     if request.method == 'POST' and 'pdf_file' in request.FILES:
#         pdf_file = request.FILES['pdf_file']
#         job_id = request.POST.get('job_id')

#         # Save the extracted data to your Django model
#         if name and email:
#             uploaded_file = UploadedFile.objects.create(name=name[0], email=email[0], pdf_file=pdf_file)
#             uploaded_file.save()
#             print('File uploaded and processed successfully')
#             text=extract_text_from_pdf(pdf_file)
#             skills=list(skill_extraction(text))
#             print(skills)

#             context = {
#                     'job_title':job_id,
#                     'skills': skills
#                     }
#             return render(request, 'your_template.html', context)
#         else:
#             return render(request, 'test.html' )
#         # For example, you might save it or perform operations on it


def get_job_description(request):
    if request.method == "POST":
        job_title = request.POST.get("selectedJob")
        print("JOBBBBBBBBBBBB", job_title)
        try:
            job = Job.objects.get(title=job_title)
            job_description = job.description
            return JsonResponse({"job_description": job_description})
        except Job.DoesNotExist:
            return JsonResponse({"error": "Job not found"}, status=400)
    return JsonResponse({}, status=400)


def upload_file(request):
    if request.method == "POST" and "pdf_file" in request.FILES:
        pdf_file = request.FILES["pdf_file"]
        job_id = request.POST.get("job_id")
        print("the job id is ", job_id)
        name = request.POST.get("name")
        email = request.POST.get("email")
        print(name, email)
        # Process the PDF file and extract text/skills if needed
        text = extract_text_from_pdf(pdf_file)
        applicant_skills = list(skill_extraction(text))
        # print(applicant_skills)
        # Get other form data
        # Save to database
        matching_resume = Resume.objects.filter(title=job_id)
        print(matching_resume)
        # job_skills=matching_resume.skills
        job_skills = []
        for job in matching_resume:
            job_skills.append(job.skills)
        # print(job_skill)
        score_req=Job.objects.get(title=job_id)
        score = score_check(job_skills, applicant_skills)
        status='Passed' if score>=score_req.score_threshold else 'Failed'
        your_skills, recommended_skills = comparing_skills(job_skills, applicant_skills)
        uploaded_file = UploadedFile.objects.create(
            name=name, email=email, pdf_file=pdf_file, score=score, job=job_id,status=status
        )
        print("Your score:::", score)
        print("your_skills:::", your_skills)
        print("recommended_skills::", recommended_skills)
        context = {
            "job_title": job_id,
            "your_skills": applicant_skills,
            "recommended_skills": recommended_skills,
            "score": score,
        }

        return JsonResponse(context)
    else:
        return JsonResponse({"error": "Invalid request"})


# Use csrf_exempt for simplicity in this example, but handle CSRF properly in production.
def save_skills(request):
    if request.method == "POST":
        job_title = request.POST.get("job")
        skill_name = request.POST.get("skill")

        if job_title and skill_name:
            # Create a new Resume instance with the job title and skill
            resume = Resume(title=job_title, skills=skill_name)
            resume.save()

            return redirect(edit_HR)

    return JsonResponse({"message": "Application not saved"}, status=400)


# function for comparing applicant skills and job skills using bert based text similarity
def comparing_skills(job_skills, applicant_skills):
    embeddings = TransformerWordEmbeddings("bert-base-multilingual-cased")
    bert = Embeddings(embeddings)
    bert_model = PolyFuzz(bert)
    bert_model.match(job_skills, applicant_skills)
    matches = bert_model.get_matches()
    your_skills = []
    for index, row in matches.iterrows():
        if row["Similarity"] >= 0.8:
            your_skills.append(row["From"])
    recommended_skill = [skill for skill in job_skills if skill not in your_skills]
    print("You Skills (>= 90% similarity):", your_skills)
    print("Recommended Skills:", recommended_skill)
    return your_skills, recommended_skill


# admin side job title and  description uploading
@login_required
def job_description(request):
    jobs = Job.objects.all()
    # Replace with your actual skills data
    context = {"jobs": jobs}
    return render(request, "job_description.html", context)


@login_required
def add_job(request):
    if request.method == "POST":
        job_title = request.POST["job_title"]
        job_description = request.POST["job_description"]
        score_threshold = request.POST["score_threshold"]
        if job_title and job_description:
            Job.objects.create(
                title=job_title,
                description=job_description,
                score_threshold=score_threshold,
            )
            messages.success(request, "Job added successfully.")
            return redirect("job_description")
        else:
            messages.error(request, "Please fill in both job title and description.")
            return redirect("job_description")


# admin/HR side job editing function


def edit_HR(request):
    jobs = Job.objects.all()
    skills = Resume.objects.all()
    return render(request, "edit_HR.html", {"jobs": jobs, "job_skills": skills})

def update_skill(request, skill_id):
    if request.method == 'POST':
        try:
            skill = Resume.objects.get(id=skill_id)
            data = json.loads(request.body)
            skill.title = data.get('title', skill.title)
            skill.skills = data.get('skills', skill.skills)
            skill.save()
            return JsonResponse({'message': 'Skill updated successfully'})
        except Resume.DoesNotExist:
            return JsonResponse({'message': 'Skill not found'}, status=404)

    return JsonResponse({'message': 'Invalid request method'}, status=400)

def delete_skill(request, skill_id):
    if request.method == 'POST':
        try:
            skill = Resume.objects.get(id=skill_id)
            skill.delete()
            return JsonResponse({'message': 'Skill deleted successfully'})
        except Resume.DoesNotExist:
            return JsonResponse({'message': 'Skill not found'}, status=404)

    return JsonResponse({'message': 'Invalid request method'}, status=400)




#########################################################################
# editing function
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == "POST":
        job.title = request.POST["job_title"]
        job.description = request.POST["job_description"]  # Update job description
        job.score_threshold = request.POST["score_threshold"]
        job.save()
        return JsonResponse({"message": "Job updated successfully"})
    return render(request, "edit_HR.html", {"job": job})


def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == "POST":
        job.delete()
        print(f"Deleted job with ID {job_id}")
        return redirect("edit_HR")
    return render(request, "edit_HR.html", {"job": job})


# admin/HR side applicants data viewing and downloading PDF's
############################################################
from django.template.loader import render_to_string
from django.db.models import Q


@login_required
def applicants_view(request):
    query = request.GET.get("q")  # Get the search query from the request
    files = UploadedFile.objects.all()

    if query:
        files = files.filter(
            Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(job__icontains=query)
        )

    return render(request, "applicants_view.html", {"files": files, "query": query})


def delete_file(request, file_id):
    file_to_delete = UploadedFile.objects.get(id=file_id)
    file_to_delete.delete()
    return redirect("applicants_view")


def view_pdf(request, file_id):
    file_to_print = get_object_or_404(UploadedFile, id=file_id)
    file_path = file_to_print.pdf_file.path
    file_name = file_to_print.pdf_file.name.split("/")[-1]

    with open(file_path, "rb") as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type="application/pdf")

    # Use quote function to ensure proper encoding of the filename
    response["Content-Disposition"] = f'inline; filename="{quote(file_name)}"'
    return response


# admin side resume and job uploading and skill extraction form it
def upload_file_admin(request):
    if request.method == "POST" and "pdf_file" in request.FILES:
        print("HELOOOOOOOOOOOOOOOOOOOOOOOOOO")
        pdf_file = request.FILES["pdf_file"]
        job_id = request.POST.get("job_id")
        text = extract_text_from_pdf(pdf_file)
        skills = list(skill_extraction(text))
        context = {"job_title": job_id, "skills": skills}
        return JsonResponse(
            {"message": "skills extracted successfully.", "context": context}
        )

    return redirect("upload_file")  # Redirect to the appropriate view


from django.contrib import messages
from django.http import JsonResponse

#power BI Dashboard 
def dashboard(request):
    return render(request, "dashboard.html")


def upload_skill_HR(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            skills = data.get("skills", [])
            job_id = data.get("job_id")
            print(skills, job_id)
            # Now you have 'skills' as a list and 'job_id' as a value

            # Perform further processing with skills and job_id
            # For example, save them to a database or perform other operations

            if skills:
                for skill_name in skills:
                    skill, created = Resume.objects.get_or_create(
                        skills=skill_name, title=job_id
                    )
                    if created:
                        # Skill was created, you can perform additional actions if needed
                        pass
                messages.success(
                    request, f"Skills extracted and saved for job: {job_id}"
                )
                return JsonResponse(
                    {"messages": "skills added to database", "status": True}
                )
            else:
                messages.warning(request, "No skills extracted from the PDF.")
                return JsonResponse({"messages": "No skills extracted from the PDF."})
        except json.JSONDecodeError:
            messages.error(request, "Invalid JSON data")
            return JsonResponse({"message": "Invalid JSON data"})


def job_selection(request):
    jobs = Job.objects.all()
    context = {"jobs": jobs}
    return render(request, "test.html", context)


# extract text from pd
def extract_text_from_pdf(pdf_file):
    def pdf_reader(file):
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(
            resource_manager, fake_file_handle, laparams=LAParams()
        )
        page_interpreter = PDFPageInterpreter(resource_manager, converter)
        for page in PDFPage.get_pages(file, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()

        # close open handles
        converter.close()
        fake_file_handle.close()

        return text

    # Extract text from PDF
    extracted_text = pdf_reader(pdf_file)

    # Tokenize the text into words
    nltk.download("punkt")
    words = nltk.word_tokenize(extracted_text)

    # Remove punctuation and convert to lowercase
    table = str.maketrans("", "", string.punctuation)
    words = [word.translate(table).lower() for word in words if word.isalpha()]
    text_string = " ".join(words)

    return text_string


# extract skills from text
def skill_extraction(text):
    def extract_skill_annotations(annotation):
        full_matches = annotation["results"]["full_matches"]
        ngram_scored = annotation["results"]["ngram_scored"]

        skill_annotations = set()
        for match in full_matches:
            skill_annotations.add(match["doc_node_value"])

        for scored in ngram_scored:
            skill_annotations.add(scored["doc_node_value"])

        return skill_annotations

    nlp = en_core_web_lg.load()
    # init skill extractor
    skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
    skills = extract_skill_annotations(skill_extractor.annotate(text))
    return skills


# score checking function
def score_check(job_skills, applicant_skills):
    job_skills.sort()
    applicant_skills.sort()
    job = " ".join(job_skills)
    applicant = " ".join(applicant_skills)
    score = fuzz.token_set_ratio(job, applicant)
    return score
