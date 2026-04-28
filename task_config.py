TASK_DESCRIPTION = """
Analyze the provided email content and determine if it is a phishing or social engineering attempt. 
Extract the data into a strict JSON format with the following keys:
1. 'is_phishing' (boolean): true if malicious, false if safe.
2. 'threat_vector' (string): MUST be exactly one of: 'malicious_link', 'malicious_attachment', 'urgency_manipulation', or 'none'.
3. 'confidence_score' (integer): 1 to 100 representing how confident you are in the assessment.
"""

EVALUATION_CRITERIA = """
1. The output MUST be a valid JSON.
2. If the email is safe (promotional, legitimate internal communication), 'is_phishing' must be false, and 'threat_vector' MUST be 'none'.
3. 'malicious_link' is for fake login pages or suspicious URLs.
4. 'malicious_attachment' is for unexpected invoices, receipts, or documents.
5. 'urgency_manipulation' is for CEO fraud, gift card requests, or "act immediately" texts with no direct link/attachment.
6. The Judge must penalize the Target Agent if it hallucinates threat vectors outside of the allowed list.
"""

DATASET = [
    {
        "id": 1,
        "input_text": "URGENT: Your PayPal account has been suspended due to unusual activity. Click here [http://paypal-security-update.com/login] to verify your identity within 24 hours or your account will be permanently closed.",
        "expected": '{"is_phishing": true, "threat_vector": "malicious_link", "confidence_score": 99}'
    },
    {
        "id": 2,
        "input_text": "Attached is the overdue invoice #99124 for your recent purchase. Please remit payment immediately to avoid legal action. Best, Accounting.",
        "expected": '{"is_phishing": true, "threat_vector": "malicious_attachment", "confidence_score": 95}'
    },
    {
        "id": 3,
        "input_text": "Hey, it's John from HR. I'm stuck in a meeting and need a huge favor. Can you buy $500 in Apple gift cards for a client presentation right now? I'll reimburse you later today. Please hurry!",
        "expected": '{"is_phishing": true, "threat_vector": "urgency_manipulation", "confidence_score": 98}'
    },
    {
        "id": 4,
        "input_text": "Hi Team, just a reminder that the Q3 All-Hands meeting is scheduled for next Thursday at 2 PM in the main conference room. Pizza will be provided! Cheers, Sarah.",
        "expected": '{"is_phishing": false, "threat_vector": "none", "confidence_score": 99}'
    },
    {
        "id": 5,
        "input_text": "Your Amazon order #112-4412-991 has shipped! Track your package securely at https://amazon.com/orders/tracking. Thank you for shopping with us.",
        "expected": '{"is_phishing": false, "threat_vector": "none", "confidence_score": 95}'
    },
    # {
    #     "id": 6,
    #     "input_text": "Hey Mark, can you review the attached draft for the upcoming marketing campaign? Let me know your thoughts by Friday.",
    #     "expected": '{"is_phishing": false, "threat_vector": "none", "confidence_score": 90}'
    # },
    # {
    #     "id": 7,
    #     "input_text": "IT ALERT: We are migrating to a new Exchange server tonight at 11 PM. You may experience a 10-minute downtime. No action is required on your part. Do not share your password.",
    #     "expected": '{"is_phishing": false, "threat_vector": "none", "confidence_score": 95}'
    # },
    # {
    #     "id": 8,
    #     "input_text": "IT ALERT: Your mailbox quota is full. To prevent incoming emails from bouncing, you must upgrade your quota immediately by logging in here: http://webmail-upgrade-portal.info/login.",
    #     "expected": '{"is_phishing": true, "threat_vector": "malicious_link", "confidence_score": 98}'
    # },
    # {
    #     "id": 9,
    #     "input_text": "Did you see this picture of you from the weekend party?? LOL download it here: photo_weekend.exe",
    #     "expected": '{"is_phishing": true, "threat_vector": "malicious_attachment", "confidence_score": 99}'
    # },
    # {
    #     "id": 10,
    #     "input_text": "Don't miss out on our Black Friday deals! Get 50% off all shoes. Click here to browse our catalog. Unsubscribe at the bottom of this email.",
    #     "expected": '{"is_phishing": false, "threat_vector": "none", "confidence_score": 98}'
    # },
    # {
    #     "id": 11,
    #     "input_text": "Microsoft Security: A sign-in attempt from Russia was blocked. If this wasn't you, secure your account by changing your password immediately at https://account.microsoft-secure-auth.com.",
    #     "expected": '{"is_phishing": true, "threat_vector": "malicious_link", "confidence_score": 96}'
    # }
]