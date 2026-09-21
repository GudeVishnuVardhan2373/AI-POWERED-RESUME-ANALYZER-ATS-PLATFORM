// ResuMatch AI Frontend Application Logic

let selectedFile = null;
let activeJobs = [];
let debounceTimer = null;
let chartScoreDist = null;
let chartSkillsDemand = null;

// Sample resumes for instant demo testing
const SAMPLE_RESUMES = {
  fullstack: {
    filename: "Alex_Morgan_Fullstack_Engineer.txt",
    content: `ALEXANDER MORGAN
Email: alex.morgan.dev@example.com | Phone: +1 (555) 234-5678
LinkedIn: linkedin.com/in/alexmorgan-dev | GitHub: github.com/alexmorgan-code
San Francisco, CA

PROFESSIONAL SUMMARY
Dynamic and results-driven Software Engineer with 3+ years of experience in designing, building, and deploying scalable web applications and REST APIs. Proficient in Python, FastAPI, React, JavaScript, and relational databases. Adept at agile collaboration and automated testing.

TECHNICAL SKILLS
- Programming Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3
- Frameworks & Libraries: FastAPI, Flask, React.js, Tailwind CSS, Redux
- Databases: PostgreSQL, SQLite, Redis
- DevOps & Tools: Docker, Git, GitHub Actions, Linux, Postman, Jest, PyTest

PROFESSIONAL EXPERIENCE
Software Engineer | NexaTech Solutions (2022 - Present)
- Architected and engineered high-throughput REST APIs using Python and FastAPI, serving over 150,000 active users.
- Built responsive single-page web applications with React and Tailwind CSS, reducing load times by 35%.
- Optimized complex PostgreSQL database queries and implemented Redis caching, boosting query performance by 40%.
- Automated CI/CD build and testing pipelines using GitHub Actions and Docker containerization.
- Collaborated with cross-functional teams in daily Agile Scrum meetings to deliver features on sprint schedules.

EDUCATION
Bachelor of Technology (B.Tech) in Computer Science & Engineering
Apex University (Graduated 2021)`
  },
  junior: {
    filename: "David_Chen_Junior_Developer.txt",
    content: `DAVID CHEN
Email: david.chen99@email.com | Phone: +1 (555) 987-6543
GitHub: github.com/davidchen-code
Austin, TX

OBJECTIVE
Passionate junior front-end developer looking to contribute to exciting software products.

SKILLS
- HTML5, CSS3, JavaScript, jQuery, Git, Bootstrap
- Learning React and Node.js

EXPERIENCE
Frontend Intern | WebCraft Agency (2023 - 2024)
- Developed responsive marketing landing pages using HTML5 and CSS3.
- Assisted senior engineers with bug fixes in JavaScript codebase.
- Participated in weekly team sprint retrospectives.

EDUCATION
Associate Degree in Web Development (Graduated 2023)`
  }
};

// Initialize app on DOM Load
document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  setupDropZone();
  fetchJobPostings();
  fetchCandidatesList();
  fetchDashboardKPIs();
});

// ---------------- Navigation ----------------
function switchTab(tabName) {
  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.classList.remove("active-tab");
    tab.classList.add("text-slate-400");
  });
  const activeBtn = document.getElementById(`nav-${tabName}`);
  if (activeBtn) {
    activeBtn.classList.add("active-tab");
    activeBtn.classList.remove("text-slate-400");
  }

  document.querySelectorAll(".tab-content").forEach(content => {
    content.classList.add("hidden");
  });
  const activeContent = document.getElementById(`tab-${tabName}`);
  if (activeContent) {
    activeContent.classList.remove("hidden");
  }

  if (window.lucide) lucide.createIcons();

  if (tabName === "dashboard") {
    fetchCandidatesList();
    fetchDashboardKPIs();
  } else if (tabName === "jobs") {
    fetchJobPostings();
  } else if (tabName === "analytics") {
    renderAnalyticsCharts();
  }
}

// ---------------- Drop Zone & File Management ----------------
function setupDropZone() {
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("resume-file");

  dropZone.addEventListener("click", () => fileInput.click());

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });
}

function handleFileSelected(file) {
  selectedFile = file;
  document.getElementById("drop-zone-idle").classList.add("hidden");
  const selectedEl = document.getElementById("drop-zone-selected");
  selectedEl.classList.remove("hidden");
  document.getElementById("selected-file-name").textContent = file.name;
  document.getElementById("selected-file-size").textContent = `${(file.size / 1024).toFixed(1)} KB`;
  if (window.lucide) lucide.createIcons();
}

