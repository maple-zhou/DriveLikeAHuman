import json
from typing import Union,List

from langchain.agents.agent import AgentOutputParser
from langchain.agents import Tool
from langchain.agents.chat.prompt import FORMAT_INSTRUCTIONS
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.prompts import StringPromptTemplate

import re


FINAL_ANSWER_ACTION = "Final Answer:"


class myChatOutputParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        # First we log the original output of LLM.
        with open("log/parser_log.txt",'a') as f:
            f.write(f"\nBelow is the LLM output!\n")
            f.write(text)
            f.write(f"\nEnd, the LLM output has.\n")
        # Since the LLM output can't understand stop sequence. We shall do it manually.
        try:
            regex = r"^(Observation.*?\n)?(.+?)\s*?\n(\s*?)(\*\*)?Observation(\*\*)?"
            match = re.search(regex,text,flags=re.DOTALL)
            text = match.group(2)
        except:
            pass
        # See how well our cut do
        with open("log/parser_log.txt",'a') as f:
            f.write(f"\nBelow is the stop-LLM output!\n")
            f.write(text)
            f.write(f"\nEnd, the stop-LLM output has.\n")

        
        includes_answer = FINAL_ANSWER_ACTION in text
        try:
            action = text.split("```")[1]

            with open("log/parser_log.txt",'a') as f:
                f.write(f"\nNow we consider the action retrieving\n")
                f.write(action)
            action = action.strip("json")
            response = json.loads(action.strip())

            with open("log/parser_log.txt",'a') as f:
                f.write(f"\nNow we consider the json parsing\n")
                f.write(str(response))

            includes_action = "action" in response
            if includes_answer and includes_action:
                raise OutputParserException(
                    "Parsing LLM output produced a final answer "
                    f"and a parse-able action: {text}"
                )
            return AgentAction(
                response["action"], response.get("action_input", {}), text
            )

        except Exception:
            if not includes_answer:
                raise OutputParserException(f"Could not parse LLM output: {text}")
            return AgentFinish(
                {"output": text.split(FINAL_ANSWER_ACTION)[-1].strip()}, text
            )

    @property
    def _type(self) -> str:
        return "chat"




# class myChatOutputParser(AgentOutputParser):

#     def get_format_instructions(self) -> str:
#         return FORMAT_INSTRUCTIONS

#     def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
#         with open("C:/Users/lyk/Desktop/DriveLikeAHuman/llmoutput.txt","a") as f:
#             f.write(f"{text}\n")
#         includes_answer = FINAL_ANSWER_ACTION in text
#         try:
#             print(text.split("Action:")[1])
#             text = text.split("Action:")[1].split("}\n```")[0] + "}"
#             action = "{"+text.split("```\n{")[1]
#             response = json.loads(action.strip())
#             includes_action = "action" in response
#             if includes_answer and includes_action:
#                 raise OutputParserException(
#                     "Parsing LLM output produced a final answer "
#                     f"and a parse-able action: {text}"
#                 )
#             return AgentAction(
#                 response["action"], response.get("action_input", {}), text
#             )

#         except Exception:
#             if not includes_answer:
#                 raise OutputParserException(f"Could not parse LLM output: {text}")
#             return AgentFinish(
#                 {"output": text.split(FINAL_ANSWER_ACTION)[-1].strip()}, text
#             )

#     @property
#     def _type(self) -> str:
#         return "chat"

