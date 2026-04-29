# DATASET = [
#     {
#         "id": 1,
#         "input_text": "URGENT: Your PayPal account has been suspended due to unusual activity. Click here [http://paypal-security-update.com/login] to verify your identity within 24 hours or your account will be permanently closed.",
#         "expected": '{"is_phishing": true, "threat_vector": "malicious_link"}'
#     },
#     {
#         "id": 2,
#         "input_text": "Attached is the overdue invoice #99124 for your recent purchase. Please remit payment immediately to avoid legal action. Best, Accounting.",
#         "expected": '{"is_phishing": true, "threat_vector": "malicious_attachment"}'
#     },
#     {
#         "id": 3,
#         "input_text": "Hey, it's John from HR. I'm stuck in a meeting and need a huge favor. Can you buy $500 in Apple gift cards for a client presentation right now? I'll reimburse you later today. Please hurry!",
#         "expected": '{"is_phishing": true, "threat_vector": "urgency_manipulation"}'
#     },
#     {
#         "id": 4,
#         "input_text": "Hi Team, just a reminder that the Q3 All-Hands meeting is scheduled for next Thursday at 2 PM in the main conference room. Pizza will be provided! Cheers, Sarah.",
#         "expected": '{"is_phishing": false, "threat_vector": "none"}'
#     },
#     {
#         "id": 5,
#         "input_text": "Your Amazon order #112-4412-991 has shipped! Track your package securely at https://amazon.com/orders/tracking. Thank you for shopping with us.",
#         "expected": '{"is_phishing": false, "threat_vector": "none"}'
#     },
#     {
#         "id": 6,
#         "input_text": "Hey Mark, can you review the attached draft for the upcoming marketing campaign? Let me know your thoughts by Friday.",
#         "expected": '{"is_phishing": false, "threat_vector": "none"}'
#     },
#     {
#         "id": 7,
#         "input_text": "IT ALERT: We are migrating to a new Exchange server tonight at 11 PM. You may experience a 10-minute downtime. No action is required on your part. Do not share your password.",
#         "expected": '{"is_phishing": false, "threat_vector": "none"}'
#     },
#     {
#         "id": 8,
#         "input_text": "IT ALERT: Your mailbox quota is full. To prevent incoming emails from bouncing, you must upgrade your quota immediately by logging in here: http://webmail-upgrade-portal.info/login.",
#         "expected": '{"is_phishing": true, "threat_vector": "malicious_link"}'
#     },
#     {
#         "id": 9,
#         "input_text": "Did you see this picture of you from the weekend party?? LOL download it here: photo_weekend.exe",
#         "expected": '{"is_phishing": true, "threat_vector": "malicious_attachment"}'
#     },
#     {
#         "id": 10,
#         "input_text": "Don't miss out on our Black Friday deals! Get 50% off all shoes. Click here to browse our catalog. Unsubscribe at the bottom of this email.",
#         "expected": '{"is_phishing": false, "threat_vector": "none"}'
#     },
#     {
#         "id": 11,
#         "input_text": "Microsoft Security: A sign-in attempt from Russia was blocked. If this wasn't you, secure your account by changing your password immediately at https://account.microsoft-secure-auth.com.",
#         "expected": '{"is_phishing": true, "threat_vector": "malicious_link"}'
#     },
# {
#         "id": 12,
#         "input_text": "Hi, please find my resume attached for the Senior Developer role. Let me know if you need any further information. Best, Emily. [Attachment: Emily_Resume_PDF.zip]",
#         "expected": '{"is_phishing": true, "threat_vector": "malicious_attachment"}'
#     },
#     {
#         "id": 13,
#         "input_text": "Are you at your desk? I am in a meeting with a potential partner and need you to process a wire transfer to them right now. Reply to this email immediately so I can send the details.",
#         "expected": '{"is_phishing": true, "threat_vector": "urgency_manipulation"}'
#     },
#     {
#         "id": 14,
#         "input_text": "Reminder: Please restart your laptops by EOD Friday to apply the monthly security patch. Contact the IT Helpdesk at ext. 5555 if you have any issues.",
#         "expected": '{"is_phishing": false, "threat_vector": "none"}'
#     },
#     {
#         "id": 15,
#         "input_text": "Alex shared a confidential financial report with you on OneDrive. Click here to view and sign the document: http://onedrive-login-secure.co/auth",
#         "expected": '{"is_phishing": true, "threat_vector": "malicious_link"}'
#     },
#     {
#         "id": 16,
#         "input_text": "You have 3 unread messages in the #marketing-campaign channel. Open the Slack app to view and reply to your team.",
#         "expected": '{"is_phishing": false, "threat_vector": "none"}'
#     },
#     {
#         "id": 17,
#         "input_text": "Thank you for your recent Apple Store purchase of $899.00. Please see the attached receipt.docx for transaction details. If you did not make this purchase, contact our support team immediately.",
#         "expected": '{"is_phishing": true, "threat_vector": "malicious_attachment"}'
#     },
#     {
#         "id": 18,
#         "input_text": "Status Update: Jira is currently experiencing degraded performance. Our engineering team is investigating the root cause. We will provide another update in 30 minutes.",
#         "expected": '{"is_phishing": false, "threat_vector": "none"}'
#     },
#     {
#         "id": 19,
#         "input_text": "HR Notice: We encountered an error processing your direct deposit for this pay period. Please reply with your updated banking details immediately to avoid delays in receiving your paycheck.",
#         "expected": '{"is_phishing": true, "threat_vector": "urgency_manipulation"}'
#     },
#     {
#         "id": 20,
#         "input_text": "Netflix: Your membership has been paused because we couldn't authorize your payment for the next billing cycle. Update your payment info here to resume watching: http://netflix-billing-update-support.net",
#         "expected": '{"is_phishing": true, "threat_vector": "malicious_link"}'
#     },
#     {
#         "id": 21,
#         "input_text": "Weekly Tech Digest: Top 5 AI trends to watch this month. Plus, don't forget to register for our upcoming free webinar on cloud security best practices.",
#         "expected": '{"is_phishing": false, "threat_vector": "none"}'
#     }
# ]

