from django.shortcuts import render, redirect
import PyPDF2, docx, re
from .skills_data import JOB_SKILLS
from .models import Candidate
import pandas as pd
from datetime import datetime
from django.http import FileResponse

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text.lower()

def extract_text_from_docx(docx_file):
    d = docx.Document(docx_file)
    text = "\n".join([p.text for p in d.paragraphs])
    return text.lower()

def upload_resume(request):
    result = None

    if request.method == "POST":
        role = request.POST.get("job_role")
        file = request.FILES["resume_file"]

        # ---- Extract resume text ----
        if file.name.endswith(".pdf"):
            text = extract_text_from_pdf(file)
        else:
            text = extract_text_from_docx(file)

        text_original = text

        # Regex Info Extraction
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}", text)
        email = email_match.group(0) if email_match else None

        phone_match = re.search(r"\b\d{10}\b", text)
        phone = phone_match.group(0) if phone_match else None

        name = None
        if email:
            name = text_original.split(email)[0].strip().split("\n")[0][:30]

        linkedin_match = re.search(r"(https?://)?(www\.)?linkedin\.com/[^\s]+", text)
        linkedin = linkedin_match.group(0) if linkedin_match else None

        cgpa_match = re.search(r"(\d\.\d)\s*cgpa", text)
        cgpa = cgpa_match.group(1) if cgpa_match else None

        college = None
        for line in text_original.split("\n"):
            if "college" in line.lower() or "university" in line.lower():
                college = line.strip()
                break

        exp_match = re.search(r"(\d+)\s+(year|years|month|months)", text)
        experience = exp_match.group(0) if exp_match else None

        matched = []
        missing = []
        required_skills = JOB_SKILLS.get(role, [])
        for skill in required_skills:
            if skill.lower() in text:
                matched.append(skill)
            else:
                missing.append(skill)

        score = round((len(matched) / len(required_skills)) * 100, 2)

        # ---- Save into database ----
        candidate = Candidate.objects.create(
            name=name,
            email=email,
            phone=phone,
            linkedin=linkedin,
            college=college,
            cgpa=cgpa,
            experience=experience,
            role=role,
            score=score,
            matched_skills=",".join(matched),
            missing_skills=",".join(missing),
        )

        # 🔥 Save resume file inside model for download
        candidate.resume_file = file
        candidate.save()

        # ---- Export CSV for Power BI ----
        df = pd.DataFrame([{
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "college": college,
            "cgpa": cgpa,
            "experience": experience,
            "role": role,
            "score": score,
            "matched": ",".join(matched),
            "missing": ",".join(missing),
            "uploaded_at": datetime.now()
        }])
        df.to_csv("C:/Users/Avinash/Desktop/ats_data.csv", mode="a", header=False, index=False)

        result = {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "college": college,
            "cgpa": cgpa,
            "experience": experience,
            "role": role,
            "score": score,
            "matched": matched,
            "missing": missing,
        }

    return render(request, "upload.html", {"result": result})


# ---- HR Dashboard ----
def hr_dashboard(request):
    data = Candidate.objects.all().order_by('-score')
    return render(request, "dashboard.html", {"candidates": data})

# ---- DOWNLOAD RESUME FILE ----
def download_resume(request, candidate_id):
    c = Candidate.objects.get(id=candidate_id)
    return FileResponse(c.resume_file.open("rb"), as_attachment=True, filename=c.resume_file.name)
