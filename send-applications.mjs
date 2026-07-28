#!/usr/bin/env node
/**
 * Bulk Email Sender for YC Job Applications
 * Sends tailored emails with resume to HRs from YC job applications
 * 
 * Usage:
 *   node send-applications.js [--dry-run] [--limit N]
 * 
 * Requires .env with:
 *   GMAIL_CLIENT_ID=...
 *   GMAIL_CLIENT_SECRET=...
 *   GMAIL_REFRESH_TOKEN=...
 *   RESUME_PATH=/path/to/resume.pdf
 */

import { config } from 'dotenv';
config();

import { sendEmail, generateJobEmail } from './gmail-sender.mjs';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';

// ===================== CONFIGURATION =====================
const RESUME_PATH = process.env.RESUME_PATH || './resume.pdf';
const JOBS_LOG = './yc_applications_latest.jsonl';  // from yc-job-apply script
const SENT_LOG = './email_sent_log.jsonl';
const MAX_EMAILS_PER_RUN = parseInt(process.env.MAX_EMAILS || '50');
const DRY_RUN = process.argv.includes('--dry-run');

// Your profile (from resume)
const PROFILE = {
  name: 'Shashi Kumar',
  email: 'shashikumar69440@gmail.com',
  phone: '+91 84312 50682',
  github: 'https://github.com/shashhii',
  linkedin: 'https://linkedin.com/in/shashhii',
  current_role: 'Full Stack Developer at MindMatrix.io (Android + AI)',
  experience_years: 2,
  education: 'BE Computer Science, VTU, 2026 (CGPA 7.83)',
  salary_expectation: '4+ LPA (~$5k/month)',
  visa_status: 'Indian citizen, no visa sponsorship needed',
  location: 'Bangalore/Mysore, India (open to remote)',
  preferred_keywords: ['AI', 'ML', 'fullstack', 'remote', 'Python', 'React', 'backend', 'SaaS', 'computer vision'],
};

// ===================== HELPER FUNCTIONS =====================
function loadEnv() {
  const required = ['GMAIL_CLIENT_ID', 'GMAIL_CLIENT_SECRET', 'GMAIL_REFRESH_TOKEN'];
  for (const key of required) {
    if (!process.env[key]) {
      console.error(`❌ Missing required env var: ${key}`);
      process.exit(1);
    }
  }
  return {
    clientId: process.env.GMAIL_CLIENT_ID,
    clientSecret: process.env.GMAIL_CLIENT_SECRET,
    refreshToken: process.env.GMAIL_REFRESH_TOKEN,
  };
}

function loadApplications() {
  if (!existsSync(JOBS_LOG)) {
    console.error(`❌ Applications log not found: ${JOBS_LOG}`);
    console.error('Run the YC job application script first to generate applications.');
    process.exit(1);
  }
  
  const lines = readFileSync(JOBS_LOG, 'utf-8').trim().split('\n').filter(Boolean);
  return lines.map(line => JSON.parse(line)).filter(app => app.result === 'success');
}

function loadSentLog() {
  if (!existsSync(SENT_LOG)) return new Set();
  const lines = readFileSync(SENT_LOG, 'utf-8').trim().split('\n').filter(Boolean);
  return new Set(lines.map(l => JSON.parse(l).company));
}

function saveSentEntry(entry) {
  writeFileSync(SENT_LOG, JSON.stringify(entry) + '\n', { flag: 'a' });
}

function extractHRContact(app) {
  // Try to extract HR email from job application data
  // This is a placeholder - you'd need to extract from actual job pages
  return {
    email: `hr@${app.company.toLowerCase().replace(/[^a-z0-9]/g, '')}.com`,
    name: 'Hiring Team',
  };
}

async function sendApplicationEmail(app, credentials, gmail, dryRun = false) {
  const contact = extractHRContact(app);
  const { subject, body } = generateJobEmail({
    company: app.company,
    role: app.job_title,
    hrName: contact.name,
    jobUrl: `https://www.workatastartup.com/jobs/${app.job_id}`,
    profile: PROFILE,
  });

  console.log(`\n📧 Sending to ${contact.name} at ${app.company} (${contact.email})`);
  console.log(`   Subject: ${subject}`);
  console.log(`   Role: ${app.job_title}`);

  if (dryRun) {
    console.log('   🔍 DRY RUN - not sending');
    return { success: true, dryRun: true };
  }

  try {
    const result = await sendEmail({
      to: contact.email,
      subject,
      body,
      attachmentPath: RESUME_PATH,
      attachmentName: 'Shashi_Kumar_Resume.pdf',
      credentials,
    });
    console.log(`   ✅ Sent! Message ID: ${result.id}`);
    return { success: true, messageId: result.id };
  } catch (error) {
    console.error(`   ❌ Failed: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// ===================== MAIN =====================
async function main() {
  console.log('='.repeat(60));
  console.log('📧 YC Job Application Email Sender');
  console.log('='.repeat(60));

  if (!existsSync(RESUME_PATH)) {
    console.error(`❌ Resume not found: ${RESUME_PATH}`);
    console.error('Set RESUME_PATH in .env or place resume.pdf in project root');
    process.exit(1);
  }

  const credentials = loadEnv();
  const applications = loadApplications();
  const sentCompanies = loadSentLog();

  console.log(`📋 Found ${applications.length} successful applications`);
  console.log(`📭 Already emailed: ${sentCompanies.size} companies`);
  console.log(`📄 Resume: ${RESUME_PATH}`);
  console.log(`📊 Max emails this run: ${MAX_EMAILS_PER_RUN}`);
  if (DRY_RUN) console.log('🔍 DRY RUN MODE - no emails will be sent');

  // Filter out already emailed companies
  const toEmail = applications.filter(app => !sentCompanies.has(app.company)).slice(0, MAX_EMAILS_PER_RUN);
  console.log(`📤 Will email ${toEmail.length} new companies`);

  if (toEmail.length === 0) {
    console.log('✅ All caught up! No new companies to email.');
    return;
  }

  // Import Gmail module dynamically
  const { sendEmail, generateJobEmail } = await import('./gmail-sender.mjs');

  let sent = 0;
  let failed = 0;

  for (const app of toEmail) {
    const result = await sendApplicationEmail(app, credentials, GMAIL, DRY_RUN);
    if (result.success) {
      sent++;
      saveSentEntry({ company: app.company, timestamp: new Date().toISOString(), messageId: result.messageId });
    } else {
      failed++;
      saveSentEntry({ company: app.company, timestamp: new Date().toISOString(), error: result.error });
    }

    // Rate limiting: wait between emails
    await new Promise(r => setTimeout(r, 5000 + Math.random() * 5000));
  }

  console.log('\n' + '='.repeat(60));
  console.log(`✅ Sent: ${sent} | ❌ Failed: ${failed} | 📊 Total processed: ${toEmail.length}`);
  console.log('='.repeat(60));
}

import { generateJobEmail } from './gmail-sender.mjs';

main().catch(console.error);