from functools import wraps
from datetime import datetime

MONTHS = {"Январь": "January",
          "Февраль": "February",
          "Март": "March",
          "Апрель": "April",
          "Май": "May",
          "Июнь": "June",
          "Июль": "July",
          "Август": "August",
          "Сентябрь": "September",
          "Октябрь": "October",
          "Ноябрь": "November",
          "Декабрь": "December"}


def num_pages(page):
    """
    :param bs4.BeautifulSoup page: resumes search page
    :return: int
    """
    num = page.find("div", {"data-qa": "pager-block"})

    if not num:
        return 1

    num = num.findAll("a", {"class": "bloko-button"})

    if not num:
        return 1

    return int(num[-2].getText())


def resume_hashes(page):
    """
    :param bs4.BeautifulSoup page: resumes search page
    :return: list
    """
    hashes = []
    page = page.find("div", {"data-qa": "resume-serp__results-search"})

    if page is not None:
        hashes = page.findAll("div", {"data-qa": "resume-serp__resume"})
        hashes = [item.find("a")["href"][8:46] for item in hashes]

    return hashes


def header(page):
    """
    :param bs4.BeautifulSoup page: resume page
    :return: bs4.Tag
    """
    return page.find("div", {"class": "resume-header-block"})


def get_optional_text(find_optional_element):
    @wraps(find_optional_element)
    def wrapper(page):
        """
        :param bs4.Tag element: element from resume
        :return: str or None
        """
        optional_element = find_optional_element(page)
        return None if optional_element is None else optional_element.getText()
    return wrapper


@get_optional_text
def birth_date(page):
    """
    :param bs4.BeautifulSoup page: resume page
    :return: str or None
    """
    return page.find("span", {"data-qa": "resume-personal-birthday"})


@get_optional_text
def gender(page):
    """
    :param bs4.BeautifulSoup page: resume page
    :return: str or None
    """
    return page.find("span", {"data-qa": "resume-personal-gender"})


@get_optional_text
def area(page):
    """
    :param bs4.BeautifulSoup page: resume page
    :return: str or None
    """
    return page.find("span", {"data-qa": "resume-personal-address"})


def position(page):
    """
    :param bs4.BeautifulSoup page: resume page
    :return: bs4.Tag
    """
    return page.find("div", {"class": "resume-block", "data-qa": "resume-block-position"})


def position_title(position_block):
    """
    :param bs4.Tag position_block: position block
    :return: str
    """
    title = position_block.find("span", {"class": "resume-block__title-text",
                                         "data-qa": "resume-block-title-position"})

    return title.getText()


def position_specializations(position_block):
    """
    :param bs4.Tag position_block: position block
    :return: list
    """
    position_block = position_block.find("div", {"class": "bloko-gap bloko-gap_bottom"})

    profarea_name = position_block.find("span", {"data-qa": "resume-block-specialization-category"})
    profarea_name = profarea_name.getText()

    profarea_specializations = position_block.find("ul")
    profarea_specializations = profarea_specializations.findAll("li", {"class": "resume-block__specialization",
                                                                       "data-qa": "resume-block-position-specialization"})

    profarea_specializations = [item.getText() for item in profarea_specializations]
    profarea_specializations = [{"name": specialization_name, "profarea_name": profarea_name}
                                for specialization_name in profarea_specializations]

    return profarea_specializations


def position_salary(position_block):
    """
    :param bs4.Tag position_block: position block
    :return: dict
    """
    salary = position_block.find("span", {"class": "resume-block__salary resume-block__title-text_salary",
                                          "data-qa": "resume-block-salary"})
    amount = None
    currency = None
    if salary is not None:
        salary = salary.getText().replace('\u2009', '').replace('\xa0', ' ').strip().split()
        amount = int(salary[0])
        currency = ' '.join(salary[1:])

    salary = {"amount": amount,
              "currency": currency}

    return salary


def education(page):
    """
    :param bs4.BeautifulSoup page: resume page
    :return: bs4.Tag
    """
    return page.find("div", {"class": "resume-block", "data-qa": "resume-block-education"})


