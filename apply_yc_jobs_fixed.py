#!/usr/bin/env python3
"""
YC Work at a Startup - Bulk Job Application Script
Applies to all remote, India-friendly software engineering jobs
with tailored cover letters based on your resume.
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

SEARCH_URL = ("https://www.workatastartup.com/companies?"
              "remote=only&role=eng&role_type=fs&role_type=android"
              "&usVisaNotRequired=any&minExperience=0&sortBy=created_desc")

LOG_FILE = f"yc_applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

# Your profile data (extracted from your resume)
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
    "skills": ["Python", "JavaScript/TypeScript", "React", "Node.js", "Java/Kotlin", 
              "AWS", "Docker", "Git", "TensorFlow", "PyTorch", "SQL", "MongoDB"],
    "projects": [
        "Camouflage Object Detection (using SINet V2, PyTorch, CUDA)",
        "Muntz Tech Development (fullstack e-commerce platform)"
    ]
}

# ===================== HELPER FUNCTIONS =====================
def human_delay(min_s=0.8, max_s=2.0):
    """Random human-like delay"""
    time.sleep(random.uniform(min_s, max_s))

def setup_logging():
    """Configure logging to file and console"""
    logger = logging.getLogger("yc_apply")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    # File handler
    fh = logging.FileHandler(LOG_FILE.replace('.jsonl', '.log'))
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)
    
    return logger

def build_driver():
    """Create Chrome driver with anti-detection options"""
    opts = Options()
    # Anti-detection
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    # Stability
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    # User agent
    opts.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    
    # Remove webdriver property
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    return driver

def login_yc(driver, wait):
    """Log into YC account"""
    driver.get("https://account.ycombinator.com/?continue=" + SEARCH_URL)
    
    # Username
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(YC_USERNAME)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]").click()
    human_delay(1, 2)
    
    # Password
    wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(YC_PASSWORD)
    driver.find_element(By.XPATH, "//button[text()='Log In']").click()
    
    # Wait for redirect
    wait.until(EC.url_contains("workatastartup.com"))
    human_delay(2, 3)
    print("✅ Logged in successfully!")

def generate_message(company_name, job_title, job_desc):
    """Generate tailored cover letter"""
    
    # Extract relevant keywords from job description
    keywords = []
    jd_lower = job_desc.lower()
    if "python" in jd_lower: keywords.append("Python")
    if "react" in jd_lower: keywords.append("React")
    if "node" in jd_lower or "javascript" in jd_lower: keywords.append("JavaScript/Node.js")
    if "ai" in jd_lower or "ml" in jd_lower or "machine learning" in jd_lower: keywords.append("AI/ML")
    if "android" in jd_lower or "kotlin" in jd_lower: keywords.append("Android/Kotlin")
    if "aws" in jd_lower or "cloud" in jd_lower: keywords.append("AWS/Cloud")
    if "fullstack" in jd_lower or "full stack" in jd_lower: keywords.append("Full Stack")
    
    keyword_str = ", ".join(keywords) if keywords else "software engineering"
    
    msg = f"""Hi {company_name} team,

I'm Shashi Kumar, a full-stack developer with 2+ years of experience building scalable web and mobile applications. I'm excited about the {job_title} role at {company_name} — your work in {keyword_str} aligns perfectly with my background.

At MindMatrix.io, I develop Android apps with AI features (camouflage object detection using PyTorch/CUDA) and full-stack platforms (React, Node.js, Python). My recent projects include a camouflage object detection system (SINet V2, PyTorch, 20K+ training images) and Muntz Tech Development, a full-stack e-commerce platform.

What draws me to {company_name}: your focus on {keyword_str} and building impactful products. I'm particularly interested in how you're tackling [specific challenge from job description].

I'm based in Bangalore/Mysore, open to remote work, and require no visa sponsorship (Indian citizen). My salary expectation is 4+ LPA (~$5k/month).

My GitHub: https://github.com/shashhii | LinkedIn: https://linkedin.com/in/shashhii

Would love to discuss how I can contribute to your team!

