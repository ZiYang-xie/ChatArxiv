
import gradio as gr
from src.paper import Paper
from src.reader import Reader
from src.utils import language_dict

class ChatArxiv: 
    def init(self, api_key, url, lang='English'):
        self.paper = Paper(url)
        self.reader = Reader(self.paper, api_key, language=lang)
        embed_html = f'''
                        <div style='display:flex; height:80vh; border: 1px solid #e5e7eb; border-radius: 8px'>
                            <embed
                                src=file/{self.paper.path}
                                type="application/pdf"
                                width="100%"
                                height="100%"
                            />
                        </div>
                      '''
        reply = "我已经阅读完论文的基本信息 😋\n您可以开始提问一些基本问题了 \n 点击 📖 Read Full Paper 让我阅读整篇论文可以提高回答质量"
        basic_info = self.reader.get_basic_info()
        chapter_list = self.ret_chapter_list()

        return embed_html, reply, basic_info, chapter_list
    
    def ret_chapter_list(self):
        chapter_ops = [str(k) for k in self.paper.paper_instance.get('content').keys()]
        return gr.Dropdown.update(choices=chapter_ops)
    
    def read_chap(self, chapter_list):
        if getattr(self, 'paper', None) is None:
            return "请先设置论文链接和 API key，点击 ⚙ Set 按钮"
        return self.reader.read_paper(chapter_list)

    def ask(self, prompt):
        return self.reader.chat_with_paper(prompt)

if __name__ == '__main__':
    chatArxiv = ChatArxiv()
    title = "<div align='center'><h1> ChatArxiv 📑 </h1></div>"
    desc = "<div align='center'>帮助您快速阅读 Arxiv 论文</div>"
    with gr.Blocks() as app:
        gr.HTML(title)
        gr.HTML(desc)
        with gr.Row():
            with gr.Column(scale=1):
                ip_config = [
                    gr.inputs.Textbox(label="请输入OpenAI api key", default=""),
                    gr.inputs.Textbox(label="请输入论文 Arxiv 链接", default=""),
                ]
                # We do not need the ISO 639-1 language code since we interact with LLM by natural language!!
                lang = gr.Dropdown(list(language_dict.values()), label="语言", value='中文')
                configure_btn = gr.Button("⚙ 初始设置")
                simple_rate = gr.Textbox(label="基本简介与评价", default="", interactive=False)
                
                #test_btn = gr.Button("Test Btn")
            with gr.Column(scale=1):
                chapter_sel = gr.Dropdown(label="请选择阅读章节", multiselect=True, interactive=True)
                read_btn = gr.Button("📖 阅读章节")
                op_submit = gr.Textbox(label="🤖 Arxiv Bot ", default="")
                ip_submit = gr.inputs.Textbox(label="请输入问题", default="")
                submit_btn = gr.Button("🚀 提交 ")

            with gr.Column(scale=1.5):
                embed_html = '''
                        <div style='display:flex; height:80vh; border: 1px solid #e5e7eb; border-radius: 8px'>
                            <embed
                                src=file/assets/blank.pdf
                                type="application/pdf"
                                width="100%"
                                height="100%"
                            />
                        </div>
                      '''
                pdf_preview = gr.HTML(value=embed_html)

        configure_btn.click(fn=chatArxiv.init, inputs=[*ip_config, lang], outputs=[pdf_preview, op_submit, simple_rate, chapter_sel])
        submit_btn.click(fn=chatArxiv.ask, inputs=ip_submit, outputs=op_submit)
        read_btn.click(fn=chatArxiv.read_chap, inputs=chapter_sel, outputs=op_submit)
        #test_btn.click(fn=chatArxiv.test)
    app.launch()