function clearSelectedFile(e) {
  if (e) e.stopPropagation();
  selectedFile = null;
  document.getElementById("resume-file").value = "";
  document.getElementById("drop-zone-selected").classList.add("hidden");
  document.getElementById("drop-zone-idle").classList.remove("hidden");
}

function loadSampleResume(type) {
  const sample = SAMPLE_RESUMES[type];
  if (!sample) return;

  const blob = new Blob([sample.content], { type: "text/plain" });
  const file = new File([blob], sample.filename, { type: "text/plain" });
  handleFileSelected(file);
  showToast(`Loaded sample resume: ${sample.filename}`);
}

// ---------------- Job Descriptions & Selection ----------------
function toggleJobMode(mode) {
  const savedBtn = document.getElementById("mode-saved-btn");
  const customBtn = document.getElementById("mode-custom-btn");
  const savedSec = document.getElementById("job-mode-saved");
  const customSec = document.getElementById("job-mode-custom");

  if (mode === "saved") {
    savedBtn.classList.add("bg-indigo-600", "text-white");
    savedBtn.classList.remove("text-slate-400");
    customBtn.classList.remove("bg-indigo-600", "text-white");
    customBtn.classList.add("text-slate-400");
    savedSec.classList.remove("hidden");
    customSec.classList.add("hidden");
  } else {
    customBtn.classList.add("bg-indigo-600", "text-white");
    customBtn.classList.remove("text-slate-400");
    savedBtn.classList.remove("bg-indigo-600", "text-white");
    savedBtn.classList.add("text-slate-400");
    customSec.classList.remove("hidden");
    savedSec.classList.add("hidden");
  }
}

async function fetchJobPostings() {
  try {
    const res = await fetch("/api/jobs");
    activeJobs = await res.json();
    populateJobSelector();
    renderJobCards();
  } catch (err) {
    console.error("Failed to fetch jobs:", err);
  }
}

function populateJobSelector() {
  const selector = document.getElementById("job-selector");
  if (!selector) return;

  selector.innerHTML = "";
  if (activeJobs.length === 0) {
    selector.innerHTML = `<option value="">No job openings available</option>`;
    return;
  }

  activeJobs.forEach((job, idx) => {
    const opt = document.createElement("option");
    opt.value = job.id;
    opt.textContent = `${job.title} (${job.department})`;
    if (idx === 0) opt.selected = true;
    selector.appendChild(opt);
  });

  selector.onchange = () => updateJobPreview(selector.value);
  if (activeJobs[0]) {
    updateJobPreview(activeJobs[0].id);
  }
}

function updateJobPreview(jobId) {
  const job = activeJobs.find(j => j.id == jobId);
  if (!job) return;

  document.getElementById("preview-job-department").textContent = job.department;
  document.getElementById("preview-job-exp").textContent = job.experience_level;
  document.getElementById("preview-job-desc").textContent = job.description;

  const skillsContainer = document.getElementById("preview-job-skills");
  skillsContainer.innerHTML = (job.required_skills || []).map(s => 
    `<span class="px-2 py-0.5 rounded bg-indigo-950/60 border border-indigo-800/40 text-[11px] text-indigo-300 font-medium">${s}</span>`
  ).join("");
}

