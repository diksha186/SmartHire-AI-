"""
Skill dictionary used by the NLP layer.

Key   = canonical skill name stored in the database
Value = list of aliases / spellings that may appear in a resume
Keeping this in one file makes the AI layer easy to extend later.
"""

SKILL_ALIASES: dict[str, list[str]] = {
    # Programming languages
    "python": ["python", "python3"],
    "java": ["java", "core java"],
    "javascript": ["javascript", "js", "es6"],
    "typescript": ["typescript", "ts"],
    "c": ["c programming", "c language"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "c sharp"],
    "php": ["php"],
    "kotlin": ["kotlin"],
    "swift": ["swift"],
    "r": ["r programming"],
    # Web / frameworks
    "react": ["react", "react.js", "reactjs"],
    "angular": ["angular", "angularjs"],
    "vue": ["vue", "vue.js", "vuejs"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "bootstrap": ["bootstrap"],
    "tailwind": ["tailwind", "tailwindcss"],
    "fastapi": ["fastapi", "fast api"],
    "django": ["django"],
    "flask": ["flask"],
    "spring boot": ["spring boot", "springboot"],
    "node.js": ["node.js", "nodejs", "node js"],
    "rest api": ["rest api", "restful", "rest apis"],
    # Data / databases
    "sql": ["sql"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo"],
    "sqlite": ["sqlite"],
    "oracle": ["oracle db", "oracle database"],
    "excel": ["excel", "ms excel", "microsoft excel"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "data analysis": ["data analysis", "data analytics"],
    # AI / ML
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "nlp": ["nlp", "natural language processing"],
    "spacy": ["spacy"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    # DevOps / tools
    "git": ["git"],
    "github": ["github"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],
    "linux": ["linux", "ubuntu"],
    "postman": ["postman"],
    "jenkins": ["jenkins"],
    # Soft / general
    "communication": ["communication skills", "communication"],
    "teamwork": ["teamwork", "team player"],
    "problem solving": ["problem solving", "problem-solving"],
    "leadership": ["leadership"],
    "project management": ["project management"],
    "agile": ["agile", "scrum"],
    "testing": ["unit testing", "software testing", "manual testing"],
}

# Education levels ranked from lowest to highest (used for the education score).
EDUCATION_LEVELS: list[tuple[str, int, list[str]]] = [
    ("High School", 1, ["high school", "12th", "intermediate", "senior secondary"]),
    ("Diploma", 2, ["diploma", "polytechnic"]),
    ("Bachelor", 3, ["bachelor", "b.tech", "btech", "b.e", "bca", "b.sc", "bsc",
                     "b.com", "bcom", "ba ", "graduation", "undergraduate"]),
    ("Master", 4, ["master", "m.tech", "mtech", "mca", "m.sc", "msc", "mba",
                   "m.com", "post graduate", "postgraduate"]),
    ("PhD", 5, ["ph.d", "phd", "doctorate"]),
]

# Words that show a resume is achievement-oriented rather than a bare list.
QUALITY_KEYWORDS: list[str] = [
    "project", "internship", "experience", "developed", "designed", "implemented",
    "built", "managed", "improved", "optimized", "achieved", "certification",
    "certified", "award", "responsible", "collaborated", "deployed", "analysed",
    "analyzed", "increased", "reduced", "team", "research", "published",
]

# Sections a strong resume usually contains.
EXPECTED_SECTIONS: list[str] = [
    "education", "experience", "skills", "projects", "certification", "summary",
]
