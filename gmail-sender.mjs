/**
 * Gmail Email Sender Module
 * Sends tailored job application emails with resume attachments via Gmail API
 * 
 * Requires in .env:
 * - GMAIL_CLIENT_ID
 * - GMAIL_CLIENT_SECRET  
 * - GMAIL_REFRESH_TOKEN
 * (OAuth credentials with gmail.send scope)
 */

import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

const TOKEN_URL = 'https://oauth2.googleapis.com/token';
const GMAIL_API = 'https://gmail.googleapis.com/gmail/v1/users/me';

const SCOPES = ['https://www.googleapis.com/auth/gmail.send'];

/** Exchange refresh token for access token */
async function getAccessToken(credentials, fetchFn = globalThis.fetch) {
  const res = await fetchFn(TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: credentials.clientId,
      client_secret: credentials.clientSecret,
      refresh_token: credentials.refreshToken,
      grant_type: 'refresh_token',
    }),
  });
  
  if (!res.ok) {
    throw new Error(`Token refresh failed: ${res.status} ${await res.text()}`);
  }
  const data = await res.json();
  if (!data.access_token) throw new Error('No access_token returned');
  return data.access_token;
}

/** Create MIME message with attachment */
function createMimeMessage({ to, subject, body, attachmentPath, attachmentName }) {
  const boundary = `boundary_${Date.now()}_${Math.random().toString(36).slice(2)}`;
  
  let message = [
    `To: ${to}`,
    `Subject: ${subject}`,
    `MIME-Version: 1.0`,
    `Content-Type: multipart/mixed; boundary="${boundary}"`,
    '',
    `--${boundary}`,
    'Content-Type: text/plain; charset="UTF-8"',
    'Content-Transfer-Encoding: 7bit',
    '',
    body,
    '',
  ];
  
  if (attachmentPath && existsSync(attachmentPath)) {
    const fileContent = readFileSync(attachmentPath, { encoding: 'base64' });
    const filename = attachmentName || 'resume.pdf';
    
    message.push(
      `--${boundary}`,
      `Content-Type: application/pdf; name="${filename}"`,
      'Content-Transfer-Encoding: base64',
      `Content-Disposition: attachment; filename="${filename}"`,
      '',
      fileContent,
      '',
    );
  }
  
  message.push(`--${boundary}--`);
  
  return Buffer.from(message.join('\r\n')).toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

/** Send email via Gmail API */
async function sendEmail({ to, subject, body, attachmentPath, attachmentName, credentials, fetchFn = globalThis.fetch }) {
  const token = await getAccessToken(credentials, fetchFn);
  const raw = createMimeMessage({ to, subject, body, attachmentPath, attachmentName });
  
  const res = await fetchFn('https://gmail.googleapis.com/gmail/v1/users/me/messages/send', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ raw }),
  });
  
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Gmail send failed: ${res.status} ${error}`);
  }
  
  return await res.json();
}

/** Generate tailored email for a specific job */
function generateJobEmail({ company, role, hrName, jobUrl, profile }) {
  const subject = `Application: ${role} at ${company} — ${profile.name}`;
  
  const body = `Hi ${hrName || 'Hiring Team'},

I'm ${profile.name}, a ${profile.current_role} with ${profile.experience_years}+ years of experience building scalable web and mobile applications. I came across the ${role} position at ${company} and was immediately drawn to your mission.

A bit about my background:
• ${profile.experience_years}+ years full-stack development (React, Node.js, Python, React Native)
• Recently built a Camouflage Object Detection system (PyTorch, CUDA, 20K+ images)
• Built Muntz Tech — a full-stack e-commerce platform (React, Node.js, MongoDB)
• Currently at MindMatrix.io developing AI-driven Android apps for engineering education

What excites me about ${company}: your work in ${profile.preferred_keywords.slice(0,3).join(', ')} aligns perfectly with my background. I'm particularly interested in how you're tackling [specific challenge from job description].

I'm based in Bangalore/Mysore, open to remote work, and require no visa sponsorship (Indian citizen). My salary expectation is ${profile.salary_expectation}.

Resume: ${profile.github}
LinkedIn: ${profile.linkedin}

Would love to chat about how I can contribute to ${company}'s mission!

Best regards,
${profile.name}
${profile.email}
${profile.phone}`;

  return { subject, body };
}

export { sendEmail, generateJobEmail, getAccessToken };
export default { sendEmail, generateJobEmail, getAccessToken };