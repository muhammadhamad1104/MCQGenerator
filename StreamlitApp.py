import os
import json
import traceback
import re
import pandas as pd
from dotenv import load_dotenv
from mcqgenrator.utils import read_file,get_table_data
import streamlit as st
# from langchain.callbacks import get_openai_callback
# from langchain_community.callbacks.manager import get_openai_callback

# from mcqgenrator.MCQGenrator import generate_evaluate_chain
from mcqgenrator.MCQGenrator import build_chain
from mcqgenrator.logger import logging

#loading json file

with open('Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

#creating a title for the app
st.title("MCQs Creator Application with LangChain 🦜⛓️")
df = None
#Create a form using st.form
with st.form("user_inputs"):
    #File Upload
    uploaded_file=st.file_uploader("Uplaod a PDF or txt file")

    #Input Fields
    mcq_count=st.number_input("No. of MCQs", min_value=3, max_value=50)

    #Subject
    subject=st.text_input("Insert Subject",max_chars=20)

    # Quiz Tone
    tone=st.text_input("Complexity Level Of Questions", max_chars=20, placeholder="Simple")

    #Add Button
    button=st.form_submit_button("Create MCQs")

    # Check if the button is clicked and all fields have input

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text=read_file(uploaded_file)
                #Count tokens and the cost of API call
                # with get_openai_callback() as cb:
                #     response=generate_evaluate_chain(
                #         {
                #         "text": text,
                #         "number": mcq_count,
                #         "subject":subject,
                #         "tone": tone,
                #         "response_json": json.dumps(RESPONSE_JSON)
                #             }
                #     )
                chain = build_chain(subject)
                response = chain.invoke({
                    "text": text,
                    "number": mcq_count,
                    "subject": subject,
                    "tone": tone,
                    "response_json": json.dumps(RESPONSE_JSON)
                })
                # st.write(response)

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")

            else:
                # print(f"Total Tokens:{cb.total_tokens}")
                # print(f"Prompt Tokens:{cb.prompt_tokens}")
                # print(f"Completion Tokens:{cb.completion_tokens}")
                # print(f"Total Cost:{cb.total_cost}")
                # if isinstance(response, dict):
                #     #Extract the quiz data from the response
                #     quiz=response.get("quiz", None)
                #     if quiz is not None:
                #         table_data=get_table_data(quiz)
                #         if table_data is not None:
                #             df=pd.DataFrame(table_data)
                #             df.index=df.index+1
                #             st.table(df)
                #             #Display the review in atext box as well
                #             st.text_area(label="Review", value=response["review"])
                #             # st.text_area(label="Review", value=response.get("review", "No review generated."))

                #         else:
                #             st.error("Error in the table data")

                # else:
                #     st.write(response)
                # Always try to build the quiz table from the response
                try:
                    quiz_str = response.get("quiz", "")
                    review_text = response.get("review", "No review generated.")

                    # Extract only the JSON part for quiz_str
                    if quiz_str:
                        import re
                        json_match = re.search(r"\{[\s\S]*\}", quiz_str)
                        if json_match:
                            quiz_str = json_match.group()
                        else:
                            quiz_str = ""

                    if quiz_str:
                        table_data = get_table_data(quiz_str)
                        if table_data:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            # Remove any JSON block from the review text
                            clean_review = re.sub(r"\*\*Revised Quiz:\*\*[\s\S]*", "", review_text).strip()

                            # As an extra safeguard, also strip any leftover JSON
                            clean_review = re.sub(r"\{[\s\S]*\}", "", clean_review).strip()

                            st.text_area(label="Review", value=clean_review or "No review available.", height=120, disabled=True)

                        else:
                            st.error("Error in the table data or invalid quiz format.")
                    else:
                        st.error("No valid quiz JSON found in the response.")

                except Exception as e:
                    traceback.print_exception(type(e), e, e.__traceback__)
                    st.error("Error processing the quiz response.")
if df is not None:
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download MCQs as CSV",
        data=csv_data,
        file_name="mcqs_quiz.csv",
        mime="text/csv",
    )