function renderJobCards() {
  const container = document.getElementById("job-cards-grid");
  if (!container) return;

  if (activeJobs.length === 0) {
    container.innerHTML = `<div class="col-span-3 text-center py-12 text-slate-500">No active job openings created yet.</div>`;
    return;
  }

  container.innerHTML = activeJobs.map(job => `
    <div class="glass-card rounded-2xl p-6 border border-slate-800/80 bg-slate-900/60 flex flex-col justify-between space-y-4">
      <div class="space-y-2">
        <div class="flex items-start justify-between">
          <div>
            <span class="text-xs px-2.5 py-0.5 rounded-full bg-indigo-950/70 border border-indigo-800/50 text-indigo-300 font-medium">${job.department}</span>
            <h3 class="font-display text-lg font-bold text-white mt-1.5">${job.title}</h3>
          </div>
          <span class="text-xs px-2 py-1 rounded bg-slate-800 text-slate-400 font-mono">${job.experience_level}</span>
        </div>
        <p class="text-xs text-slate-400 line-clamp-3 leading-relaxed">${job.description}</p>
      </div>

      <div class="space-y-3 pt-2 border-t border-slate-800">
        <div>
          <p class="text-[11px] text-slate-500 font-medium mb-1.5 uppercase tracking-wider">Required Skills</p>
          <div class="flex flex-wrap gap-1">
            ${(job.required_skills || []).slice(0, 6).map(sk => `
              <span class="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">${sk}</span>
            `).join("")}
          </div>
        </div>

        <div class="flex items-center justify-between pt-2">
          <div class="flex items-center space-x-1.5 text-xs text-indigo-400 font-medium">
            <i data-lucide="users" class="w-3.5 h-3.5"></i>
            <span>${job.applicant_count || 0} Candidates Evaluated</span>
          </div>
          <button onclick="deleteJob(${job.id})" class="text-xs text-slate-400 hover:text-rose-400 p-1.5 rounded-lg hover:bg-slate-800 transition-colors" title="Delete Job">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>
    </div>
  `).join("");

  if (window.lucide) lucide.createIcons();
}

// ---------------- Perform Resume Analysis ----------------
async function performAnalysis() {
  if (!selectedFile) {
    showToast("Please select or drop a resume file first!", "alert-circle");
    return;
  }

  const btn = document.getElementById("btn-analyze");
  const btnText = document.getElementById("btn-analyze-text");
  const isCustomMode = !document.getElementById("job-mode-custom").classList.contains("hidden");

  const formData = new FormData();
  formData.append("file", selectedFile);

  if (isCustomMode) {
    const customTitle = document.getElementById("custom-job-title").value;
    const customDesc = document.getElementById("custom-job-desc").value;
    if (!customDesc.trim()) {
      showToast("Please enter a custom job description!", "alert-circle");
      return;
    }
    formData.append("custom_job_title", customTitle);
    formData.append("custom_job_description", customDesc);
  } else {
    const selector = document.getElementById("job-selector");
    if (selector.value) {
      formData.append("job_id", selector.value);
    }
  }

  btn.disabled = true;
  btnText.textContent = "Analyzing Profile & Matching Skills...";

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Analysis failed");
    }

    const data = await res.json();
    displayAnalysisResults(data);
    showToast("Resume analyzed successfully!", "check-circle");
    fetchCandidatesList();
    fetchDashboardKPIs();
  } catch (err) {
    showToast(err.message, "alert-circle");
  } finally {
    btn.disabled = false;
    btnText.textContent = "Run AI Resume Analysis";
  }
}

