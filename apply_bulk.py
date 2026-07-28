#!/usr/bin/env python3

import time
import json
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =====================
# CONFIGURATION
# =====================
LOGIN_URL = "https://account.ycombinator.com/"
SEARCH_URL = "https://www.workatastartup.com/companies?remote=only&role=eng&role_type=fs&role_type=android&usVisaNotRequired=any&sortBy=created_desc"

# Your credentials (keep this file secure!)
USERNAME = "shashi145"
PASSWORD = "Shashi@01"

# Resume data for tailoring messages
RESUME_DATA = {
    "name": "Shashi Kumar",
    "degree": "BE Computer Science",
    "university": "Maharaja Institute of Technology, Mysore",
    "graduation_year": "2026",
    "current_role": "Full Stack Developer",
    "current_company": "MindMatrix.io",
    "projects": [
        "Camouflage Object Detection (using SINet V2, PyTorch, CUDA)",
        "Muntz Tech Development (fullstack e-commerce platform)"
    ],
    "skills": ["Python", "JavaScript", "Frontend/Backend", "AWS", "Git", "Docker", "TensorFlow"]
}

# =====================
# SETUP
# =====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/data/jobs/application_log.json'),
        logging.StreamHandler()
    ]
)

def send_message(driver, company_name, job_title, message):
    """Type and submit message in the Apply modal"""
    # Wait for modal to appear
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//textarea"))
    )
    
    # Enter the message
    textarea = driver.find_element(By.XPATH, "//textarea")
    textarea.clear()
    textarea.send_keys(message)
    
    # Click the Send button
    submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Send') or contains(text(), 'Apply')]")
    submit_btn.click()
    
    # Wait for success indication
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'saved') or contains(text(), 'success')]"))
        )
        logging.info(f"✅ Sent application to {company_name} - {job_title}")
    except Exception as e:
        logging.error(f"❌ Failed to submit to {company_name}: {str(e)}")

# =====================
# MAIN SCRIPT
# =====================
def main():
    # Setup Chrome driver (no extensions, persistent session)
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # 1. LOG IN TO YC ACCOUNT
        print("1) Logging in to YC...")
        driver.get(LOGIN_URL)
        
        # Fill username
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(USERNAME)
        
        # Continue
        driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]").click()
        
        # Enter password
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "password"))
        ).send_keys(PASSWORD)
        
        # Click Log In
        driver.find_element(By.XPATH, "//button[text()='Log In']").click()
        
        # Wait for dashboard
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//heading[text()='Apply to top YC startup jobs']"))
        )
        
        print("✅ Logged in successfully!")
        
        # 2. Navigate to farmed jobs
        print("2) Navigating to filtered jobs...")
        driver.get(SEARCH_URL)
        
        # Wait for jobs to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[text()='Apply']"))
        )
        
        # Find all Apply buttons (they're generic at this point)
        apply_btns = driver.find_elements(By.XPATH, "//a[contains(@ref,'Add') or contains(., 'Apply') or contains(., 'Apply now')]")
        print(f"✅ Found {len(apply_btns)} Apply buttons")
        
        # ---- FILTER JOBS (you can customize this section) ----
        # We'll target jobs that mention India, Remote, Senior, etc.
        relevant_buttons = []
        
        for i, btn in enumerate(apply_btns[:50]):  # Process first ~50
            # Try to get the containing job card for context
            try:
                # Scroll to button to ensure it's rendered
                driver.scroll_by_pixels(0, 200 * i)
                time.sleep(1)
                
                # Try to click to see if it’s interactive
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                time.sleep(0.5)
                
                # Try to see if it's still clickable
                if btn.is_displayed() and btn.enabled:
                    relevant_buttons.append(i)
                    print(f"  Approved apply button {i} (index in list: {i})")
                    
            except Exception as e:
                continue
        
        # Take first few relevant buttons
        relevant_buttons = relevant_buttons[:30]  # Limit to 30 for demo
        
        # ===== APPLY TO EACH JOB ===
        applications_log = []
        for i, idx in enumerate(relevant_buttons[:30]):  # Limit to 30 applications per session
            try:
                # Click the job to open details/modal
                btn = apply_btns[idx]
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                
                # Click Apply
                btn.click()
                
                # Wait for modal to appear
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//textarea"))  # Text area appears in modal
                )
                
                # Get company and job title from page (basic extraction)
                # Example: subtitle often contains "Company • Role"
                company_elem = driver.find_element(By.XPATH, "//strong[contains(@ref,'company') or contains(text(), 'at')]") or \
                              driver.find_element(By.XPATH, "//h3[contains(., 'Apply')]//ancestor::strong")
                job_title_elem = driver.find_element(By.XPATH, "//h2[contains(., 'Apply now') or contains(@level, 'level') and contains(., 'Senior')]/*ancestor::strong")
                
                company_name = company_elem.text.strip() if company_elem else "Unknown Company"
                job_title = driver.find_element(By.XPATH, "//h2[contains(., 'Apply now') or contains(@ref,'job')]/ancestor::strong").text.strip()
                
                # BUILD PERSONALIZED MESSAGE
                # Use resume data to tailor it
                msg_parts = [
                    f"Hi {job_title.split()[0]},",
                    "",
                    "My name is Shashi Kumar, a full-stack developer with 2+ years of experience building scalable web applications.",
                    "I noticed your job posting for {job_title} at {company_name} and was immediately impressed by {specific detail from job description}.",
                    "",
                    "At MindMatrix.io, I developed a camouflage object detection system using PyTorch and CUDA,",
                    "and recently contributed to Muntz Tech Development's fullstack platform. My resume includes Python, React, and AWS expertise.",
                    "I'm particularly interested in roles that leverage my experience in:",
                    "  • Python backends with async frameworks",
                    "  • Frontend scalability with React/Angular",
                    "  • AI/ML integration for feature enhancement",
                    "",
                    "I'm flexible with remote roles and currently seeking positions paying 4LPA+ (approx. $5k+/month).",
                    "My resume highlights projects in AI object detection and fullstack development.",
                    "You can review my resume at /opt/data/career-ops/resumes/shashi_resume.pdf"
                ]
                
                message = "\n".join([p for p in parts if p.strip()])
                
                # Ensure minimum 50 characters (as required by platform)
                if len(message) < 50:
                    extra = "Actively exploring opportunities in fullstack development and AI integration. Seeking roles that allow me to grow technically while contributing to innovative products."
                    parts.append(extra)
                
                # Send the message
                textarea = driver.find_element(By.XPATH, "//textarea")
                textarea.clear()
                textarea.send_keys(parts[:2000])  # Limit to prevent overflow
                time.sleep(1)
                send_btn = driver.find_element(By.XPATH, "//button[text()='Send' or contains(., 'Apply')]") 
                send_btn.click()
                
                # Log success
                logging.info(f"✅ Applied to {company_name} - {job_title}")
                applications_log.append({
                    "company": company_name,
                    "job_title": job_title,
                    "status": "success",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Go back to jobs page to continue applying
                driver.back()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(@ref, 'Apply')]"))
                )
                time.sleep(1)
            except Exception as e:
                logging.error(f"❌ Failed to apply to job index {i}: {str(e)}")
                time.sleep(2)
        
        # 4. Save final log
        with open('/opt/data/jobs/application_log.json', 'a') as f:
            for entry in applications_log:
                json.dump(entry, f, separators=(',', ': '), ensure_ascii=False)
                f.write('\n')
        
        print("🎉 Application process completed!")
        print("📝 Your applications have been logged to /opt/data/jobs/application_log.json")
        print("📬 Check your email and YC inbox for confirmation messages.")
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    main()