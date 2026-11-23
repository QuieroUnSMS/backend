# QuieroUnSMS – Project Document

## 1. Executive Summary

**Project name:** QuieroUnSMS  

**Description:** Website that allows users to purchase temporary phone numbers to receive verification codes (OTP/SMS) from social networks, platforms, and applications (Instagram, WhatsApp, Telegram, TikTok, Facebook, etc.).

**Business model:** Resale of temporary numbers via specialized provider APIs. Users pay per number and receive the SMS in a real-time dashboard.

**Current status:** Project in definition phase. Main service already defined as temporary numbers for OTP verification.

---

## 2. Problem and Solution

**Problem:**  
Many people need a temporary number to verify accounts on social media or applications without using their personal number (privacy, multiple accounts, testing, etc.).
This problem raised in Mexico with the new law of telecommunications where citizens have to provide PII to the network companies in order to 
use their services.

**Solution:**  
QuieroUnSMS offers an easy-to-use platform where the user selects the service/country, purchases a temporary number, and sees the SMS code arrive in real time.

---

## 3. Main Features

### MVP (initial version)
- [ ] User registration and login
- [ ] Temporary number purchase
- [ ] Service and country selection (WhatsApp, Instagram, Telegram, etc.)
- [ ] Connection with specialized SMS providers
- [ ] Real-time SMS viewing

### Future (post-MVP)
- [ ] Number and SMS history (for logged users)
- [ ] Multi-language support (we're focusing on Mexico)

---

## 4. Key User Flows

1. **Registration / Login** (Registration is optional, by default users do not have the need to provide PII because in frontend we'll make use of sessionStorage and cookies to maintain session persistence)
2. **Number purchase** (choose service + country → pay → receive number)
3. **SMS reception** (view codes in the dashboard)

---

## 5. Technical Requirements and Preferred Stack

- **Number providers:** Grizzly SMS
- **Payments:** SPEI, Stripe

---

## 6. Scope, Priorities and Constraints

- **Priority 1:** Functional MVP with number purchase and SMS reception
- **Initial language:** Spanish (for some API responses) / English (all documents in this project)
- **Main market:** Mexico

---

## 7. Legal and Compliance Considerations

- Terms of use

Users may only use the temporary numbers provided by QuieroUnSMS for legitimate purposes, such as account verification, privacy protection, software testing, or personal use. By purchasing a number, the user agrees that they are the end user of the service and will not resell, share, or transfer the number to third parties. QuieroUnSMS reserves the right to suspend or terminate any account that violates these terms.

- Privacy policy

QuieroUnSMS collects only the information necessary to provide the service (account details, payment information, and temporary numbers used). We do not sell personal data to third parties. SMS messages received on temporary numbers are stored temporarily for the user’s convenience and are automatically deleted after a defined period. Users are responsible for not submitting sensitive personal information through the temporary numbers. For full details, see the complete Privacy Policy.

- Restrictions on prohibited uses

The following uses are strictly prohibited:
Creating fake accounts for fraud, scams, or spam
Circumventing platform bans or security measures in a malicious way
Any illegal activity, including but not limited to phishing, identity theft, or financial fraud
Sending unsolicited bulk messages or harassing others
Violation of these restrictions will result in immediate account suspension and may be reported to the relevant authorities.

- Compliance according to the country of operation

QuieroUnSMS operates in compliance with the applicable laws and regulations of its country of incorporation and the countries where it offers services. The company reserves the right to restrict access or refuse service in jurisdictions where the offering of temporary numbers is restricted or prohibited. Users are responsible for ensuring that their use of the service complies with the laws of their own country.

---

## Notes

Last update: November 23, 2026.
