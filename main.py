from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
SBR_WEBDRIVER = 'https://brd-customer-hl_431079b5-zone-arjunsscraper:bwe9i5tg3sry@brd.superproxy.io:9515'
input1 = input("Link:")
parse_description = input("Description:")

def main(website):
    try:
        print("starting")
        options = Options()
        driver = webdriver.Remote(command_executor=SBR_WEBDRIVER, options=options)
        print("maybe")
        driver.get(website)
        html = driver.page_source
        driver.quit()
        return html
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def extract(body):
    soup = BeautifulSoup(body, 'html.parser')
    content = soup.body
    if content:
        return str(content)
    return ""

def clean(body):
    soup = BeautifulSoup(body, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    cleaned = soup.get_text(separator='\n')
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines() if line.strip())
    return cleaned

def split(content, max_length=6000):
    return [content[i: i + max_length] for i in range(0, len(content), max_length)]

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

llm = ChatOpenAI(model_name="gpt-4", temperature=0, openai_api_key=api_key)

def parse(input_chunks, description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = LLMChain(prompt=prompt, llm=llm)
    parsed_content = []
    for i, chunk in enumerate(input_chunks, start=1):
        response = chain.run(dom_content=chunk, parse_description=description)
        print(f"Parsed batch: {i} of {len(input_chunks)}")
        parsed_content.append(response)
    return "\n".join(parsed_content)

result = main(input1)
if result:
    extracted_content = extract(result)
    cleaned_content = clean(extracted_content)
    content_chunks = split(cleaned_content)
    final_output = parse(content_chunks, parse_description)
    print("\nFinal Output:")
    print(final_output)
