import os
import re
import numpy as np
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

        # Read Basic Info of the Paper 
        self._read_basic()

    # Split the Prompt to fit the model's input token size
    def _split_prompt(self, prompt, max_token):
        usage_token = self.chatPaper.token_str(prompt)
        if usage_token <= max_token:
            return [str(prompt)]
            
        sentences = re.split(r'(?<=[。.!?])\s+', prompt)
        result = []
        current_prompt = ''
        for sentence in sentences:
            sentence = str(sentence)
            if self.chatPaper.token_str(current_prompt + sentence) <= max_token:
                current_prompt += sentence
            else:
                result.append(current_prompt.strip())
                current_prompt = sentence

        result.append(current_prompt.strip())
        return result


    def _read_basic(self):
        intro_key = [k for k in self.paper_instance['content'].keys()][0]
        msg_prompt = f"This is an academic paper from {self.paper_instance['categories']} fields, \
                        Title of this paper are {self.paper_instance['title']}. \
                        Authors of this paper are {self.paper_instance['authors']}. \
                        Abstract of this paper is {self.paper_instance['abstract']}. \
                        Introduction of this paper is {self.paper_instance['content'][intro_key]}. \
                        You will be asked to answer questions about this paper. \
                        You know a lot about this field and your reply will help the reader to understand the general idea of this paper."
        
        max_token = self.chatPaper.max_tokens
        prompt_list = self._split_prompt(msg_prompt, max_token)
        for prompt in prompt_list:
            self.chatPaper.add_to_conversation(
                convo_id="chat", 
                role="assistant", 
                message= prompt
            )
        

    def read_paper(self):
        #TODO not implemented yet
        return "我读完了，让我们开始吧! 🤩 (Under Development)"
    
    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
                    stop=tenacity.stop_after_attempt(5),
                    reraise=True)
    def chat_with_paper(self, prompt):
        result = self.chatPaper.ask(
            prompt = prompt,
            role="user",
            convo_id="chat",
        )
        return result[0]


        
