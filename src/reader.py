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
                 language='English'):
        self.user_name = user_name 
        self.language = language
        self.paper_instance = paper.get_paper()
        
        self.chat_api_list = [api_key]
        self.chatPaper = chatPaper(api_keys=self.chat_api_list, apiTimeInterval=10)
        self.chatPaper.add_to_conversation(message="You are a professional academic paper reviewer and mentor named Arxiv Bot. As a professional academic paper reviewer and helpful mentor, you possess exceptional logical and critical thinking skills, enabling you to provide concise and insightful responses.", role='assistant', convo_id="chat")
        self.chatPaper.add_to_conversation(message="You are not allowed to discuss anything about politics, do not comment on anything about that.", role='assistant', convo_id="chat")
        self.chatPaper.add_to_conversation(message="You will be asked to answer questions about the paper with deep knowledge about it, providing clear and concise explanations in a helpful, friendly manner, using the asker's language.", role='user', convo_id="chat")

        # Read Basic Info of the Paper 
        self._read_basic()

    def _get_intro_prompt(self, intro_content: str = ''):
        if intro_content == '':
            intro_key = [k for k in self.paper_instance['content'].keys()][0]
            intro_content = self.paper_instance['content'][intro_key]
        prompt = (f"This is an academic paper from {self.paper_instance['categories']} fields,\n\
                        Title of this paper are {self.paper_instance['title']}.\n\
                        Authors of this paper are {self.paper_instance['authors']}.\n\
                        Abstract of this paper is {self.paper_instance['abstract']}.\n\
                        Introduction of this paper is {intro_content}.")
        return prompt

    def _init_prompt(self, convo_id: str = 'default'):
        intro_content = ''
        max_tokens = self.chatPaper.max_tokens

        prompt = self._get_intro_prompt(intro_content)
        full_conversation_ = "\n".join([str(x["content"]) for x in self.chatPaper.conversation[convo_id]],)
        full_conversation = str(full_conversation_ + prompt)

        # Try to summarize the intro part
        if(len(self.chatPaper.ENCODER.encode(str(full_conversation)))>max_tokens):
            prompt = f'This is the introduction, please summarize it and reduct its length in {max_tokens} tokens: {prompt}'
            intro_content = self._summarize_content(prompt)
            prompt = self._get_intro_prompt(intro_content)
            full_conversation = str(full_conversation_ + prompt)

        # Failed, try to reduce the length of the prompt
        while(len(self.chatPaper.ENCODER.encode(str(full_conversation)))>max_tokens):
            prompt = prompt[:self.chatPaper.decrease_step]
            full_conversation = str(full_conversation_ + prompt)

        return prompt
    
    def _summarize_content(self, content: str = ''):
        sys_prompt = "Your goal is to summarize the provided content from an academic paper. Your summary should be concise and focus on the key information of the academic paper, do not miss any important point."
        self.chatPaper.reset(convo_id='summary', system_prompt=sys_prompt)
        response = self.chatPaper.ask(content, convo_id='summary')
        res_txt = str(response[0])
        return res_txt
    
    def get_basic_info(self):
        prompt = f'Introduce this paper (its not necessary to include the basic information like title and author name), comment on this paper based on its abstract and introduction from its 1. Novelty, 2. Improtance, 3. Potential Influence. Relpy in {self.language}'
        basic_op = self.chatPaper.ask(prompt, convo_id='chat')[0]
        authors = ", ".join([au.name for au in self.paper_instance['authors']])
        basic_info = [
            self.paper_instance['title'],
            authors,
            basic_op
        ]
        return basic_info

    def _read_basic(self, convo_id="chat"):
        prompt = self._init_prompt(convo_id)
        self.chatPaper.add_to_conversation(
            convo_id=convo_id, 
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
        reply = str(result[0])
        return reply


        
