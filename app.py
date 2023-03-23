
import gradio as gr
from src.paper import Paper
from src.reader import Reader

class ChatArxiv: 
    def init(self, api_key, url):
        self.paper = Paper(url)
        self.reader = Reader(self.paper, api_key)
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
        return embed_html, reply
    
    def test(self):
        self.paper.paper_instance['content'].keys()
        import pdb; pdb.set_trace()
    
    def read_full(self):
        if getattr(self, 'paper', None) is None:
            return "请先设置论文链接和 API key，点击 ⚙ Set 按钮"
        
        return self.reader.read_paper()

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
                with gr.Row():
                    configure_btn = gr.Button("⚙ Set")
                    read_btn = gr.Button("📖 Read Full Paper")
                
                #test_btn = gr.Button("Test Btn")
            with gr.Column(scale=1):
                op_submit = gr.Textbox(label="🤖 Arxiv Bot ", default="")
                ip_submit = gr.inputs.Textbox(label="请输入问题", default="")
                submit_btn = gr.Button("🚀 Submit ")
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
            
        configure_btn.click(fn=chatArxiv.init, inputs=ip_config, outputs=[pdf_preview, op_submit])
        submit_btn.click(fn=chatArxiv.ask, inputs=ip_submit, outputs=op_submit)
        read_btn.click(fn=chatArxiv.read_full, outputs=op_submit)
        #test_btn.click(fn=chatArxiv.test)
    app.launch()
