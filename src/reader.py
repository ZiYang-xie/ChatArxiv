import os
import re
import datetime
import tenacity
import arxiv
import markdown

from .paper import Paper
from .optimizeOpenAI import chatPaper

class Reader:
    def __init__(self, 
                 paper: Paper,
                 api_key='',
                 user_name='defualt', 
                 language='en'):
        self.user_name = user_name 
        self.language = language
        self.paper_instance = paper.get_paper()
        
        self.chat_api_list = [api_key]
        self.chatPaper = chatPaper(api_keys=self.chat_api_list, apiTimeInterval=10)
        self.chatPaper.reset(convo_id="chat", 
                             system_prompt="You are a professional academic paper reviewer. \
                                            As a professional academic paper reviewer, you possess exceptional logical and critical thinking skills, \
                                            enabling you to provide concise and insightful responses.")

        self.chat_api_list = [api.strip() for api in self.chat_api_list if len(api) > 5]
        self.cur_api = 0
        self.file_format = 'md' 
        self.save_image = False

    def read_intro(self):
        intro_key = [k for k in self.paper_instance['content'].keys()][0]
        msg_prompt = f"This is an academic paper from {self.paper_instance['categories']} fields, \
                        Authors of this paper are {self.paper_instance['authors']}. \
                        Abstract of this paper is {self.paper_instance['abstract']}. \
                        Introduction of this paper is {self.paper_instance['content'][intro_key]}. \
                        You will be asked to answer questions about this paper. \
                        You know a lot about this field and your reply will help the reader to understand the general idea of this paper."
        max_token = self.chatPaper.max_tokens
        assert len(msg_prompt) < max_token, "System prompt is too long, you find a TOBE fixed bug"
        self.chatPaper.add_to_conversation(
            convo_id="chatIntro", 
            role="assistant", 
            message= msg_prompt
        )
        return "I'm Done! 😋"
    
    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
                    stop=tenacity.stop_after_attempt(5),
                    reraise=True)
    def chat_with_paper(self, prompt):
        self.chatPaper.add_to_conversation(
            convo_id="chat", 
            role="assistant", 
            message=str(f"This is an academic paper from {self.paper_instance['categories']} fields, \
                          {self.paper_instance['content']}. \
                          You know a lot about this paper and will reply any questions about this paper.")
        )
        pass


    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
                    stop=tenacity.stop_after_attempt(5),
                    reraise=True)
    # Some Predefined Function
    def chat_intro(self, prompt):
        result = self.chatPaper.ask(
            prompt = prompt,
            role="user",
            convo_id="chatIntro",
        )
        return result[0]
        
