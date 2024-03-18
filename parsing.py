import fitz
from unidecode import unidecode
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import spacy
from nltk.corpus import stopwords
from collections import Counter
from nltk import word_tokenize
from nltk.util import ngrams
import csv

extracted_information = {}

# nltk.download("averaged_perceptron_tagger")
nlp = spacy.load("en_core_web_sm")
nlp__ = spacy.load("en_core_web_trf")
# nltk.download("stopwords")
# nltk.download("punkt")

formatted_phone_numbers = set()
formatted_Emails = set()

# phone_numbers__ = []
entity = [
    "Projects",
    "PROJECTS",
    "Skills & Interests",
    "Certifications",
    "Positions of Responsibility",
    "Achievements",
    "Project",
    "PROJECT",
    "EXPERIENCE",
    "Technical Skills",
    "Honours and Awards",
    "Algorithmic Competitions/Achievements",
    "Work Experience",
    "Education",
    "WORK EXPERIENCE",
    "EDUCATION",
    "Experience",
    "CERTIFICATIONS",
    "SKILLS",
    "PROFESSIONAL SUMMARY",
    "Skills",
    "POSITION OF RESPONSIBILITY",
    "TECHNICAL SKILLS",
    "Key courses taken",
    "ACHIEVEMENTS",
    "Technical Skills and Interests",
    "Skills",
    "COURSEWORK",
    "CERTIFICATIONS/ACHIEVEMENTS",
]


class Parse_Resume:
    def __init__(self, file):
        self.file = file

    def Block_converter(self):
        output = []
        with fitz.open(self.file) as doc:
            for page in doc:
                output += page.get_text("blocks")
            # text = page.get_text("blocks")

        # doc = fitz.open(self.file)
        # for page in doc:

        clean_output = []
        for i in range(0, len(output)):
            plain_text = unidecode(output[i][4])
            clean_output.append(plain_text)
        return clean_output

    def extract_emails(self, text):
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(pattern, text)
        for i in range(0, len(emails)):
            formatted_Emails.add(emails[i])
        return emails

    def extract_links(self, text):
        pattern = r"(https?://\S+)"
        links = re.findall(pattern, text)
        return links

    def extract_linkedins(self, strings):
        linkedin_strings = []
        pattern = re.compile(r".linkedin.com.")
        for string in strings:
            if pattern.match(string):
                linkedin_strings.append(string)
        return linkedin_strings

    def create_dictionary_from_text(self, lines):
        dictionary = {}
        current_heading = None

        for line in lines:
            if line.strip():
                words = line.strip().split()

                if len(words) == 1:
                    current_heading = words[0]
                    dictionary[current_heading] = []

                else:
                    if current_heading:
                        dictionary[current_heading].append(line.strip())

        return dictionary


def Education(text):
    cgpa_pattern = r"\b\d+\.\d+\b"
    cgpa_matches = re.findall(cgpa_pattern, text)
    # branch_pattern = r"(B\.Tech|Bachelors\s*of\s*Technology)\s*in\s*([^\n]+?(?=\s*(Engineering|Technology|$)))"
    # branch_match = re.search(branch_pattern, text)
    # branch = branch_match.group(2).strip() if branch_match else None
    year_pattern = r"(\d{4})\s*-\s*(\d{4})"
    year_match = re.search(year_pattern, text)

    start_year = year_match.group(1).strip() if year_match else None
    end_year = year_match.group(2).strip() if year_match else None

    college_pattern = r"\*(.*?)\d{4}"  # Matches any text between '*' and a 4-digit year
    branch_pattern = r"B\.Tech\s+in\s+([A-Za-z\s]+(?:Engineering|Technology))\b"

    # Extract college name
    college_match = re.search(college_pattern, text)
    college_name = college_match.group(1).strip() if college_match else None

    # Extract branch name
    branch_match = re.search(branch_pattern, text)
    branch_name = branch_match.group(1).strip() if branch_match else None

    # doc = nlp(text)
    # college_names_ = [entity.text for entity in doc.ents if entity.label_ == "ORG"]
    # print("College Names:", college_names_)

    if end_year:
        batch = end_year
    else:
        batch = None

    # print(text)
    extracted_information["Education"] = {college_name, branch_name, batch, cgpa_matches[0]}
    print("College: ", college_name)
    # print("College: ", college_names_[1])
    # print("College: ", college_names_[2])
    print("Branch:", branch_name)
    print("Batch:", batch)
    # print("CGPA:", cgpa_matches)

    if cgpa_matches is not None:
        print("CGPA:", cgpa_matches[0])


def extract_certifications(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words("english"))
    tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
    doc = nlp(" ".join(tokens))
    certifications = []
    patterns = [
        r"\bcertified\b",
        r"\bcertification\b",
        r"\bqualified\b",
        r"\baccredited\b",
        r"\blicense\b",
        r"\bdiploma\b",
    ]

    for token in doc:
        for pattern in patterns:
            if re.search(pattern, token.text):

                start_index = max(0, token.i - 3)
                end_index = min(token.i + 3, len(doc))
                context = doc[start_index : end_index + 1]
                certification_name = " ".join([t.text for t in context])
                certifications.append(certification_name)

    return list(set(certifications))