DATASET = [
    {
        "id": 1,
        "input_text": "I was charged twice for my subscription this month! I need a refund immediately, my bank account is overdrawn!",
        "expected": '{"department": "billing", "priority": "high"}'
    },
    {
        "id": 2,
        "input_text": "The main server API is returning 500 Internal Server Error for all requests. Our production app is completely down.",
        "expected": '{"department": "technical", "priority": "high"}'
    },
    {
        "id": 3,
        "input_text": "My package was supposed to arrive last Tuesday, but the tracking hasn't updated in 5 days. Can you check where it is?",
        "expected": '{"department": "shipping", "priority": "medium"}'
    },
    {
        "id": 4,
        "input_text": "How do I change the avatar picture on my profile? I can't find the settings menu.",
        "expected": '{"department": "general", "priority": "low"}'
    },
    {
        "id": 5,
        "input_text": "I love the new dark mode feature! Great job team, it makes reading at night so much easier.",
        "expected": '{"department": "general", "priority": "low"}'
    },
    {
        "id": 6,
        "input_text": "I want to cancel my account at the end of the current billing cycle. What is the process for this?",
        "expected": '{"department": "billing", "priority": "medium"}'
    },
    {
        "id": 7,
        "input_text": "The mobile app keeps crashing every time I try to upload a video larger than 50MB. I'm using an iPhone 13.",
        "expected": '{"department": "technical", "priority": "medium"}'
    },
    {
        "id": 8,
        "input_text": "I received the wrong item. I ordered a blue shirt size L, but the box contained a red hat.",
        "expected": '{"department": "shipping", "priority": "high"}'
    },
    {
        "id": 9,
        "input_text": "Is there a discount available for non-profit organizations or students? Let me know, thanks.",
        "expected": '{"department": "billing", "priority": "low"}'
    },
    {
        "id": 10,
        "input_text": "I dropped my laptop and the screen cracked. I bought the extended warranty last year. How do I send it in for repair?",
        "expected": '{"department": "technical", "priority": "medium"}'
    },
    {
        "id": 11,
        "input_text": "URGENT: Your delivery driver literally threw my fragile package over the fence and shattered the glass vase inside. I have it on camera!",
        "expected": '{"department": "shipping", "priority": "high"}'
    },
    {
        "id": 12,
        "input_text": "My credit card was stolen and I see unauthorized charges from your company today. Cancel everything immediately and refund me!",
        "expected": '{"department": "billing", "priority": "high"}'
    },
    {
        "id": 13,
        "input_text": "Does your API support GraphQL? I'm just exploring tech stack options for a project we might start next quarter.",
        "expected": '{"department": "technical", "priority": "low"}'
    },
    {
        "id": 14,
        "input_text": "The tracking status says 'Delivered', but I've checked my porch, the mailbox, and asked my neighbors. It's nowhere to be found.",
        "expected": '{"department": "shipping", "priority": "medium"}'
    },
    {
        "id": 15,
        "input_text": "I want to file a formal complaint about the customer service representative I spoke to yesterday. They were extremely rude and unhelpful.",
        "expected": '{"department": "general", "priority": "medium"}'
    },
    {
        "id": 16,
        "input_text": "URGENT: All our customer data has vanished from the dashboard after your latest platform update. We cannot operate our business right now!",
        "expected": '{"department": "technical", "priority": "high"}'
    },
    {
        "id": 17,
        "input_text": "My invoice for this month is incorrect. It doesn't include the 20% promotional discount code 'SUMMER20' that I applied during checkout.",
        "expected": '{"department": "billing", "priority": "medium"}'
    },
    {
        "id": 18,
        "input_text": "Can I change my default shipping address for all future orders? I just moved to a new city.",
        "expected": '{"department": "shipping", "priority": "low"}'
    },
    {
        "id": 19,
        "input_text": "I need to be put in touch with your legal department immediately regarding a cease and desist order. Provide contact details ASAP.",
        "expected": '{"department": "general", "priority": "high"}'
    },
    {
        "id": 20,
        "input_text": "I can log into the web version just fine, but the Windows desktop client keeps rejecting my 2FA authentication token.",
        "expected": '{"department": "technical", "priority": "medium"}'
    },
    {
        "id": 21,
        "input_text": "Do you guys have any physical store locations in Warsaw, Poland? Or is your business strictly online only?",
        "expected": '{"department": "general", "priority": "low"}'
    }
]