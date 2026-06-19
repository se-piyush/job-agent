"""
profile.py — Piyush Sharma's master experience bank.
All agents pull from here. Update this file when experience changes.
"""

PERSONAL = {
    "name": "Piyush Sharma",
    "location": "India",
    "phone": "+91 9873302882",
    "linkedin": "https://www.linkedin.com/in/se-piyusharma/",
    "linkedin_display": "linkedin.com/in/se-piyusharma",
    "github": "https://github.com/se-piyush",
    "github_display": "github.com/se-piyush",
}

EDUCATION = {
    "degree": "Bachelor of Technology (B.Tech) in Information Technology",
    "university": "Guru Gobind Singh Indraprastha University, Delhi",
    "years": "2012 - 2016",
}

EXPERIENCE = [
    {
        "company": "Abillion",
        "via": None,
        "title": "Senior Software Engineer",
        "start": "Jul 2025",
        "end": "Nov 2025",
        "stack": ["NestJS", "GraphQL", "MongoDB", "Redis", "TypeScript", "React Native", "GitHub Copilot"],
        "bullets": [
            "Improved marketplace API performance for 200K+ MAU by migrating REST to GraphQL (NestJS, TypeScript, MongoDB) with Redis caching and strategic indexing, eliminating over-fetching and reducing p95 response times.",
            "Reduced duplicate pagination code across services to zero by building connection-based pagination for infinite-scroll feeds and abstracting it into a shared module adopted platform-wide.",
            "Drove a 10% increase in paid brand claims within a single quarter by leading a pricing migration across 3 subscription tiers that cut brand costs by 15%.",
            "Leveraged GitHub Copilot in agentic mode with Claude Sonnet to accelerate feature delivery and maintain high code quality in a fast-moving product environment.",
        ],
    },
    {
        "company": "ForteGlobal",
        "via": "Teamified",
        "title": "Senior Software Engineer",
        "start": "Nov 2024",
        "end": "Jul 2025",
        "stack": ["Node.js", "TypeScript", "Express", "PostgreSQL", "AWS RDS", "AWS Cognito", "Stripe", "GitHub Actions", "CloudWatch", "Slack SDK"],
        "bullets": [
            "Eliminated all manual data-entry operations by building a secure bulk upload system (Excel/forms → PostgreSQL on AWS RDS) using Node.js, TypeScript, and Express, enabling thousands of records to be processed per run.",
            "Automated $50K/month in contractor payments with zero manual invoicing by integrating Stripe and implementing RBAC (4 roles) with AWS Cognito auth, shipped end-to-end via CI/CD on GitHub Actions.",
            "Cut mean time to detect production incidents by building a configurable observability pipeline that routes severity-filtered errors to Slack with full audit logs retained in CloudWatch.",
            "Built backend APIs from scratch replacing 100% of manual workflows with automated digital operations.",
        ],
    },
    {
        "company": "Gomist",
        "via": "Teamified",
        "title": "Senior Software Engineer",
        "start": "Mar 2024",
        "end": "Nov 2024",
        "stack": ["Node.js", "TypeScript", "AWS Lambda", "DynamoDB", "Firebase", "Onfido", "Razorpay", "Terraform", "GitHub Actions", "S3", "CloudFront"],
        "bullets": [
            "Unblocked SIM purchases and cash transfers for a $30K+ per-account fintech platform by architecting a KYC pipeline (Onfido) with Firebase OTP auth, delivering on schedule for go-live.",
            "Achieved zero-touch deployments across 3 environments by building a fully serverless backend (AWS Lambda, TypeScript, DynamoDB) and managing all IaC end-to-end with Terraform, S3, CloudFront, and GitHub Actions.",
            "Led a team of 4 (2 backend, 2 frontend) to deliver a complete fintech product for international students.",
            "Built serverless backend on AWS Lambda (TypeScript) with DynamoDB and Razorpay handling $30K+ per student account.",
        ],
    },
    {
        "company": "Lifebit",
        "via": None,
        "title": "Senior Software Engineer (Contract)",
        "start": "Jun 2022",
        "end": "Jan 2024",
        "stack": ["Node.js", "AWS Lambda", "EC2", "S3", "Azure AD", "SSO"],
        "bullets": [
            "Made 100% of file downloads auth-gated by replacing vulnerable public S3 pre-signed URLs with a private server-side proxy API that validates requester identity before streaming — closing an unauthenticated access exploit.",
            "Reduced AWS infrastructure costs by 30% by migrating low-frequency services from EC2 to serverless (AWS Lambda).",
            "Enabled self-serve enterprise access management via Azure AD SSO with group-based permissions through Active Directory groups.",
        ],
    },
    {
        "company": "OnceHub",
        "via": None,
        "title": "Senior Software Engineer (2021-2022) | SDE (2017-2021)",
        "start": "Jan 2017",
        "end": "Jun 2022",
        "stack": ["Node.js", "TypeScript", "Apache Kafka", "PostgreSQL", "Kubernetes", "Helm", "Azure AKS", "ORY Hydra", "JWT", "GitHub Actions"],
        "bullets": [
            "Eliminated data loss at 1,000+ req/s peak by replacing a crashing webhook processor with a scalable event-driven pipeline — Apache Kafka publishing to batch consumers that pre-aggregate and persist booking events asynchronously.",
            "Cut release cycle time by 90% by migrating a monolith to microservices, building an internal Node.js bootstrap library, and deploying all services on Kubernetes (Azure AKS) with Helm charts.",
            "Reduced dashboard load from 8s to 100ms via server-side pagination on booking data, and unified auth across all products with an in-house OAuth 2.0 server (ORY Hydra, JWT, PostgreSQL).",
            "Blocked brute-force card enumeration attacks by implementing a configurable rate limiter on the payment iframe.",
            "Implemented automated payment system with dynamic pricing, eliminating all manual billing processes.",
            "Led a team of 2 backend developers.",
        ],
    },
]

SKILLS = {
    "Languages": ["Node.js", "TypeScript", "JavaScript"],
    "APIs & Patterns": ["REST APIs", "BFF", "GraphQL", "Event-Driven Architecture", "Microservices", "Contract-First Design"],
    "Databases": ["PostgreSQL (RDS)", "MongoDB (DocumentDB)", "DynamoDB", "Redis", "Data Modeling", "Indexing", "Migration"],
    "Messaging": ["Apache Kafka", "AWS SQS", "Webhooks", "Event Streaming"],
    "Cloud (AWS)": ["Lambda", "RDS", "DocumentDB", "DynamoDB", "S3", "Cognito", "CloudWatch", "EC2", "CloudFront", "Terraform", "Serverless"],
    "Security": ["OAuth 2.0", "JWT", "RBAC", "IAM", "Azure AD SSO", "API Security", "Rate Limiting"],
    "DevOps & Testing": ["GitHub Actions", "CI/CD", "Kubernetes", "Helm", "Docker", "Unit/Integration/Migration Testing"],
    "AI Dev Tools": ["GitHub Copilot (agentic mode)", "Claude Sonnet", "LLM-assisted development"],
}