Best regards,
Shashi Kumar
shashikumar69440@gmail.com
+91 84312 50682"""

    return msg

# ===================== MAIN =====================
def main():
    logger = setup_logging()
    logger.info("="*60)
    logger.info("🚀 Starting YC bulk job application")
    logger.info(f"📝 Log file: {LOG_FILE}")
    logger.info("="*60)
    
    driver = None
    try:
        # Build driver
        driver = build_driver()
        wait = WebDriverWait(driver, 20)
        
        # 1. Login
        login_yc(driver, wait)
        
        # 2. Go to filtered jobs
        driver.get(SEARCH_URL)
        human_delay(3, 5)
        
        # 3. Process jobs
        total_applied = 0
        page = 1
        
        while total_applied < 50:  # Safety limit
            logger.info(f"📄 Processing page {page}")
            
            # Find company cards (each startup block)
            try:
                # Wait for company list to load
                wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//a[contains(text(), 'View job')]")
                ))
            except:
                logger.warning("No jobs found on page")
                break
            
            # Get all "View job" links
            view_jobs = driver.find_elements(By.XPATH, "//a[contains(text(), 'View job')]")
            logger.info(f"Found {len(view_jobs)} jobs on page {page}")
            
            for i, view_btn in enumerate(view_jobs):
                if total_applied >= 50:
                    break
                
                try:
                    # Click View Job
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", view_btn)
                    human_delay(0.5, 1)
                    view_btn.click()
                    human_delay(2, 3)
                    
                    # Wait for job detail
                    wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//a[contains(text(), 'Apply')]")
                    ))
                    
                    # Get company name and job title
                    company = driver.find_element(By.XPATH, "//a[contains(@href, '/companies/')]").text
                    job_title = driver.find_element(By.TAG_NAME, "h1").text
                    
                    # Try to get job description for tailoring
                    try:
                        job_desc = driver.find_element(
                            By.XPATH, "//section[contains(., 'About') or contains(., 'role')]"
                        ).text
                    except:
                        job_desc = ""
                    
                    logger.info(f"📝 Applying to {company} - {job_title}")
                    
                    # Click Apply
                    apply_btn = driver.find_element(By.XPATH, "//a[text()='Apply' or text()='Apply now']")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", apply_btn)
                    human_delay(0.5, 1)
                    apply_btn.click()
                    
                    # Wait for modal with textarea
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
                    human_delay(0.5, 1)
                    
                    # Fill message
                    textarea = driver.find_element(By.TAG_NAME, "textarea")
                    msg = generate_message(company, job_title, job_desc)
                    textarea.clear()
                    textarea.send_keys(msg)
                    human_delay(0.5, 1)
                    
                    # Click Send
                    send_btn = driver.find_element(By.XPATH, 
                        "//button[contains(text(), 'Send') or contains(text(), 'Submit') or contains(text(), 'Apply')]")
                    send_btn.click()
                    human_delay(2, 3)
                    
                    # Log success
                    logger.info(f"✅ Applied: {company} - {job_title}")
                    total_applied += 1
                    
                    # Log to JSONL
                    with open(LOG_FILE, "a") as f:
                        f.write(json.dumps({
                            "timestamp": datetime.now().isoformat(),
                            "company": company,
                            "job_title": job_title,
                            "result": "success",
                            "message_preview": msg[:100]
                        }) + "\n")
                    
                except Exception as e:
                    logger.error(f"❌ Failed on job {i}: {e}")
                
                # Go back to companies list
                driver.get(SEARCH_URL)
                human_delay(2, 3)
            
            # Try next page
            try:
                next_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Next') or @aria-label='Next page']")
                if next_btn.is_enabled():
                    next_btn.click()
                    page += 1
                    human_delay(3, 5)
                else:
                    break
            except:
                break
        
        logger.info(f"🎉 Done! Applied to {total_applied} jobs. Log: {LOG_FILE}")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        if driver:
            driver.quit()
        logger.info("👋 Browser closed")

if __name__ == "__main__":
    main()