function displayAnalysisResults(data) {
  const section = document.getElementById("analysis-results-section");
  section.classList.remove("hidden");

  // Candidate basics
  document.getElementById("res-candidate-name").textContent = data.candidate_name;
  document.getElementById("res-job-title").textContent = `Target Role: ${data.job_title}`;
  
  const initials = data.candidate_name.split(" ").map(w => w[0]).join("").substring(0, 2).toUpperCase() || "CN";
  document.getElementById("res-avatar-initials").textContent = initials;

  document.getElementById("res-email").textContent = data.email || "Email not specified";
  document.getElementById("res-phone").textContent = data.phone || "Phone not specified";
  document.getElementById("res-experience").textContent = `${data.experience_score >= 85 ? "Experienced" : "Early-career"} Profile`;

  // Links
  const linksContainer = document.getElementById("res-links");
  linksContainer.innerHTML = "";
  if (data.ats_details && data.ats_details.checks) {
    // Links display
  }

  // Circular score animation
  const overall = Math.round(data.overall_score);
  const scoreNumberEl = document.getElementById("res-overall-score");
  scoreNumberEl.textContent = overall;

  const circle = document.getElementById("score-circle-progress");
  const maxDash = 251.2;
  const offset = maxDash - (overall / 100) * maxDash;
  circle.style.strokeDashoffset = offset;

  // Score color grading
  const verdictBadge = document.getElementById("res-verdict-badge");
  const verdictDesc = document.getElementById("res-verdict-desc");

  if (overall >= 80) {
    circle.setAttribute("class", "stroke-current text-emerald-400 transition-all duration-1000 ease-out");
    verdictBadge.className = "inline-block px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/40";
    verdictBadge.textContent = "High Match (Recommended)";
    verdictDesc.textContent = "Candidate demonstrates strong alignment with core technical stack and experience expectations.";
  } else if (overall >= 60) {
    circle.setAttribute("class", "stroke-current text-amber-400 transition-all duration-1000 ease-out");
    verdictBadge.className = "inline-block px-3 py-1 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-400 border border-amber-800/40";
    verdictBadge.textContent = "Moderate Potential";
    verdictDesc.textContent = "Solid foundational skills. Candidate has some skill gaps that can be bridged with onboarding or upskilling.";
  } else {
    circle.setAttribute("class", "stroke-current text-rose-400 transition-all duration-1000 ease-out");
    verdictBadge.className = "inline-block px-3 py-1 rounded-full text-xs font-semibold bg-rose-950/80 text-rose-400 border border-rose-800/40";
    verdictBadge.textContent = "Low Alignment";
    verdictDesc.textContent = "Substantial technical gaps detected between applicant background and target job requirements.";
  }

  // Mini Breakdown meters
  document.getElementById("res-score-skills").textContent = `${Math.round(data.skills_score)}%`;
  document.getElementById("bar-skills").style.width = `${Math.round(data.skills_score)}%`;

  document.getElementById("res-score-exp").textContent = `${Math.round(data.experience_score)}%`;
  document.getElementById("bar-exp").style.width = `${Math.round(data.experience_score)}%`;

  document.getElementById("res-score-ats").textContent = `${Math.round(data.ats_score)}%`;
  document.getElementById("bar-ats").style.width = `${Math.round(data.ats_score)}%`;

  document.getElementById("res-score-domain").textContent = `${Math.round(data.domain_score)}%`;
  document.getElementById("bar-domain").style.width = `${Math.round(data.domain_score)}%`;

  // Matched Skills
  document.getElementById("count-matched").textContent = data.matched_skills.length;
  const matchedBox = document.getElementById("container-matched-skills");
  if (data.matched_skills.length === 0) {
    matchedBox.innerHTML = `<p class="text-xs text-slate-500 italic">No direct required skill matches detected.</p>`;
  } else {
    matchedBox.innerHTML = data.matched_skills.map(s => `
      <span class="inline-flex items-center space-x-1 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/40 text-xs font-medium text-emerald-300">
        <i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i>
        <span>${s}</span>
      </span>
    `).join("");
  }

  // Missing Skills
  document.getElementById("count-missing").textContent = data.missing_skills.length;
  const missingBox = document.getElementById("container-missing-skills");
  if (data.missing_skills.length === 0) {
    missingBox.innerHTML = `<p class="text-xs text-emerald-400 font-medium">Full skill coverage! No critical required skills missing.</p>`;
  } else {
    missingBox.innerHTML = data.missing_skills.map(s => `
      <span class="inline-flex items-center space-x-1 px-3 py-1 rounded-full bg-rose-950/60 border border-rose-800/40 text-xs font-medium text-rose-300">
        <i data-lucide="x" class="w-3.5 h-3.5 text-rose-400"></i>
        <span>${s}</span>
      </span>
    `).join("");
  }

  // Missing-Skill Suggestions & Learning Path
  const suggestionsBox = document.getElementById("container-suggestions");
  if (!data.suggestions || data.suggestions.length === 0) {
    suggestionsBox.innerHTML = `<p class="col-span-3 text-xs text-slate-400 py-3">No immediate skill suggestions needed.</p>`;
  } else {
    suggestionsBox.innerHTML = data.suggestions.map(sug => `
      <div class="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex flex-col justify-between space-y-3">
        <div>
          <div class="flex items-center justify-between mb-1.5">
            <span class="font-bold text-sm text-white">${sug.skill}</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full ${sug.priority === 'High' ? 'bg-rose-950 border border-rose-800 text-rose-300' : 'bg-amber-950 border border-amber-800 text-amber-300'} font-semibold uppercase">${sug.priority} Priority</span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed"><span class="text-indigo-400 font-medium">Recommended Course:</span> ${sug.learning_path}</p>
        </div>
        <p class="text-[11px] text-slate-400 bg-slate-900/90 p-2.5 rounded-lg border border-slate-800/80 italic">💡 "${sug.tip}"</p>
      </div>
    `).join("");
  }

  // ATS Checklist
  const atsBox = document.getElementById("container-ats-checks");
  if (data.ats_details && data.ats_details.checks) {
    document.getElementById("ats-word-badge").textContent = `${data.ats_details.word_count} words (${data.ats_details.word_count_grade})`;
    atsBox.innerHTML = data.ats_details.checks.map(chk => `
      <div class="p-3 rounded-xl bg-slate-950/50 border border-slate-800/80 flex items-start space-x-3">
        <div class="mt-0.5 w-5 h-5 rounded-full ${chk.passed ? 'bg-emerald-950 text-emerald-400 border border-emerald-700/50' : 'bg-rose-950 text-rose-400 border border-rose-700/50'} flex items-center justify-center flex-shrink-0">
          <i data-lucide="${chk.passed ? 'check' : 'x'}" class="w-3.5 h-3.5"></i>
        </div>
        <div>
          <p class="text-xs font-semibold text-white">${chk.label}</p>
          <p class="text-[11px] text-slate-400 mt-0.5 leading-tight">${chk.tip}</p>
        </div>
      </div>
    `).join("");
  }

  // Extracted Skills Categorized
  const allSkillsBox = document.getElementById("container-all-skills");
  allSkillsBox.innerHTML = "";
  // Fetch full details if needed
  fetchCandidateSkillsDetail(data.resume_id);

  if (window.lucide) lucide.createIcons();

  // Scroll smoothly down to results
  section.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function fetchCandidateSkillsDetail(candidateId) {
  try {
    const res = await fetch(`/api/candidates/${candidateId}`);
    const data = await res.json();
    const allSkillsBox = document.getElementById("container-all-skills");
    if (!data.extracted_skills || Object.keys(data.extracted_skills).length === 0) {
      allSkillsBox.innerHTML = `<p class="col-span-4 text-xs text-slate-500">No categorized skills identified.</p>`;
      return;
    }

    allSkillsBox.innerHTML = Object.entries(data.extracted_skills).map(([category, skills]) => `
      <div class="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
        <h5 class="text-xs font-semibold text-indigo-400 mb-2">${category}</h5>
        <div class="flex flex-wrap gap-1">
          ${skills.map(sk => `<span class="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">${sk}</span>`).join("")}
        </div>
      </div>
    `).join("");
  } catch (err) {
    console.error(err);
  }
}

// ---------------- Admin Candidate CRM ----------------
function debounceCandidateFetch() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    fetchCandidatesList();
  }, 300);
}

