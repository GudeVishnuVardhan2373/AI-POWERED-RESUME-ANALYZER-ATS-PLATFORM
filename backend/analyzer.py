import re
import math
from typing import Dict, List, Any, Tuple, Set

# ----------------- Comprehensive Skill Taxonomy -----------------
SKILL_TAXONOMY = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "r", "dart", "scala", "shell", "bash",
        "powershell", "sql", "html", "css"
    ],
    "Frontend Frameworks & UI": [
        "react", "react.js", "reactjs", "next.js", "nextjs", "vue", "vue.js", "vuejs",
        "nuxt", "angular", "svelte", "tailwind css", "tailwindcss", "bootstrap",
        "redux", "html5", "css3", "sass", "less", "webpack", "vite", "graphql",
        "rest api", "websocket", "jquery", "material ui", "chakra ui"
    ],
    "Backend & APIs": [
        "node.js", "nodejs", "express", "express.js", "fastapi", "flask", "django",
        "spring boot", "spring", "asp.net", ".net", "ruby on rails", "nestjs",
        "laravel", "gin", "microservices", "restful api", "grpc", "soap", "apollo"
    ],
    "Databases & Caching": [
        "postgresql", "postgres", "mysql", "mongodb", "redis", "sqlite", "cassandra",
        "elasticsearch", "dynamodb", "oracle", "mariadb", "neo4j", "firebase",
        "supabase", "prisma", "sqlalchemy", "hibernate"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "google cloud", "gcp", "docker",
        "kubernetes", "k8s", "terraform", "ci/cd", "github actions", "gitlab ci",
        "jenkins", "ansible", "helm", "linux", "nginx", "apache", "serverless",
        "cloudformation", "prometheus", "grafana"
    ],
    "AI, ML & Data Science": [
        "machine learning", "deep learning", "generative ai", "genai", "llm", "llms",
        "nlp", "natural language processing", "computer vision", "pytorch",
        "tensorflow", "keras", "scikit-learn", "sklearn", "pandas", "numpy",
        "scipy", "hugging face", "langchain", "llamaindex", "rag", "opencv",
        "prompt engineering", "data science", "data analysis", "tableau", "power bi"
    ],
    "Tools & Methodologies": [
        "git", "github", "gitlab", "jira", "agile", "scrum", "kanban", "unit testing",
        "pytest", "jest", "cypress", "selenium", "docker compose", "postman",
        "swagger", "openapi", "tdd", "ci/cd pipelines"
    ],
    "Soft Skills": [
        "communication", "leadership", "problem solving", "critical thinking",
        "team collaboration", "collaboration", "time management", "adaptability",
        "mentorship", "project management", "conflict resolution", "creativity"
    ]
}

# Inverted mapping for quick lookup
SKILL_TO_CATEGORY = {}
for cat, skills in SKILL_TAXONOMY.items():
    for skill in skills:
        SKILL_TO_CATEGORY[skill.lower()] = cat

# Course / Resource recommendations for top tech skills
SKILL_LEARNING_RESOURCES = {
    "docker": {"course": "Docker Mastery on Udemy / Official Docker Docs", "priority": "High"},
    "kubernetes": {"course": "Kubernetes for Developers (CKAD) on Linux Foundation", "priority": "High"},
    "aws": {"course": "AWS Certified Solutions Architect on Coursera / AWS Skill Builder", "priority": "High"},
    "azure": {"course": "Microsoft Azure Fundamentals (AZ-900) on MS Learn", "priority": "Medium"},
    "react": {"course": "The Complete React Guide by Academind / react.dev", "priority": "High"},
    "fastapi": {"course": "FastAPI Full Course & Official Documentation", "priority": "High"},
    "python": {"course": "Python for Everybody (University of Michigan / Coursera)", "priority": "High"},
    "sql": {"course": "SQL for Data Science (Coursera) / LeetCode Database Practice", "priority": "High"},
    "graphql": {"course": "GraphQL with Apollo & React / Odyssey by Apollo", "priority": "Medium"},
    "typescript": {"course": "Understanding TypeScript on Udemy / typescriptlang.org", "priority": "High"},
    "mongodb": {"course": "MongoDB for Python Developers on MongoDB University", "priority": "Medium"},
    "postgresql": {"course": "PostgreSQL Bootcamp & Relational Database Design", "priority": "High"},
    "ci/cd": {"course": "CI/CD with GitHub Actions on GitHub Skills", "priority": "High"},
    "generative ai": {"course": "Generative AI Fundamentals (DeepLearning.AI)", "priority": "High"},
    "prompt engineering": {"course": "ChatGPT Prompt Engineering for Developers (DeepLearning.AI)", "priority": "High"},
    "rag": {"course": "Building Systems with ChatGPT & Vector DBs (DeepLearning.AI)", "priority": "High"},
    "langchain": {"course": "LangChain for LLM Application Development", "priority": "High"},
    "machine learning": {"course": "Machine Learning Specialization by Andrew Ng (Coursera)", "priority": "High"},
    "deep learning": {"course": "Deep Learning Specialization (DeepLearning.AI)", "priority": "High"},
    "terraform": {"course": "HashiCorp Certified Terraform Associate on Udemy", "priority": "Medium"},
    "redis": {"course": "Redis for Developers on Redis University", "priority": "Medium"},
    "linux": {"course": "Linux Basics for SysAdmins on edX", "priority": "Medium"},
    "git": {"course": "Version Control with Git by Atlassian", "priority": "High"},
}

