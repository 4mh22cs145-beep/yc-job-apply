#!/usr/bin/env python3
"""
YC Work at a Startup - Bulk Job Application Script
==================================================
Applies to all remote, India-friendly software engineering jobs
with tailored cover letters based on your resume.

Requirements:
- Python 3.8+
- Chrome browser installed
- pip install selenium webdriver-manager

Usage:
    python3 apply_yc_jobs.py
"""

import time
import json
import logging
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ===================== CONFIGURATION =====================
YC_USERNAME = "shashi145"
YC_PASSWORD = "Shashi@01"

# Search URL with your exact filters
SEARCH_URL = (
    "https://www.workatastartup.com/companies?"
    "remote=only&role=eng&role_type=fs&role_type=android"
    "&usVisaNotRequired=any&minExperience=0&sortBy=created_desc"
)

LOG_FILE = f"yc_applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

# Your profile data from resume
PROFILE = {
    "name": "Shashi Kumar",
    "email": "shashikumar69440@gmail.com",
    "phone": "+91 84312 50682",
    "linkedin": "https://linkedin.com/in/shashhii",
    "github": "https://github.com/shashhii",
    "location": "Mysore/Bangalore, India",
    "visa_status": "Indian citizen, no visa sponsorship needed",
    "current_role": "Full Stack Developer at MindMatrix.io (Android + AI)",
    "experience_years": 2,
    "education": "BE Computer Science, VTU, 2026 (CGPA 7.83)",
    "skills": [
        "Python", "JavaScript/TypeScript", "React", "Node.js", "Java/Kotlin",
        "AWS", "Docker", "Git", "TensorFlow", "PyTorch", "SQL", "MongoDB"
    ],
    "projects": [
        "Camouflage Object Detection (SINet V2, PyTorch, CUDA, 20K+ images)",
        "Muntz Tech Development (Full-stack e-commerce, React/Node/MongoDB)"
    ],
    "salary_expectation": "4+ LPA (~$5k/month)",
    "preferred_keywords": ["AI", "ML", "fullstack", "remote", "Python", "React", "backend", "SaaS", "computer vision"]
}

MAX_APPLICATIONS = 200  # Updated to 200 as requested
# ==========================================================

def human_delay(min_s=1.0, max_s=2.5):
    """Random human-like delay"""
    time.sleep(random.uniform(min_s, max_s))

def setup_logging():
    logger = logging.getLogger("yc_apply")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    fh = logging.FileHandler(LOG_FILE.replace('.jsonl', '.log'))
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)
    
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)
    
    return logger

def build_driver():
    """Create Chrome driver with anti-detection options"""
    opts = Options()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    return driver

def login_yc(driver, wait):
    """Log into YC account"""
    driver.get("https://account.ycombinator.com/?continue=" + SEARCH_URL)
    
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(YC_USERNAME)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]").click()
    human_delay()
    
    wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(YC_PASSWORD)
    driver.find_element(By.XPATH, "//button[text()='Log In']").click()
    
    wait.until(EC.url_contains("workatastartup.com"))
    human_delay(2, 3)
    print("✅ Logged in successfully!")

def generate_message(company_name, job_title, job_desc):
    """Generate tailored cover letter for each application"""
    
    jd_lower = job_desc.lower()
    relevant_skills = []
    for skill in PROFILE["skills"]:
        if skill.lower() in jd_lower:
            relevant_skills.append(skill)
    if not relevant_skills:
        relevant_skills = ["Python", "React", "Node.js", "AWS", "Docker", "AI/ML"]
    
    skill_str = ", ".join(relevant_skills[:5])
    
    message = f"""Hi {company_name} team,

I'm Shashi Kumar — a full-stack developer with 2+ years building scalable web and mobile applications. I'm excited about the {job_title} role at {company_name} — your work aligns perfectly with my background in:

• {skill_str}
• Building production ML pipelines (recently built a Camouflage Object Detection system with PyTorch/CUDA)
• Full-stack development (React/Node, Python, React Native for Android)
• Cloud deployment on AWS with Docker

At MindMatrix.io, I'm developing AI-driven Android apps for engineering education, reducing manual content effort by ~40%. Previously built Muntz Tech — a full-stack e-commerce platform (React/Node/MongoDB).

I'm based in Bangalore/Mysore, Indian citizen (no visa sponsorship needed), and seeking 4+ LPA remote roles. My resume: https://github.com/shashhii

I'd love to chat about how I can contribute to {company_name}!

Best regards,
Shashi Kumar
shashikumar69440@gmail.com | +91 84312 50682"""
    
    return message.strip()