async function fetchCandidatesList() {
  const search = document.getElementById("filter-search").value.trim();
  const status = document.getElementById("filter-status").value;
  const minScore = document.getElementById("filter-score").value;

  let url = `/api/candidates?`;
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (status && status !== "all") params.append("status", status);
  if (minScore) params.append("min_score", minScore);

  try {
    const res = await fetch(`${url}${params.toString()}`);
    const candidates = await res.json();
    renderCandidatesTable(candidates);
  } catch (err) {
    console.error("Failed to load candidates:", err);
  }
}

function renderCandidatesTable(candidates) {
  const tbody = document.getElementById("candidates-table-body");
  if (!tbody) return;

  if (candidates.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="px-6 py-8 text-center text-slate-500">No candidates match current filters.</td></tr>`;
    return;
  }

  tbody.innerHTML = candidates.map(c => {
    const score = Math.round(c.overall_score);
    const scoreColor = score >= 80 ? "text-emerald-400 bg-emerald-950/70 border-emerald-800/40" : (score >= 60 ? "text-amber-400 bg-amber-950/70 border-amber-800/40" : "text-rose-400 bg-rose-950/70 border-rose-800/40");
    const barColor = score >= 80 ? "bg-emerald-500" : (score >= 60 ? "bg-amber-500" : "bg-rose-500");

    return `
      <tr class="hover:bg-slate-800/40 transition-colors">
        <td class="px-6 py-4">
          <div class="font-medium text-white">${c.candidate_name}</div>
          <div class="text-xs text-slate-400 flex items-center space-x-2 mt-0.5">
            <span>${c.email || 'No email'}</span>
          </div>
        </td>
        <td class="px-6 py-4 text-xs font-medium text-indigo-300">
          ${c.job_title}
        </td>
        <td class="px-6 py-4">
          <div class="flex items-center space-x-2">
            <span class="px-2 py-0.5 rounded-full text-xs font-bold border ${scoreColor}">${score}%</span>
            <div class="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden hidden sm:block">
              <div class="h-full ${barColor} rounded-full" style="width: ${score}%"></div>
            </div>
          </div>
        </td>
        <td class="px-6 py-4 text-xs text-slate-400">
          ${new Date(c.uploaded_at).toLocaleDateString()}
        </td>
        <td class="px-6 py-4">
          <select onchange="updateCandidateStatus(${c.id}, this.value)" class="text-xs bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-slate-300 focus:outline-none focus:border-indigo-500">
            <option value="Shortlisted" ${c.status === 'Shortlisted' ? 'selected' : ''}>Shortlisted</option>
            <option value="Under Review" ${c.status === 'Under Review' ? 'selected' : ''}>Under Review</option>
            <option value="Interview" ${c.status === 'Interview' ? 'selected' : ''}>Interview</option>
            <option value="Rejected" ${c.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
          </select>
        </td>
        <td class="px-6 py-4 text-right">
          <div class="flex items-center justify-end space-x-2">
            <button onclick="showCandidateModal(${c.id})" class="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/40 border border-indigo-500/30 text-indigo-300 text-xs font-medium transition-colors">
              Inspect
            </button>
            <button onclick="deleteCandidate(${c.id})" class="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition-colors" title="Delete record">
              <i data-lucide="trash" class="w-4 h-4"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");

  if (window.lucide) lucide.createIcons();
}

async function updateCandidateStatus(candidateId, newStatus) {
  try {
    const res = await fetch(`/api/candidates/${candidateId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
    if (res.ok) {
      showToast(`Status updated to ${newStatus}`);
      fetchDashboardKPIs();
    }
  } catch (err) {
    showToast("Failed to update status", "alert-circle");
  }
}

async function deleteCandidate(candidateId) {
  if (!confirm("Are you sure you want to delete this candidate record?")) return;
  try {
    const res = await fetch(`/api/candidates/${candidateId}`, { method: "DELETE" });
    if (res.ok) {
      showToast("Candidate deleted");
      fetchCandidatesList();
      fetchDashboardKPIs();
    }
  } catch (err) {
    showToast("Failed to delete candidate", "alert-circle");
  }
}

// ---------------- Candidate Detail Modal ----------------
async function showCandidateModal(candidateId) {
  try {
    const res = await fetch(`/api/candidates/${candidateId}`);
    const data = await res.json();
    
    document.getElementById("modal-candidate-name").textContent = data.candidate_name;
    document.getElementById("modal-job-title").textContent = data.latest_analysis ? `Target Role: ${data.latest_analysis.job_title}` : "";
    document.getElementById("modal-email").textContent = data.email || "N/A";
    document.getElementById("modal-phone").textContent = data.phone || "N/A";
    document.getElementById("modal-exp").textContent = `${data.experience_years} Years`;
    document.getElementById("modal-file").textContent = data.filename;
    document.getElementById("modal-raw-text").textContent = data.raw_text;

    if (data.latest_analysis) {
      const score = Math.round(data.latest_analysis.overall_score);
      const scoreEl = document.getElementById("modal-score");
      scoreEl.textContent = `${score}%`;
      scoreEl.className = `text-3xl font-display font-extrabold ${score >= 80 ? 'text-emerald-400' : (score >= 60 ? 'text-amber-400' : 'text-rose-400')}`;

      // Matched & Missing
      const matchedBox = document.getElementById("modal-matched-skills");
      matchedBox.innerHTML = (data.latest_analysis.matched_skills || []).map(s => 
        `<span class="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-xs text-emerald-300">${s}</span>`
      ).join("") || `<span class="text-xs text-slate-500">None</span>`;

      const missingBox = document.getElementById("modal-missing-skills");
      missingBox.innerHTML = (data.latest_analysis.missing_skills || []).map(s => 
        `<span class="px-2 py-0.5 rounded bg-rose-950 border border-rose-800 text-xs text-rose-300">${s}</span>`
      ).join("") || `<span class="text-xs text-slate-500">None</span>`;
    }

    document.getElementById("candidate-modal").classList.remove("hidden");
    if (window.lucide) lucide.createIcons();
  } catch (err) {
    showToast("Failed to load candidate details", "alert-circle");
  }
}

function closeCandidateModal() {
  document.getElementById("candidate-modal").classList.add("hidden");
}

// ---------------- Job Openings Actions ----------------
function openNewJobModal() {
  document.getElementById("job-modal").classList.remove("hidden");
}

function closeNewJobModal() {
  document.getElementById("job-modal").classList.add("hidden");
  document.getElementById("form-new-job").reset();
}

async function submitNewJob(e) {
  e.preventDefault();
  const title = document.getElementById("new-job-title").value.trim();
  const department = document.getElementById("new-job-dept").value.trim();
  const exp = document.getElementById("new-job-exp").value.trim();
  const skillsRaw = document.getElementById("new-job-skills").value.trim();
  const desc = document.getElementById("new-job-desc").value.trim();

  const required_skills = skillsRaw.split(",").map(s => s.trim()).filter(Boolean);

  try {
    const res = await fetch("/api/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        department,
        experience_level: exp,
        description: desc,
        required_skills
      })
    });

    if (!res.ok) throw new Error("Failed to create job");
    showToast("Job Opening created successfully!", "check-circle");
    closeNewJobModal();
    fetchJobPostings();
  } catch (err) {
    showToast(err.message, "alert-circle");
  }
}

async function deleteJob(jobId) {
  if (!confirm("Are you sure you want to delete this job opening?")) return;
  try {
    const res = await fetch(`/api/jobs/${jobId}`, { method: "DELETE" });
    if (res.ok) {
      showToast("Job opening deleted");
      fetchJobPostings();
    }
  } catch (err) {
    showToast("Failed to delete job", "alert-circle");
  }
}

// ---------------- Dashboard KPIs & Talent Analytics ----------------
async function fetchDashboardKPIs() {
  try {
    const res = await fetch("/api/analytics/dashboard");
    const data = await res.json();
    document.getElementById("kpi-total").textContent = data.total_resumes;
    document.getElementById("kpi-avg").textContent = `${data.average_score}%`;
    document.getElementById("kpi-shortlisted").textContent = data.shortlisted_count;
    document.getElementById("kpi-review").textContent = data.under_review_count;
  } catch (err) {
    console.error(err);
  }
}

async function renderAnalyticsCharts() {
  try {
    const res = await fetch("/api/analytics/dashboard");
    const data = await res.json();

    // Chart 1: Score Distribution Doughnut
    const distCtx = document.getElementById("chart-score-dist");
    if (distCtx) {
      if (chartScoreDist) chartScoreDist.destroy();

      chartScoreDist = new Chart(distCtx, {
        type: "doughnut",
        data: {
          labels: ["90 - 100% (Top Fit)", "75 - 89% (Qualified)", "50 - 74% (Review)", "< 50% (Gaps)"],
          datasets: [{
            data: [
              data.score_distribution["90-100"] || 0,
              data.score_distribution["75-89"] || 0,
              data.score_distribution["50-74"] || 0,
              data.score_distribution["<50"] || 0
            ],
            backgroundColor: ["#10b981", "#6366f1", "#f59e0b", "#f43f5e"],
            borderColor: "#111827",
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "bottom",
              labels: { color: "#94a3b8", font: { family: "Inter", size: 11 } }
            }
          }
        }
      });
    }

    // Chart 2: In-Demand Required Skills
    const skillsCtx = document.getElementById("chart-skills-demand");
    if (skillsCtx) {
      if (chartSkillsDemand) chartSkillsDemand.destroy();

      const skillLabels = data.top_in_demand_skills.map(s => s.skill);
      const skillCounts = data.top_in_demand_skills.map(s => s.count);

      chartSkillsDemand = new Chart(skillsCtx, {
        type: "bar",
        data: {
          labels: skillLabels.length ? skillLabels : ["Python", "React", "Docker", "SQL", "Git"],
          datasets: [{
            label: "Openings Requesting Skill",
            data: skillCounts.length ? skillCounts : [3, 2, 2, 2, 2],
            backgroundColor: "#6366f1",
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              ticks: { color: "#94a3b8", stepSize: 1 },
              grid: { color: "#1f293d" }
            },
            y: {
              ticks: { color: "#94a3b8" },
              grid: { display: false }
            }
          }
        }
      });
    }
  } catch (err) {
    console.error("Failed to render charts:", err);
  }
}

// ---------------- Toast Notifications ----------------
function showToast(msg, iconName = "check-circle") {
  const toast = document.getElementById("toast");
  const toastMsg = document.getElementById("toast-msg");
  const toastIcon = document.getElementById("toast-icon");

  toastMsg.textContent = msg;
  toastIcon.setAttribute("data-lucide", iconName);
  if (window.lucide) lucide.createIcons();

  toast.classList.remove("hidden");
  setTimeout(() => {
    toast.classList.add("hidden");
  }, 3500);
}