def Experience(text):
    experiences = re.findall(
        r"\*([\w\s]+) ([A-Z][a-z]+ \d{4}) - ([A-Z][a-z]+ \d{4})", text
    )
    return experiences


def extract_coursework(text):
    tokens = nltk.word_tokenize(text)
    tagged_tokens = nltk.pos_tag(tokens)
    course_phrases = []
    current_course = []

    for word, tag in tagged_tokens:
        if tag.startswith("NN"):
            current_course.append(word)
        elif current_course:
            course_phrases.append(" ".join(current_course))
            current_course = []

    if current_course:
        course_phrases.append(" ".join(current_course))

    # print(course_phrases)
    return course_phrases


def skills_(text):
    tokens = nltk.word_tokenize(text)
    tagged_tokens = nltk.pos_tag(tokens)
    skill_phrases = []
    current_skill = []

    for word, tag in tagged_tokens:
        if tag.startswith("NN"):
            current_skill.append(word)
        elif current_skill:
            skill_phrases.append(" ".join(current_skill))
            current_skill = []

    if current_skill:
        skill_phrases.append(" ".join(current_skill))

    return skill_phrases


# def address(text):
#     doc = nlp(text)
#     addresses = [entity.text for entity in doc.ents if entity.label_ == "GPE"]
#     print("Addresses:", addresses)


def extract_keywords(text, n=5):
    doc = nlp(text)
    entity_counts = Counter()

    for ent in doc.ents:
        if ent.label_ in ["ORG", "WORK_OF_ART", "EVENT", "PRODUCT"]:

            entity_counts[ent.text] += 1

    top_entities = entity_counts.most_common(n)

    return top_entities


# def extract_achievements(text):
#     # Define regular expression pattern for extracting achievements
#     achievement_pattern = r"\*(.*?)\n(?=\*)"  # Matches any text between '*' and the next '*' indicating the start of a new section
#     # Extract achievements
#     achievements = re.findall(achievement_pattern, text, re.DOTALL)
#     cleaned_achievements = [
#         achievement.strip()
#         for achievement in achievements
#         if "Achievements" not in achievement
#     ]

#     return cleaned_achievements


resume = Parse_Resume("resume.pdf")
cleanoutput = resume.Block_converter()
# print(cleanoutput)


for i in range(0, len(cleanoutput)):

    temp_ = str(cleanoutput[i])
    # print(temp_)
    clean_string = " ".join(temp_.split())
    clean_string_ = clean_string.replace(":", "")
    cleanoutput[i] = clean_string_


for i in range(0, len(cleanoutput)):
    temp_ = str(cleanoutput[i])
    if temp_ in entity:
        # print("hit")
        new_temp = " :"
        new_temp += cleanoutput[i]
        new_temp += ": "
        new_temp.lower()
        cleanoutput[i] = new_temp

    else:
        cleanoutput[i] += "."


final_text = ""
for i in range(0, len(cleanoutput)):
    print(cleanoutput[i])
    final_text += cleanoutput[i]
    print("\n")


def extract_text(text, entities):
    extracted_text = {}
    for entity in entities:
        pattern = re.compile(r":{}:(.*?)(?=:|$)".format(entity), re.DOTALL)
        match = pattern.search(text)
        if match:
            extracted_text[entity] = match.group(1).strip()
    return extracted_text


extracted_text = extract_text(final_text, entity)


for i in range(0, len(cleanoutput)):
    resume.extract_emails(cleanoutput[i])

phone_number = re.search(r"\+\d{2}-\d{10}", final_text)
phone_number = phone_number.group() if phone_number else None

extracted_information["Phone Number"] = phone_number
extracted_information["emails"] = formatted_Emails

print("Phone No: ", phone_number)
print("Email: ", formatted_Emails)
print("\n")


def process_skills(text):
    return skills_(text)


def process_education(text):
    return Education(text)


def process_experience(text):
    return Experience(text)


def process_certifications(text):
    return extract_certifications(text)


def process_course(text):
    return extract_coursework(text)


def process_achievements(text):
    keywords = extract_keywords(text)
    print("Top 5 Keywords:")
    for keyword, count in keywords:
        print(keyword, "-", count)
    # print("Achie")
    # print(text)
    # achievements = extract_achievements(text)
    # for achievement in achievements:
    #     print(achievement)

def write_to_csv(data_items):
    data_dict = dict(data_items)
    with open('resume_information.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data_dict.keys())
        writer.writeheader()
        writer.writerow(data_dict)

entity_processors = {
    "skills": process_skills,
    "technical skills": process_skills,
    "skills & interests": process_skills,
    "technical skills & interests": process_skills,
    "technical skills and interests": process_skills,
    "skills and interests": process_skills,
    "education": process_education,
    "experience": process_experience,
    "work experience": process_experience,
    "certifications": process_certifications,
    "achievements": process_achievements,
    "honours and awards": process_achievements,
    "algorithmic competitions/achievements": process_achievements,
    "coursework": process_course,
    "certifications/achievements": process_achievements,
}

for entity, text in extracted_text.items():
    print(entity + ":")
    entity_lower = entity.lower()
    if entity_lower in entity_processors:
        result = entity_processors[entity_lower](text)
        if result is not None:
            print(result)
            extracted_information[entity] = result
            print("\n")

write_to_csv(extracted_information.items())