ACTION_VERBS = [
    "developed", "engineered", "built", "designed", "implemented", "deployed",
    "spearheaded", "architected", "optimized", "orchestrated", "collaborated",
    "created", "automated", "managed", "led", "enhanced", "resolved", "delivered"
]

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its",
    "itself", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "should", "shouldn't",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through",
    "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "were",
    "weren't", "what", "when", "where", "which", "while", "who", "whom", "why",
    "with", "won't", "would", "wouldn't", "you", "your", "yours", "yourself", "yourselves"
}

def clean_text_tokens(text: str) -> List[str]:
    """Tokenize and filter stop words and punctuation."""
    tokens = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def compute_tf_idf_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity between two text documents using pure Python TF-IDF."""
    tokens1 = clean_text_tokens(text1)
    tokens2 = clean_text_tokens(text2)
    
    if not tokens1 or not tokens2:
        return 0.0

    # Vocabulary
    vocab = set(tokens1).union(set(tokens2))
    if not vocab:
        return 0.0

    freq1 = {}
    for t in tokens1:
        freq1[t] = freq1.get(t, 0) + 1
        
    freq2 = {}
    for t in tokens2:
        freq2[t] = freq2.get(t, 0) + 1

    dot_product = 0.0
    norm1 = 0.0
    norm2 = 0.0

    for w in vocab:
        df = (1 if w in freq1 else 0) + (1 if w in freq2 else 0)
        # Shared terms across both documents are weighted higher for matching
        idf = 1.5 if df == 2 else 1.0

        v1 = freq1.get(w, 0) * idf
        v2 = freq2.get(w, 0) * idf

        dot_product += v1 * v2
        norm1 += v1 * v1
        norm2 += v2 * v2

    if norm1 == 0 or norm2 == 0:
        return 0.0

    raw_similarity = dot_product / (math.sqrt(norm1) * math.sqrt(norm2))
    return min(max(raw_similarity, 0.0), 1.0)


def extract_skills(text: str) -> Dict[str, List[str]]:
    """Scan text against the 500+ skill taxonomy and categorize matches."""
    text_lower = " " + text.lower() + " "
    found_skills: Dict[str, List[str]] = {
        "Programming Languages": [],
        "Frontend Frameworks & UI": [],
        "Backend & APIs": [],
        "Databases & Caching": [],
        "Cloud & DevOps": [],
        "AI, ML & Data Science": [],
        "Tools & Methodologies": [],
        "Soft Skills": []
    }

    # First handle special single/symbol characters carefully
    special_cases = {
        r'\bc\+\+\b': ("c++", "Programming Languages"),
        r'\bc\#\b': ("c#", "Programming Languages"),
        r'\b\.net\b': (".net", "Backend & APIs"),
        r'\br\b': ("r", "Programming Languages"),
        r'\bc\b': ("c", "Programming Languages"),
        r'\bgo\b': ("go", "Programming Languages")
    }
    
    for pattern, (skill_name, category) in special_cases.items():
        if re.search(pattern, text_lower):
            if skill_name.upper() not in found_skills[category]:
                found_skills[category].append(skill_name.upper() if len(skill_name) <= 3 else skill_name.title())

    for category, skill_list in SKILL_TAXONOMY.items():
        for skill in skill_list:
            if skill in ["c", "c++", "c#", "r", "go", ".net"]:
                continue  # Handled in special cases
            
            # Escape regex characters
            escaped = re.escape(skill)
            pattern = rf'(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])'
            
            if re.search(pattern, text_lower):
                display_name = skill.upper() if len(skill) <= 4 and skill not in ["java", "ruby", "rust", "node", "html", "css"] else skill.title()
                if display_name not in found_skills[category]:
                    found_skills[category].append(display_name)

    # Clean up empty categories
    return {k: sorted(v) for k, v in found_skills.items() if v}


def evaluate_ats_readability(text: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    """Audit ATS standards: contact info, section structure, word count, action verbs."""
    word_count = len(text.split())
    has_email = profile.get("email") is not None
    has_phone = profile.get("phone") is not None
    has_links = len(profile.get("links", [])) > 0
    has_education = len(profile.get("education", [])) > 0
    experience_years = profile.get("experience_years", 0) > 0

    # Count action verbs
    text_lower = text.lower()
    found_verbs = [v for v in ACTION_VERBS if re.search(rf'\b{v}\b', text_lower)]
    action_verb_score = min(len(found_verbs) * 15, 100)

    # Word count evaluation (400-1200 is optimal for ATS 1-2 page resumes)
    if 400 <= word_count <= 1200:
        word_count_grade = "Optimal (400 - 1200 words)"
        wc_score = 100
    elif word_count < 400:
        word_count_grade = "Too Brief (< 400 words)"
        wc_score = 65
    else:
        word_count_grade = "Too Long (> 1200 words)"
        wc_score = 80

    checks = [
        {"passed": has_email, "label": "Professional Email", "tip": "Candidate email detected." if has_email else "Missing email address."},
        {"passed": has_phone, "label": "Contact Phone Number", "tip": "Phone number detected." if has_phone else "Missing phone contact number."},
        {"passed": has_links, "label": "LinkedIn / GitHub Links", "tip": "Professional profiles linked." if has_links else "Include GitHub or LinkedIn profile links."},
        {"passed": has_education, "label": "Standard Degree / Education", "tip": "Recognized degree credentials found." if has_education else "Explicit degree or university info not detected."},
        {"passed": len(found_verbs) >= 4, "label": "Strong Action Verbs", "tip": f"Used {len(found_verbs)} impactful action verbs." if len(found_verbs) >= 4 else "Incorporate more action verbs like 'Engineered', 'Optimized', 'Architected'."}
    ]

    passed_count = sum(1 for c in checks if c["passed"])
    total_checks = len(checks)
    score = round((passed_count / total_checks) * 70 + (wc_score * 0.15) + (action_verb_score * 0.15), 1)

    return {
        "score": min(score, 100.0),
        "word_count": word_count,
        "word_count_grade": word_count_grade,
        "action_verbs_found": found_verbs,
        "checks": checks
    }


def analyze_resume_against_job(resume_text: str, job_description: str, job_required_skills: List[str] = None) -> Dict[str, Any]:
    """Full analysis pipeline: extract skills, match job requirements, compute scores and suggestions."""
    # 1. Extract candidate skills
    extracted_candidate_skills_dict = extract_skills(resume_text)
    candidate_all_skills_lower = set()
    for cat, skills in extracted_candidate_skills_dict.items():
        for s in skills:
            candidate_all_skills_lower.add(s.lower())

    # 2. Extract job skills
    job_extracted_skills_dict = extract_skills(job_description)
    job_all_skills_lower = set()
    for cat, skills in job_extracted_skills_dict.items():
        for s in skills:
            job_all_skills_lower.add(s.lower())

    # Add explicitly specified required skills if provided
    if job_required_skills:
        for s in job_required_skills:
            job_all_skills_lower.add(s.strip().lower())

    # 3. Compute Matched and Missing Skills
    matched_skills_lower = candidate_all_skills_lower.intersection(job_all_skills_lower)
    missing_skills_lower = job_all_skills_lower.difference(candidate_all_skills_lower)

    # Format into Title case / clean display
    matched_skills = sorted([s.upper() if len(s) <= 4 and s not in ["java", "ruby", "rust"] else s.title() for s in matched_skills_lower])
    missing_skills = sorted([s.upper() if len(s) <= 4 and s not in ["java", "ruby", "rust"] else s.title() for s in missing_skills_lower])

    # 4. Scores Calculation
    # A. Skills Score (0 - 100)
    if job_all_skills_lower:
        skills_score = round((len(matched_skills_lower) / len(job_all_skills_lower)) * 100, 1)
    else:
        skills_score = 80.0  # Default if no specific skills in job desc

    # B. Domain / Semantic Similarity via TF-IDF (0 - 100)
    tfidf_sim = compute_tf_idf_similarity(resume_text, job_description)
    domain_score = round(min(tfidf_sim * 130.0, 100.0), 1)

    # C. ATS & Profile audit
    from .parser import parse_candidate_profile
    profile = parse_candidate_profile(resume_text, "resume.txt")
    ats_audit = evaluate_ats_readability(resume_text, profile)
    ats_score = ats_audit["score"]

    # D. Experience Score
    exp_years = profile.get("experience_years", 0.0)
    if exp_years >= 5:
        experience_score = 95.0
    elif exp_years >= 2:
        experience_score = 85.0
    elif exp_years >= 1:
        experience_score = 75.0
    else:
        experience_score = 65.0

    # Overall Weighted Score
    # 40% skills, 20% domain similarity, 20% ATS formatting, 20% experience
    overall_score = round(
        (skills_score * 0.40) +
        (domain_score * 0.20) +
        (ats_score * 0.20) +
        (experience_score * 0.20),
        1
    )
    overall_score = min(max(overall_score, 10.0), 99.0)

    # 5. Generate Missing-Skill Suggestions & Actionable Advice
    suggestions = []
    for miss in missing_skills[:6]:
        key = miss.lower()
        res = SKILL_LEARNING_RESOURCES.get(key, {
            "course": f"Explore hands-on project tutorials and documentation for {miss}",
            "priority": "Medium"
        })
        suggestions.append({
            "skill": miss,
            "priority": res["priority"],
            "learning_path": res["course"],
            "tip": f"Add a project bullet demonstrating practical use of {miss} or highlight related coursework."
        })

    return {
        "overall_score": overall_score,
        "skills_score": skills_score,
        "experience_score": experience_score,
        "ats_score": ats_score,
        "domain_score": domain_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
        "ats_details": ats_audit,
        "candidate_skills_by_category": extracted_candidate_skills_dict,
        "candidate_profile": profile
    }
