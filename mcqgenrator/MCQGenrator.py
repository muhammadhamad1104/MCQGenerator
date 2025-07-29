# import os
# import json
# import traceback
# import pandas as pd
# from dotenv import load_dotenv
# from mcqgenrator.utils import read_file,get_table_data
# from mcqgenrator.logger import logging

# #imporing necessary packages packages from langchain
# # from langchain.chat_models import ChatOpenAI
# from langchain_community.chat_models import ChatOpenAI
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnableLambda
# from langchain.prompts import PromptTemplate
# # from langchain.chains import LLMChain
# # from langchain.chains import SequentialChain
# # from langchain_core.runnables import RunnableSequence

# from langchain_google_genai import ChatGoogleGenerativeAI


# # Load environment variables from the .env file
# load_dotenv()

# # Access the environment variables just like you would with os.environ
# # key = os.getenv("OPENAI_API_KEY")

# print("Value of MY_VARIABLE:", key)

# # llm = ChatOpenAI(openai_api_key=key,model_name="gpt-3.5-turbo", temperature=0.3)

# template="""
# Text:{text}
# You are an expert MCQ maker. Given the above text, it is your job to \
# create a quiz  of {number} multiple choice questions for {subject} students in {tone} tone. 
# Make sure the questions are not repeated and check all the questions to be conforming the text as well.
# Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
# Ensure to make {number} MCQs
# ### RESPONSE_JSON
# {response_json}

# """

# quiz_generation_prompt = PromptTemplate(
#     input_variables=["text", "number", "subject", "tone", "response_json"],
#     template=template)



# # quiz_chain=LLMChain(llm=llm, prompt=quiz_generation_prompt, output_key="quiz", verbose=True)

# template="""
# You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
# You need to evaluate the complexity of teh question and give a complete analysis of the quiz if the students
# will be able to unserstand the questions and answer them. Only use at max 50 words for complexity analysis. 
# if the quiz is not at par with the cognitive and analytical abilities of the students,\
# update tech quiz questions which needs to be changed  and change the tone such that it perfectly fits the student abilities
# Quiz_MCQs:
# {quiz}

# Check from an expert English Writer of the above quiz:
# """

# quiz_evaluation_prompt=PromptTemplate(input_variables=["subject", "quiz"], template=template)

# # review_chain=LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)



# # This is an Overall Chain where we run the two chains in Sequence
# # generate_evaluate_chain=SequentialChain(chains=[quiz_chain, review_chain], input_variables=["text", "number", "subject", "tone", "response_json"],output_variables=["quiz", "review"], verbose=True,)


# 
import os
import json
from dotenv import load_dotenv
from mcqgenrator.logger import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableMap
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()
key = os.getenv("GEMINI_API_KEY")
print("Value of GEMINI_API_KEY:", key)

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=key, temperature=0.7)

# Prompt for quiz generation
quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template="""
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to 
create a quiz of {number} multiple choice questions for {subject} students in {tone} tone.
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like RESPONSE_JSON below and use it as a guide.
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}
"""
)

quiz_chain = quiz_generation_prompt | llm | StrOutputParser()

# Prompt for quiz evaluation
quiz_evaluation_prompt = PromptTemplate(
    input_variables=["subject", "quiz"],
    template="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.
You need to evaluate the complexity of the question and give a complete analysis of the quiz if the students
will be able to understand the questions and answer them. Only use at max 50 words for complexity analysis.
If the quiz is not at par with the cognitive and analytical abilities of the students,
update the quiz questions which need to be changed and change the tone such that it perfectly fits the student abilities.
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""
)

review_chain = quiz_evaluation_prompt | llm | StrOutputParser()

# Build combined chain
def build_chain(user_subject):
    return RunnableMap({
        "quiz": quiz_chain,
        "review": quiz_chain | RunnableLambda(lambda quiz: {"quiz": quiz, "subject": user_subject}) | review_chain
    })
