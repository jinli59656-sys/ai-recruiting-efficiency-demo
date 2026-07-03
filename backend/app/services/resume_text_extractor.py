import pdfplumber
from PyPDF2 import PdfReader
from docx import Document


#将简历内容转换为文本
def extract_resume_text(file_path:str,file_type:str)->str:
    if file_type=="pdf":
        return extract_text_from_pdf(file_path)
    if file_type=="docx":
        return extract_text_from_docx(file_path)

    raise ValueError(f"暂不支持的文件类型：{file_type}")

def extract_text_from_pdf(file_path:str)-> str:

    texts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                texts.append(text)
    #分成两步：1 将每一页文字用换行拼接，列表中的"第一页内容","第二页内容","第三页内容"
    #会变成第一页内容\n 第二页内容\n 第三页内容中间用\n隔开，再strip（）去掉开头和结尾的空白字符
    #这样返回的就是一段文本了，并且每一页换行分开
    return "\n".join(texts).strip()

def extract_text_from_docx(file_path:str)->str:
    doc=Document(file_path)
    texts=[]
    #这里得到的是每一段
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            texts.append(paragraph.text.strip())
    return "\n".join(texts).strip()