def education_level(education_block):
    """
    :param bs4.Tag education_block: education block
    :return: str
    """
    if education_block is not None:
        return education_block.find("span", {"class": "resume-block__title-text resume-block__title-text_sub"}) \
                              .getText()

    return "Образования нет"


def educations(education_block):
    """
    :param bs4.Tag education_block: education block
    :return: list
    """
    page_educations = []
    if education_block is not None:
        education_block = education_block.find("div", {"class": "resume-block-item-gap"}) \
                                         .find("div", {"class": "bloko-columns-row"})

        for education_item in education_block.findAll("div", {"class": "resume-block-item-gap"}):
            year = education_item.find("div", {"class": "bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2"}) \
                                 .getText()

            item_name = education_item.find("div", {"data-qa": "resume-block-education-name"}) \
                                      .getText()

            item_organization = education_item.find("div", {"data-qa": "resume-block-education-organization"})
            if item_organization is not None:
                item_organization = item_organization.getText()

            page_educations.append(
                {"year": int(year),
                 "name": item_name,
                 "organization": item_organization}
            )

    return page_educations


def languages(page):
    """
    :param bs4.BeautifulSoup page: resume page
    :return: list
    """
    page_languages = []
    page = page.find("div", {"class": "resume-block", "data-qa": "resume-block-languages"})

    if page is not None:
        for language in page.findAll("p", {"data-qa": "resume-block-language-item"}):
            language = language.getText().split(" — ")

            level = ' - '.join(language[1:])
            language = language[0]

            page_languages.append({"name": language,
                                   "level": level})

    return page_languages


def date(date, format="%d-%m-%Y"):
    """
    :param date str: date in format "Month (russian) Year"
    :param format str: desired data format
    :return: str
    """
    if date in ["по настоящее время", "currently"]:
        return None

    month, year = date.split()

    if month in MONTHS:
        month = MONTHS[month]

    date = f"{month} {year}"
    date = datetime.strptime(date, "%B %Y").strftime(format)

    return date


def experiences(page, format="%d-%m-%Y"):
    """
    :param bs4.BeautifulSoup page: resume page
    :param format str: desired data format
    :return: list
    """
    #print("in experience")

    page_experiences = []
    page = page.find("div", {"class": "resume-block", "data-qa": "resume-block-experience"})

    if page is not None:
        page = page.find("div", {"class": "resume-block-item-gap"})
        for experience_item in page.findAll("div", {"class": "resume-block-item-gap"}):
            time_interval = experience_item.find("div", {"class": "bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2"})
            time_interval.div.extract()

            start, end = time_interval.getText().replace("\xa0", " ").split(' — ')
            
            #<div class="bloko-text-emphasis"><span>PAO Rosbank Societe Generale Group</span></div>
            company = experience_item.find("div",  {"class": "bloko-text-emphasis"})
            company = "" if company is None else company.getText()
            #print(company)

            #<div data-qa="resume-block-experience-position" class="bloko-text-emphasis"><span></span><span class="highlighted">IT</span><span> Support Officer</span></div>
            #item_position = experience_item.find("div",  {"class": "resume-block__sub-title", "data-qa": "resume-block-experience-position"})
            item_position = experience_item.find("div",  {"class": "bloko-text-emphasis", "data-qa": "resume-block-experience-position"})
            item_position = "" if item_position is None else item_position.getText()
            #print(f"item = {item_position}")

            item_description = experience_item.find("div", {"data-qa": "resume-block-experience-description"})
            description_child = item_description.findChild()
            item_description = item_description.getText() if description_child is None else str(description_child)
            

            page_experiences.append(
                {"start": date(start, format=format),
                 "end": date(end, format=format),
                 "company": company,
                 "position": item_position,
                 "description": item_description}
            )

    return page_experiences



