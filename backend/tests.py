import unittest
import os
from .analyzer import extract_skills, compute_tf_idf_similarity, evaluate_ats_readability, analyze_resume_against_job
from .parser import parse_candidate_profile

class TestResumeAnalyzer(unittest.TestCase):
    def test_skill_extraction(self):
        sample_text = "Experienced with Python, FastAPI, Docker, PostgreSQL, React.js, and Machine Learning."
        skills = extract_skills(sample_text)
        
        flat_skills = []
        for cat, sks in skills.items():
            flat_skills.extend([s.lower() for s in sks])
            
        self.assertIn("python", flat_skills)
        self.assertIn("fastapi", flat_skills)
        self.assertIn("docker", flat_skills)
        self.assertIn("postgresql", flat_skills)
        self.assertIn("react", flat_skills)

    def test_tf_idf_similarity(self):
        text_a = "Senior Software Engineer building Python FastAPI microservices and Docker containers."
        text_b = "We need a Python developer who knows FastAPI, Docker, and backend services."
        sim = compute_tf_idf_similarity(text_a, text_b)
        self.assertGreater(sim, 0.3, f"Expected similarity > 0.3, got {sim}")

    def test_candidate_profile_parsing(self):
        resume_content = """
        SARAH CONNOR
        Email: sarah.connor@sky.net
        Phone: +1 555-492-1234
        GitHub: github.com/sarahconnor
        
        Over 4 years of experience building modern web applications.
        Education: Bachelor of Science in Computer Science
        """
        profile = parse_candidate_profile(resume_content, "sarah_resume.pdf")
        self.assertEqual(profile["candidate_name"], "Sarah Connor")
        self.assertEqual(profile["email"], "sarah.connor@sky.net")
        self.assertIn("github.com/sarahconnor", profile["links"])
        self.assertGreaterEqual(profile["experience_years"], 4.0)

    def test_full_analysis_pipeline(self):
        resume = """
        John Doe
        john@example.com | 123-456-7890
        github.com/johndoe
        
        Software developer with 3 years of experience.
        Skills: Python, FastAPI, React, SQL, Git, Linux
        Engineered, developed, and deployed modern cloud services.
        Bachelor of Technology in Information Technology.
        """
        job = """
        Looking for a Fullstack Developer proficient in Python, FastAPI, React, Docker, and Kubernetes.
        """
        analysis = analyze_resume_against_job(resume, job, ["Docker", "Kubernetes", "Python", "FastAPI", "React"])
        
        self.assertGreater(analysis["overall_score"], 40.0)
        self.assertIn("PYTHON", [s.upper() for s in analysis["matched_skills"]])
        self.assertIn("DOCKER", [s.upper() for s in analysis["missing_skills"]])
        self.assertTrue(len(analysis["suggestions"]) > 0)

if __name__ == "__main__":
    unittest.main()
