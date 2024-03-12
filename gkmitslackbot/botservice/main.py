import os
import pandas as pd
import sqlalchemy as sa
import langchain
langchain.debug=False

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import BaseTool, StructuredTool, tool
# from langchain.tools import DuckDuckGoSearchRun
from langchain.prompts.chat import (
    SystemMessagePromptTemplate as SystemTemplate,
    HumanMessagePromptTemplate as HumanTemplate,
)
# from langchain_community.tools import DuckDuckGoSearchRun
from langchain.pydantic_v1 import BaseModel, Field
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.memory import ChatMessageHistory

from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from .models import chat_history

load_dotenv()
output_parser = StrOutputParser()

llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
openai_api_key = os.getenv('OPENAI_API_KEY')

metadata = MetaData()
metadata = MetaData()
chat_history_table = Table(
    'botservice_chat_history',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('message', String),
    Column('response', String),
    Column('timestamp', DateTime),
    Column('employee_id_id', Integer)
)

class GkmitChatBot:
    def __init__(self):
        self.llm = self.get_llm()
        self.stored_skills = self.get_stored_skills()

    def get_llm(self):
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
        return llm

    def get_tool_list(self) -> list:
        skill_by_user_input_tool = self.get_skill_by_user_input_tool()
        # internet_search_tool = self.get_internet_search_tool()
        response_from_llm_tool = self.get_response_from_llm_tool()
        return [
            skill_by_user_input_tool,
            # internet_search_tool,
            response_from_llm_tool,
        ]

    def get_response(self, question):
        try:
            system_message_template = SystemTemplate.from_template("""
            You are a gkmitchatbot. Answer the user as best you can in human readable form. \
            User will ask a question and you have to answer as best you can. \
            If the user ask about any skill then use the SKILL_BY_USER_INPUT_SEARCH tool. \
            If user ask anything else (other than the skill) then use RESPONSE_FROM_LLM tool. \
            Also use REPONSE_FROM_LLM tool when user ask something from the prevoius chat or conversation. """)
            system_message = system_message_template.format()
            
            history = self.add_chat_history_to_agent()
            agent_kwargs = {
                "system_message": system_message,
                "extra_prompt_messages": history.messages,
            }
            tools = self.get_tool_list()
            agent = initialize_agent(
                tools=tools,
                llm=self.llm,
                agent=AgentType.OPENAI_FUNCTIONS,
                verbose=True,
                agent_kwargs=agent_kwargs,
                return_intermediate_steps=True
            )
            answer = agent.invoke(question)
            # print(answer['output'])

            self.save_conversation_in_database({
                "message": question,
                "response": answer['output'],
                "employee_id_id": 2
            })

            return answer

        except Exception as e:
            return "Sorry, I am unable to answer this question."

    def get_postgres_conn(self):
        db_url = sa.engine.URL.create(drivername='postgresql+psycopg2',
                                    username = os.getenv('DB_USER'),
                                    password = os.getenv('DB_PASSWORD'),
                                    host = os.getenv('DB_HOST'),
                                    port = os.getenv('DB_PORT'),
                                    database = os.getenv('DB_NAME'))
        engine = sa.create_engine(db_url)
        return engine

    def get_stored_skills(self):
        engine = self.get_postgres_conn()
        with engine.connect() as conn:
            result = conn.execute(text("""SELECT LOWER(s."skill_name") FROM botservice_skill s ;"""))
            stored_skills = [row[0] for row in result.fetchall()]
        return stored_skills

    def query_db(self,sql_query):
        engine = self.get_postgres_conn()
        with engine.connect() as conn:
            return pd.read_sql(sql_query, conn).to_dict(orient='records')

    def get_related_skill_from_llm(self, skill):
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
        template = f"""you have a set of skill as {self.stored_skills} and when the user ask about some skill, return the most related skill if it exits. \
        other wise just return null. Also return null in case of user asks for non-technical skill.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("user", "{input}"),
        ])
        chain = prompt | llm | output_parser
        related_skill = chain.invoke({"input": f"which skill is most related to {skill} out of {self.stored_skills}.? return the answer in only one word."})
        return related_skill

    def get_skill_by_user_input_tool(self):
        def get_employee_from_database_tool(skill: str = Field(description="skill")):
            engine = self.get_postgres_conn()
            with engine.connect() as conn:  # with start and close the connection
                print(sa.text(f"""SELECT EXISTS(SELECT 1 FROM botservice_skill WHERE LOWER("skill_name") = LOWER('{skill}'))"""))
                skill_exists = conn.execute(sa.text(f"""SELECT EXISTS(SELECT 1 FROM botservice_skill WHERE LOWER("skill_name") = LOWER('{skill}'))""")).scalar()
                print(skill_exists)
                if skill_exists:
                    # query = GET_EMPLOYEES_DETAILS_EXACT.format(skill)
                    print(skill_exists)
                    temp = pd.read_sql(f"""
                    SELECT e."first_name", e."last_name", e."is_remote_employee", s."skill_name", es."skill_proficiency", e."job_level", e."designation", e."job_description"
                    FROM botservice_emp_skill es
                    JOIN botservice_employee e ON es."employee_id_id" = e."id"
                    JOIN botservice_skill s ON es."skill_id_id" = s."id"
                    WHERE LOWER(s."skill_name") = LOWER('{skill}')
                    ORDER BY
                        CASE es."skill_proficiency"
                            WHEN 'Expert' THEN 1
                            WHEN 'Intermediate' THEN 2
                            WHEN 'Beginner' THEN 3
                            ELSE 4
                        END
                    LIMIT 3;
                    """, conn)
                    print(temp)
                    return temp.to_dict(orient='records')

                else:
                    stored_skills = self.get_stored_skills()
                    related_skill = self.get_related_skill_from_llm(skill)
                    print(f"The most related stored skill to '{skill}' is '{related_skill}'")

                    # query = GET_EMPLOYEES_DETAILS_EXACT.format(related_skill)
                    temp = pd.read_sql(f"""
                    SELECT e."first_name", e."last_name", e."is_remote_employee", s."skill_name", es."skill_proficiency", e."job_level", e."designation", e."job_description"
                    FROM botservice_emp_skill es
                    JOIN botservice_employee e ON es."employee_id_id" = e."id"
                    JOIN botservice_skill s ON es."skill_id_id" = s."id"
                    WHERE LOWER(s."skill_name") = LOWER('{related_skill}')
                    ORDER BY
                        CASE es."skill_proficiency"
                            WHEN 'Expert' THEN 1
                            WHEN 'Intermediate' THEN 2
                            WHEN 'Beginner' THEN 3
                            ELSE 4
                        END
                    LIMIT 3;
                    """, conn)
                    return temp.to_dict(orient='records')
        skill_by_user_input_search_tool = Tool(
            name="SKILL_BY_USER_INPUT",
            func=get_employee_from_database_tool,
            description='''
            Take only the technical skill as input and return the employee detail associated with that skill in the paragraph format. \
            If skill matches the if skill_exists is true then move to 'if' condition otherwise move to 'else' condition. If the related_skill is also not found in the database then reply Sorry, skill not found and provide him with some source from where he can learn. \
            If exact skill is not found and related skill is found then before giving the employee detials mention that "I cannot found the detail related to {skill} but you may connect to the following person". \
            If it goes in 'else' condition then before returning employee details, mention that the employe detail retuned is of the related person. \
            Also in case of when the user ask about non-technical skill then reply Sorry, skill not found and provide him with some source from where he can learn. \
            Give each employee a number and keep them short sentences. \
            ''',
        )
        return skill_by_user_input_search_tool

    def get_response_from_llm_tool(self):
        def chat_with_llm_tool(question):
            llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
            template = """You are a gkmitchatbot. Respond the user as best you can. \
            You have a question what the user ask as reply as best you can is human readable form. \
            If you cannot answer then just return that "Sorry!, I cannot answer it".
            """
            prompt = ChatPromptTemplate.from_messages([
                ("system", template),
                ("user", "{input}"),
            ])
            chain = prompt | llm | output_parser
            related_skill = chain.invoke({"input": question})
            return related_skill
        
        response_from_llm_search_tool = Tool(
            name="RESPONSE_FROM_LLM",
            func=chat_with_llm_tool,
            description='''
            call this tool only to answer any question other than skill. \
            useful for when you need to search question on internet whose answer cannot be found by \
            skill_by_user_input_search_tool tool. You should only ask questions when \
            skill_by_user_input_search_tool tool is not able to answer. \
            ''',
        )
        return response_from_llm_search_tool

    def get_internet_search_tool(self):
        internet_search_chain = DuckDuckGoSearchRun()
        internet_search_tool = Tool(
            name="INTERNET_SEARCH",
            func=internet_search_chain.run,
            description='''
            call this tool only to answer any question other than skill. \
            useful for when you need to search question on internet whose answer cannot be found by \
            skill_by_user_input_search_tool tool. You should only ask questions when \
            skill_by_user_input_search_tool tool is not able to answer. \
            '''
        )
        return internet_search_tool

    def add_chat_history_to_agent(self) -> ChatMessageHistory:
        chat_history = self.get_chat_history()
        if chat_history is None:
            chat_history = []

        history = ChatMessageHistory()
        for chat in chat_history:
            history.add_user_message(chat.Message)
            history.add_ai_message(chat.Response)
        return history

    def save_conversation_in_database(self, conversation):
        Message = conversation["Message"]
        Response = conversation["Response"]
        Employee_ID_id = conversation["Employee_ID_id"]
        Timestamp = datetime.now()
        
        engine = self.get_postgres_conn()
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            insert_query = chat_history_table.insert().values(
                message=conversation["message"],
                response=conversation["response"],
                timestamp=datetime.now(),
                employee_id_id=conversation["employee_id_id"]
            )
            session.execute(insert_query)
            session.commit()
            result = session.execute(chat_history_table.select()).fetchall()
            return result

        except Exception as e:
            session.rollback()
            print("An error occurred:", e)
            return None
        
        finally:
            session.close()
            engine.dispose()

    def get_chat_history(self):
        try:
            chat_history = chat_history.objects.order_by('-timestamp')[:5]
            return chat_history
            
        except Exception as e:
            print("An error occurred:", e)
            return None

if __name__ == "__main__":
    chat_bot = GkmitChatBot()