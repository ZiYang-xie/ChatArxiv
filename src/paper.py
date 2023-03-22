import fitz
import os
import io
import arxiv
import tempfile

from PIL import Image
from urllib.parse import urlparse

class Paper:
    def __init__(self, url=''):       
        self.url =  url 
        self.parse_url()
        self.get_pdf()
        self.paper_instance = {
            'title': self.paper_arxiv.title,
            'authors': self.paper_arxiv.authors,
            'arxiv_id': self.paper_arxiv,
            'abstract': self.paper_arxiv.summary,
            'pdf_url': self.paper_arxiv.pdf_url,
            'categories': self.paper_arxiv.categories,
            'published': self.paper_arxiv.published,
            'updated': self.paper_arxiv.updated,
            'content': {}
        }
        self.parse_pdf()

    def get_paper(self):
        return self.paper_instance

    def parse_url(self):
        self.url = self.url.replace('.pdf', '')
        parsed_url = urlparse(self.url)
        paper_id = os.path.basename(parsed_url.path)
        self.paper_id = paper_id

    def get_pdf(self):
        search = arxiv.Search(id_list=[self.paper_id], max_results=1)
        results = search.results()
        paper_arxiv = next(results)
        if paper_arxiv:
            # with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            paper_path = f'{self.paper_id}.pdf'
            dir_path = "./pdf"
            save_dir = os.path.join(dir_path, paper_path)
            if not os.path.exists(save_dir):
                paper_arxiv.download_pdf(dirpath=dir_path, filename=paper_path)
            self.paper_arxiv = paper_arxiv
            self.path = save_dir
        else:
            raise Exception("无法找到论文，请检查 URL 是否正确。")
        
    def parse_pdf(self):
        self.pdf = fitz.open(self.path) 
        self.text_list = [page.get_text() for page in self.pdf]
        self.all_text = ' '.join(self.text_list)
        
        self._parse_paper() 
        self.pdf.close()           
        
    def _get_sections(self):
        doc = self.pdf 
        size_font = {}
        for page in doc:
            text = page.get_text("dict") 
            blocks = text["blocks"] 
            for block in blocks: 
                if block["type"] == 0: 
                    block_text = block["lines"][0]["spans"][0]["text"].strip()  
                    font_size = float(block["lines"][0]["spans"][0]["size"])
                    if font_size not in size_font.keys():
                        size_font[font_size] = []
                    size_font[font_size].append(block_text)
           
        size_list = sorted([float(s) for s in size_font.keys()], reverse=True)
        
        # Auto detect the Section
        for size in size_list:
            # Assert the section number is large than 3
            if len(size_font[size]) > 3:
                self.sections = size_font[size]
                break
        # Auto detect failed, use predefined section
        else: 
            sections = 'Abstract,Introduction,Related Work,Background,Preliminary,Problem Formulation,Methods,Methodology,Method,Approach,Approaches,Materials and Methods,Experiment Settings,Experiment,Experimental Results,Evaluation,Experiments,Results,Findings,Data Analysis,Discussion,Results and Discussion,Conclusion,References'
            self.sections = sections.split(',')

    def _get_all_page_index(self):
        section_list = self.sections
        section_page_dict = {}

        for page_index, page in enumerate(self.pdf):
            cur_text = page.get_text()
            for section_name in section_list:
                section_name_upper = section_name.upper()
                if "Abstract" == section_name and section_name in cur_text:
                    section_page_dict[section_name] = page_index
                else:
                    if section_name + '\n' in cur_text:
                        section_page_dict[section_name] = page_index
                    elif section_name_upper + '\n' in cur_text:
                        section_page_dict[section_name] = page_index

        self.section_page_dict = section_page_dict

    def _parse_paper(self):
        """
         Return: dict { <Section Name>: <Content> }
        """
        self._get_sections()
        self._get_all_page_index() 

        #TODO Optimize the following code
        text_list = []
        section_dict = {}
        text_list = [page.get_text() for page in self.pdf]
        for sec_index, sec_name in enumerate(self.section_page_dict):
            if sec_index <= 0:
                continue
            else:
                start_page = self.section_page_dict[sec_name]
                if sec_index < len(list(self.section_page_dict.keys()))-1:
                    end_page = self.section_page_dict[list(self.section_page_dict.keys())[sec_index+1]]
                else:
                    end_page = len(text_list)
                cur_sec_text = ''
                if end_page - start_page == 0:
                    if sec_index < len(list(self.section_page_dict.keys()))-1:
                        next_sec = list(self.section_page_dict.keys())[sec_index+1]
                        if text_list[start_page].find(sec_name) == -1:
                            start_i = text_list[start_page].find(sec_name.upper())
                        else:
                            start_i = text_list[start_page].find(sec_name)
                        if text_list[start_page].find(next_sec) == -1:
                            end_i = text_list[start_page].find(next_sec.upper())
                        else:
                            end_i = text_list[start_page].find(next_sec)                        
                        cur_sec_text += text_list[start_page][start_i:end_i]
                else:
                    for page_i in range(start_page, end_page):                    
                        if page_i == start_page:
                            if text_list[start_page].find(sec_name) == -1:
                                start_i = text_list[start_page].find(sec_name.upper())
                            else:
                                start_i = text_list[start_page].find(sec_name)
                            cur_sec_text += text_list[page_i][start_i:]
                        elif page_i < end_page:
                            cur_sec_text += text_list[page_i]
                        elif page_i == end_page:
                            if sec_index < len(list(self.section_page_dict.keys()))-1:
                                next_sec = list(self.section_page_dict.keys())[sec_index+1]
                                if text_list[start_page].find(next_sec) == -1:
                                    end_i = text_list[start_page].find(next_sec.upper())
                                else:
                                    end_i = text_list[start_page].find(next_sec)  
                                cur_sec_text += text_list[page_i][:end_i]
                section_dict[sec_name] = cur_sec_text.replace('-\n', '').replace('\n', ' ')
        
        self.paper_instance['content'] = section_dict