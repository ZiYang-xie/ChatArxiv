
import gradio as gr
from src.paper import Paper
from src.reader import Reader

class ChatArxiv: 
    def init(self, api_key, url):
        self.paper = Paper(url)
        self.reader = Reader(self.paper, api_key)
        return "I'm Ready!"
    
    def test(self):
        self.paper.paper_instance['content'].keys()
        import pdb; pdb.set_trace()
    
    def read_intro(self):
        return self.reader.read_intro()

    def ask_intro(self, prompt):
        return self.reader.chat_intro(prompt)

if __name__ == '__main__':
    chatArxiv = ChatArxiv()

    title = "<div align='center'><h1> ChatArxiv 📑 </h1></div>"
    desc = "<div align='center'>帮助您快速阅读 Arxiv 论文</div>"
    with gr.Blocks() as app:
        gr.HTML(title)
        gr.HTML(desc)
        with gr.Row():
            with gr.Column():
                ip_config = [
                    gr.inputs.Textbox(label="请输入OpenAI api key", default=""),
                    gr.inputs.Textbox(label="请输入论文 Arxiv 链接", default=""),
                ]
                configure_btn = gr.Button("⚙ Set")
                ip_submit = gr.inputs.Textbox(label="请输入问题", default="")
                submit_btn = gr.Button("🚀 Submit ")
                #test_btn = gr.Button("Test Btn")
            with gr.Column():
                read_btn = gr.Button("📖 Read")
                op_submit = gr.Textbox(label="🤖 Arxiv Bot ", default="")

            

        configure_btn.click(fn=chatArxiv.init, inputs=ip_config, outputs=op_submit)
        submit_btn.click(fn=chatArxiv.ask_intro, inputs=ip_submit, outputs=op_submit)
        read_btn.click(fn=chatArxiv.read_intro, outputs=op_submit)
        #test_btn.click(fn=chatArxiv.test)
    app.launch()
