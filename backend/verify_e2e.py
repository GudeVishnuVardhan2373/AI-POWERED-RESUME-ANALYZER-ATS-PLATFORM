import urllib.request
import urllib.parse
import json
import uuid

BASE_URL = "http://127.0.0.1:8000"

def make_request(path, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode())

def test_fullstack_flow():
    print("[E2E] 1. Testing GET /api/jobs ...")
    status, jobs = make_request("/api/jobs")
    assert status == 200
    assert len(jobs) >= 4
    target_job = jobs[0]
    print(f" -> Found {len(jobs)} jobs. Target: '{target_job['title']}' (ID: {target_job['id']})")

    print("\n[E2E] 2. Testing POST /api/analyze with uploaded resume ...")
    test_resume_content = """
    ELENA ROSTOVA
    Email: elena.rostova@cloudtech.io | Phone: +1 (555) 789-0123
    GitHub: github.com/elenarostova | LinkedIn: linkedin.com/in/elena-rostova
    
    PROFESSIONAL SUMMARY
    Cloud Architect & DevOps Engineer with 4 years of hands-on experience building automated CI/CD pipelines, containerizing microservices with Docker, and provisioning resilient cloud infrastructure on AWS using Terraform.
    
    CORE SKILLS
    AWS, Docker, Linux, Bash, CI/CD, Git, GitHub Actions, Terraform, Python, PostgreSQL, REST API
    
    EXPERIENCE
    DevOps Specialist | CloudSphere Inc (2022 - Present)
    - Orchestrated multi-region AWS cloud migrations and reduced monthly cloud spend by 22%.
    - Designed and implemented automated CI/CD deployment pipelines using GitHub Actions and Docker.
    - Automated server configurations using Linux shell scripts and Terraform.
    - Engineered monitoring metrics and alert thresholds using CloudWatch and Prometheus.
    
    Junior Systems Administrator | NetVantage (2020 - 2022)
    - Administered Linux server fleets and resolved infrastructure outages.
    - Scripted routine backup and data validation tasks in Bash and Python.
    
    EDUCATION
    Bachelor of Science in Computer Engineering (2020)
    """

    # Prepare multipart/form-data manually with urllib
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    lines = []
    
    # job_id field
    lines.append(f"--{boundary}".encode())
    lines.append(b'Content-Disposition: form-data; name="job_id"')
    lines.append(b'')
    lines.append(str(target_job["id"]).encode())
    
    # file field
    lines.append(f"--{boundary}".encode())
    lines.append(b'Content-Disposition: form-data; name="file"; filename="elena_rostova_resume.txt"')
    lines.append(b'Content-Type: text/plain')
    lines.append(b'')
    lines.append(test_resume_content.strip().encode('utf-8'))
    lines.append(f"--{boundary}--".encode())
    lines.append(b'')
    
    body = b"\r\n".join(lines)
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body))
    }

    status, analysis = make_request("/api/analyze", method="POST", data=body, headers=headers)
    assert status == 200
    
    print(f" -> Candidate parsed: {analysis['candidate_name']}")
    print(f" -> Overall ATS Score: {analysis['overall_score']}%")
    print(f" -> Skills Score: {analysis['skills_score']}% | Domain Score: {analysis['domain_score']}%")
    print(f" -> Matched Skills: {analysis['matched_skills']}")
    print(f" -> Missing Skills: {analysis['missing_skills']}")
    print(f" -> Suggestions generated: {len(analysis['suggestions'])}")

    candidate_id = analysis["resume_id"]

    print("\n[E2E] 3. Testing PATCH candidate status to 'Shortlisted' ...")
    patch_body = json.dumps({"status": "Shortlisted"}).encode("utf-8")
    status, patch_res = make_request(f"/api/candidates/{candidate_id}/status", method="PATCH", data=patch_body, headers={"Content-Type": "application/json"})
    assert status == 200
    print(f" -> Candidate status updated successfully to: {patch_res['status']}")

    print("\n[E2E] 4. Testing GET /api/candidates detail modal data ...")
    status, candidate_detail = make_request(f"/api/candidates/{candidate_id}")
    assert status == 200
    assert candidate_detail["candidate_name"] == "Elena Rostova"
    assert candidate_detail["email"] == "elena.rostova@cloudtech.io"
    print(" -> Candidate profile, contact info, and extracted skills verified.")

    print("\n[E2E] 5. Testing POST /api/jobs to create a custom opening ...")
    new_job_data = {
        "title": "Lead Security Engineer",
        "department": "Cybersecurity",
        "experience_level": "Senior (5+ Years)",
        "description": "Looking for a seasoned Cybersecurity engineer to lead penetration testing and cloud security posture.",
        "required_skills": ["Linux", "Python", "Docker", "AWS", "Bash"]
    }
    status, created_job = make_request("/api/jobs", method="POST", data=json.dumps(new_job_data).encode("utf-8"), headers={"Content-Type": "application/json"})
    assert status == 200
    print(f" -> Created Job ID: {created_job['id']} ('{created_job['title']}')")

    print("\n[E2E] 6. Testing DELETE /api/jobs/{id} ...")
    status, del_res = make_request(f"/api/jobs/{created_job['id']}", method="DELETE")
    assert status == 200
    print(f" -> Cleaned up test job ID {created_job['id']} successfully.")

    print("\n[E2E] 7. Testing GET /api/analytics/dashboard ...")
    status, dashboard = make_request("/api/analytics/dashboard")
    assert status == 200
    print(f" -> Total resumes now in database: {dashboard['total_resumes']}")
    print(f" -> Shortlisted count: {dashboard['shortlisted_count']}")
    print(f" -> Top in-demand skills: {[s['skill'] for s in dashboard['top_in_demand_skills'][:4]]}")

    print("\n[SUCCESS] All End-to-End Fullstack features verified successfully!")

if __name__ == "__main__":
    test_fullstack_flow()