def certificates(page):#, format="%d-%m-%Y"):
    """
    :param bs4.BeautifulSoup page: resume page
    :param format str: desired data format
    :re: list
    
    """
    #print("1")
    page_dop = []

    #<div data-qa="resume-block-additional-education" class="resume-block"><div class="bloko-columns-row"><div class="bloko-column bloko-column_xs-4 bloko-column_s-8 bloko-column_m-9 bloko-column_l-12"><div class="resume-block-container"><h2 data-qa="bloko-header-2" class="bloko-header-2 bloko-header-2_lite"><span class="resume-block__title-text resume-block__title-text_sub">Повышение квалификации, курсы</span><a data-qa="resume-block-additional-education-edit" class="resume-block-edit resume-block-edit_capitalize" href="/applicant/resumes/edit/education?resume=fca5698aff08aa635d0039ed1f447631434632&amp;field=additionalEducation">редактировать</a></h2></div></div></div><div class="resume-block-item-gap"><div class="bloko-columns-row"><div class="resume-block-item-gap"><div class="bloko-columns-row"><div class="bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2">2004</div><div class="bloko-column bloko-column_xs-4 bloko-column_s-6 bloko-column_m-7 bloko-column_l-10"><div class="resume-block-container" data-qa="resume-block-education-item"><div data-qa="resume-block-education-name" class="bloko-text-emphasis"><span>MIPT</span></div><div data-qa="resume-block-education-organization"><span>Coursera</span><span>, </span><span>DataScientist</span></div></div></div></div></div></div></div></div>
    page = page.find("div", {"class": "resume-block", "data-qa": "resume-block-additional-education"})

    if page is not None:
        #print("1")
        page = page.find("div", {"class": "resume-block-item-gap"})
        #print("1")
        for item in page.findAll("div", {"class": "resume-block-item-gap"}):

            #print("1")    
            #<div class="bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2">2003</div>
            year = item.find("div", {"class": "bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2"})
            #print(year)
            year.extract()
            year_str = year.getText()
            #print(year_str)
            
            #<div data-qa="resume-block-education-name" class="bloko-text-emphasis"><span>Coursera</span></div>
            company = item.find("div",  {"class": "bloko-text-emphasis", "data-qa": "resume-block-education-name"})
            company = "" if company is None else company.getText()
            #print(company)



            #<div data-qa="resume-block-education-organization"><span>Coursera</span><span>, </span><span>DataScientist</span></div>
            org_spec = item.find("div", {"data-qa":"resume-block-education-organization"})
            org_spec = "" if org_spec is None else org_spec.getText()
            #print(specialization)
            org, spec = org_spec.strip().split(",")


            #<div data-qa="resume-block-education-organization"><!-- --><!-- --><span>Coursera</span><span>, </span><span>DataScientist</span></div>
            #<span>Coursera</span>
            #item_description = experience_item.find("div", {"data-qa": "resume-block-experience-description"})
            #description_child = item_description.findChild()
            #item_description = item_description.getText() if description_child is None else str(description_child)

            page_dop.append(
                {"year" : year_str,
                 "institution" : company,
                 "organization" : org,
                 "specialization" : spec

                }
            )

    return page_dop

def skill_set(page):
    """
    :param bs4.BeautifulSoup page: resume page
    :return: list
    """
    page = page.find("div", {"data-qa": "skills-table", "class": "resume-block"})

    page_skill_set = []
    if page is not None:
        page_skill_set = page.findAll("div", {"class": "bloko-tag bloko-tag_inline bloko-tag_countable",
                                              "data-qa": "bloko-tag bloko-tag_inline"})
        page_skill_set = [skill.getText() for skill in page_skill_set]

    return page_skill_set


def skills(page):
    """
    :param bs4.BeautifulSoup page: resume page
    :return: str
    """
    page = page.find("div", {"data-qa": "resume-block-skills-content"})

    page_skills = ""
    if page is not None:
        skills_child = page.findChild()
        page_skills = page.getText() if skills_child is None else str(skills_child)

    return page_skills


def resume(page):
    """
    :param bs4.BeautifulSoup page: resume page
    :return: dict
    """
    #print("***********************")
    page = page.find("div", {"id": "HH-React-Root"})

    resume_position = position(page)
    resume_education = education(page)

    return {
        "birth_date": birth_date(page),
        "gender": gender(page),
        "area": area(page),
        "title": position_title(resume_position),
        "specialization": position_specializations(resume_position),
        "salary": position_salary(resume_position),
        "education_level": education_level(resume_education),
        "education": educations(resume_education),
        "certificates": certificates(page),
        "language": languages(page),
        "experience": experiences(page),
        "skill_set": skill_set(page),
        "skills": skills(page)
    }

    return resume
