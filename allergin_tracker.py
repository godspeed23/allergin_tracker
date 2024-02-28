"""
This pulls data regarding the allergin levels for a particular allergin and locale

TODO:
 - currently it only pulls only the required data based on locale and allergin;
    this can be extended to pull all the data for the various locales & all allergins

"""

from urllib.request import Request, urlopen
from io import BytesIO
from datetime import date, timedelta

from pypdf import PdfWriter, PdfReader


def get_pdf_content(pdf_file):
    """return the content byte info of a pdf file"""
    pdf_content = PdfWriter()
    if pdf_file.startswith("http"):
        raw_file = urlopen(Request(pdf_file)).read()
    else:
        with open(pdf_file, "rb") as pdf_file_obj:
            raw_file = pdf_file_obj.read()
    memory_file = BytesIO(raw_file)
    pdf_file = PdfReader(memory_file)
    for page_num in range(pdf_file._get_num_pages()):
        current_page = pdf_file._get_page(page_num)
        pdf_content.add_page(current_page)

    return pdf_content


def get_pdf_text(pdf_file):
    """return list of text for text of each page in file"""
    pdf_content = get_pdf_content(pdf_file)
    pdf_text = []
    for page in pdf_content.pages:
        pdf_text.append(page.extract_text())
    return pdf_text


def get_pollen_grade(text, locality="BARCELONA", allergin="Plàtan"):
    """reads the text from the pdf to grab the level of the allergin for a locality"""
    locale_not_reached = True
    search_ended = False
    for line in text.split("\n"):
        if line.lower().endswith(locality.lower()):
            locale_not_reached = False
            continue
        if locale_not_reached or search_ended:  # and not search_ended:
            continue
        if line.lstrip().startswith(allergin):
            data = line.replace(f" {allergin} ", "")
            allergin_level = data[0]
            allergin_change = data[1]
        if "Cladosporium" in line:
            search_ended = True
    return (allergin_level, allergin_change)


def create_file_list(current_year_start, current_year_end, past_years=None):
    """return a list of files to be looked up for the allery data,
    based on the specified date ranges
    """
    current_year = current_year_start.year
    if past_years is None:
        years = [current_year]
    else:
        print(past_years + [current_year])
        years = sorted(set(past_years + [current_year]))
    week_numbers = []
    for n in range((current_year_end - current_year_start).days + 1):
        week_numbers.append((current_year_start + timedelta(days=n)).isocalendar().week)
    week_numbers = sorted(set(week_numbers))
    file_list = [f"XAC-{wk:02}-{yr}.pdf" for yr in years for wk in week_numbers]
    print(file_list)
    # week_numbers = [date().isocalendar().week]


if __name__ == "__main__":

    # BASE_URL = "https://aerobiologia.cat/pia/general/pdf/nivells"
    # FILE = "XAC-11-2023.pdf" # XAC-09-2023.pdf
    # URL = "/".join([BASE_URL, FILE])

    # text = get_pdf_text(URL)[0]
    # allergy_status = get_pollen_grade(text, locality="Barcelona", allergin="Plàtan")
    # print(allergy_status)

    create_file_list(
        date(2024, 2, 15), date(2024, 4, 30), [2019, 2020, 2021, 2022, 2023]
    )