def apply_to_job(driver, wait, company_card, logger):
    """Click View Job, then Apply, fill modal, submit"""
    try:
        view_btn = company_card.find_element(By.XPATH, ".//a[contains(text(), 'View job') or contains(text(), 'View')]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", view_btn)
        human_delay(0.5, 1)
        view_btn.click()
        human_delay(2, 3)
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Apply')]")))
        
        try:
            job_title = driver.find_element(By.XPATH, "//h1").text
        except:
            job_title = "Software Engineer"
        
        try:
            job_desc = driver.find_element(By.XPATH, "//section[contains(., 'About') or contains(., 'role')]").text
        except:
            job_desc = ""
        
        try:
            company_name = driver.find_element(By.XPATH, "//a[contains(@href, '/companies/')]").text
        except:
            company_name = "the team"
        
        apply_btn = driver.find_element(By.XPATH, "//a[text()='Apply' or text()='Apply now']")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", apply_btn)
        human_delay(0.5, 1)
        apply_btn.click()
        
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
        human_delay(0.5, 1)
        
        textarea = driver.find_element(By.TAG_NAME, "textarea")
        msg = generate_message(company_name, job_title, job_desc)
        textarea.clear()
        textarea.send_keys(msg)
        human_delay(0.5, 1)
        
        send_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Send') or contains(text(), 'Submit') or contains(text(), 'Apply')]")
        send_btn.click()
        human_delay(2, 3)
        
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'sent') or contains(text(), 'saved') or contains(text(), 'applied')]")
            ))
            result = "success"
        except:
            result = "unknown"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "company": company_name,
            "job_title": job_title,
            "result": result,
            "message_preview": msg[:100]
        }
        
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        logger.info(f"✅ Applied to {company_name} - {job_title} [{result}]")
        
        driver.get(SEARCH_URL)
        human_delay(2, 3)
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to apply to card: {e}")
        driver.get(SEARCH_URL)
        human_delay(2, 3)
        return False


# ===================== MAIN =====================
if __name__ == "__main__":
    logger = logging.getLogger("yc_apply")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    fh = logging.FileHandler(LOG_FILE.replace('.jsonl', '.log'))
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)
    
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)
    
    logger.info("="*50)
    logger.info("🚀 Starting YC bulk job application")
    logger.info(f"📝 Log file: {LOG_FILE}")
    logger.info(f"🎯 Max applications: {MAX_APPLICATIONS}")
    logger.info("="*50)
    
    driver = None
    try:
        driver = build_driver()
        wait = WebDriverWait(driver, 20)
        
        login_yc(driver, WebDriverWait(driver, 20))
        
        driver.get(SEARCH_URL)
        human_delay(3, 5)
        
        page = 1
        total_applied = 0
        
        while total_applied < MAX_APPLICATIONS:
            logger.info(f"📄 Processing page {page}")
            
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//a[contains(text(), 'View job')]")
            ))
            
            cards = driver.find_elements(By.XPATH, "//div[contains(@onclick, 'click') or contains(@style, 'cursor: pointer')]")
            logger.info(f"Found {len(cards)} company cards on page {page}")
            
            for i, card in enumerate(cards):
                if total_applied >= MAX_APPLICATIONS:
                    break
                try:
                    apply_to_job(driver, wait, card, logger)
                    total_applied += 1
                except Exception as e:
                    logger.error(f"Error on card {i}: {e}")
                    continue
            
            try:
                next_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Next') or contains(@aria-label, 'Next')]")
                if next_btn.is_enabled():
                    next_btn.click()
                    page += 1
                    human_delay(3, 5)
                else:
                    break
            except:
                break
        
        logger.info(f"🎉 Done! Applied to {total_applied} jobs. Log saved to {LOG_FILE}")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        if driver:
            driver.quit()
        logger.info("👋 Browser closed")