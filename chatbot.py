import os
import re
import openai
import markdown
# import traceback
from dotenv import load_dotenv

load_dotenv()

def clean_string(input_string):
    # Use regex to keep only alphanumeric characters
    cleaned_string = re.sub(r'[^a-zA-Z0-9]', '', input_string)
    return cleaned_string

api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    key = input("Please input your api key: ").strip()
    api_key = clean_string(key)

client = openai.AzureOpenAI(
    azure_endpoint=os.getenv('OPENAI_API_ENDPOINT', "https://api.hku.hk"),
    api_key=api_key,
    api_version="2025-01-01-preview"
)

def history_default():
    return [{"role": "system", "content": "You are a helpful assistant who helps to write notes. You may also answer user's questions if they have query. You write or correct notes according to the user's input. Keep your response concise. Answer directly without any polite phrases or conclusions. You may have a title, but don't write any openings before the title, but after the title. If there is title, use <h1> (the largest heading) for the title. Use latex for any math symbols. Use 4 spaces for any indentations. Better use <ol> and <ul> tags for lists. Use HTML tags for tables."}]

def select_model(model_input):
    match model_input:
        case 'GPT-4.1-nano': return 'gpt-4.1-nano'
        case 'GPT-4.1-mini': return 'gpt-4.1-mini'
        case 'GPT-4.1': return 'gpt-4.1'
        case 'o4-mini': return 'o4-mini'
        case 'GPT-4o': return 'gpt-4o'
        case 'GPT-4': return 'gpt-4'
        case 'GPT-3.5': return 'gpt-35-turbo'
        case _: return model_input

def is_image_file(filepath):
    if not os.path.isfile(filepath):
        return False
    mime, _ = mimetypes.guess_type(filepath)
    if mime and mime.startswith('image/'):
        return True
    return False

def process_image(image_path):
    if image_path and is_image_file(image_path):
        with open(image_path, "rb") as image_file:
            mime, _ = mimetypes.guess_type(image_path)
            base64_str = base64.b64encode(image_file.read()).decode()
            image_data = f"data:{mime};base64,{base64_str}"
        return image_data
    else:
        raise ValueError("The provided file is not a valid image.")

def chatbot(message=False, image=False, model="gpt-4.1", prompt="You are a helpful assistant who helps to write notes.", temperature=0.7, history=history_default(), defining=False):
    model=select_model(model)
    temperature = 1 if model == 'o4-mini' else temperature
    
    history[0]['content'] = prompt
    if image:
        # with open(image, "rb") as image_file:
        #     image = "data:image/jpeg;base64," + base64.b64encode(image_file.read()).decode()
        image = process_image(image)
        content = []
        if message:
            content.append({"type": "text", "text": message})
        content.append({"type": "image_url", "image_url": {"url": image}})
        new_prompt = {"role": "user", "content": content}
    else:
        new_prompt = {"role": "user", "content": message}
    history.append(new_prompt)
    # completion = openai.ChatCompletion.create(engine="chatgpt", messages=history)
    response = client.chat.completions.create(model=model, messages=history, temperature=temperature)
    answer = response.choices[0].message.content
    if defining: history.pop()
    elif not defining:
        history.append({"role": "assistant", "content": answer})
    return history, answer

##################################################################################################

def save_to_md(text, filename="output_0.md"):
    while os.path.isfile(filename):
        name = filename.split('.')[0]
        if re.search(r'_\d+$', name):
            filename = name.split('_')[0] + '_' + str(int(name.split('_')[1])+1) + '.md'
        else:
            filename = name + '_0.md'
    with open(filename, 'w') as file:
        file.write(text)
    print(f"Markdown content saved to {filename}")


def save_to_html(text, filename="output_0.html"):
    while os.path.isfile(filename):
        name = filename.split('.')[0]
        if re.search(r'_\d+$', name):
            filename = name.split('_')[0] + '_' + str(int(name.split('_')[1])+1) + '.html'
        else:
            filename = name + '_0.html'
    # text = text.replace('\\', '\\\\')
    # text = text.replace('\n', '\n\n')
    # text = re.sub(r'\n+([ \t]+\$\$|[ \t]+\\\])', r'\n\1', text)
    # text = re.sub(r'(\$\$|\\\[)\n+', r'\1\n', text)

    text.replace('<', '< ')
    text.replace('\\(', '\\( ')
    text.replace('\\)', ' \\) ')
    text.replace('\\[', '\\[ ')
    text.replace('\\]', ' \\] ')

    text = re.sub(r'\n+([ \t]+\$\$|[ \t]+\\\])', r'\n\1', text)
    text = re.sub(r'(\$\$|\\\[)\n+', r'\1\n', text)
    text = re.sub(r'\\([()\[\]+])', r'\\\\\1', text)

    html_text = markdown.markdown(text, extensions=['extra', 'smarty'])
    
    if html_text.startswith('<!DOCTYPE html>'):
        html_style = """
    <style>
        h1 {
            text-align: center;
            font-size: 27px;
        }

        h2 {
            line-height: 0.5;
            font-size: 23px;
        }

        h3 {
            font-size: 18px;
        }
        body {
            font-family: 'Times New Roman', Times, serif;
        }
        @media print {
            section {
                page-break-inside: avoid; /* Avoid breaking inside sections */
                page-break-after: always;  /* Start a new page after each section */
            }
            
            p {
                page-break-after: avoid; /* Avoid breaking after paragraphs */
            }
        }
    </style>
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" integrity="sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+" crossorigin="anonymous">
	<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" integrity="sha384-7zkQWkzuo3B5mTepMUcHkMB5jZaolc2xDwL6VFqjFALcbeS9Ggm/Yr2r3Dy4lfFg" crossorigin="anonymous"></script>
	<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" integrity="sha384-43gviWU0YVjaDtb/GhzOouOXtZMP/7XUzwPTstBeZFe/+rCMvRwr4yROQP43s0Xk" crossorigin="anonymous"></script>
	<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    
    <script>
		document.addEventListener("DOMContentLoaded", function() {
			renderMathInElement(document.body, {
			delimiters: [
				{left: '$$', right: '$$', display: true},
				{left: '$', right: '$', display: false},
				{left: '\\\\(', right: '\\\\)', display: false},
				{left: '\\\\[', right: '\\\\]', display: true},
                {left: '\\\\begin{align*}', right: '\\\\end{align*}', display: true},
                {left: '\\\\begin{aligned}', right: '\\\\end{aligned}', display: true}
			],
			throwOnError : false
			});
		});
	</script>
    <style>
        @media print {
            .print-instructions {
                display: none;
            }
        }
        .print-instructions {
            font-size: 12px;
            color: #666;
        }
    </style>
</head>"""
        html_format = ''.join([html_text.split('</head>')[0], html_style, html_text.split('</head>')[1]])
    else:
        html_format = """<!DOCTYPE html>
<html lang="en">

<head>
    <title>%s</title>
    <meta charset="UTF-8">
    <style>
        h1 {
            text-align: center;
            font-size: 27px;
        }

        h2 {
            line-height: 0.5;
            font-size: 23px;
        }

        h3 {
            font-size: 18px;
        }
        body {
            font-family: 'Times New Roman', Times, serif;
        }
        @media print {
            section {
                page-break-inside: avoid; /* Avoid breaking inside sections */
                page-break-after: always;  /* Start a new page after each section */
            }
            
            p {
                page-break-after: avoid; /* Avoid breaking after paragraphs */
            }
        }
    </style>
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" integrity="sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+" crossorigin="anonymous">
	<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" integrity="sha384-7zkQWkzuo3B5mTepMUcHkMB5jZaolc2xDwL6VFqjFALcbeS9Ggm/Yr2r3Dy4lfFg" crossorigin="anonymous"></script>
	<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" integrity="sha384-43gviWU0YVjaDtb/GhzOouOXtZMP/7XUzwPTstBeZFe/+rCMvRwr4yROQP43s0Xk" crossorigin="anonymous"></script>
	<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    
    <script>
		document.addEventListener("DOMContentLoaded", function() {
			renderMathInElement(document.body, {
			delimiters: [
				{left: '$$', right: '$$', display: true},
				{left: '$', right: '$', display: false},
				{left: '\\\\(', right: '\\\\)', display: false},
				{left: '\\\\[', right: '\\\\]', display: true},
                {left: '\\\\begin{align*}', right: '\\\\end{align*}', display: true},
                {left: '\\\\begin{aligned}', right: '\\\\end{aligned}', display: true}
			],
			throwOnError : false
			});
		});
	</script>
    <style>
        @media print {
            .print-instructions {
                display: none;
            }
        }
        .print-instructions {
            font-size: 12px;
            color: #666;
        }
    </style>
</head>

<body>

%s


   
</body>
<footer>
 <div class="print-instructions">
        <p><i>[To print this page without headers and footers, please adjust your browser's print settings]</i></p>
    </div>
</footer>
</html>""" %(filename.split('.')[0], html_text)
    
    with open(filename, 'w') as file:
        file.write(html_format)

    import webbrowser 
    filename = os.path.abspath(filename)
    webbrowser.open(f'file://{filename}') 
    print(f"Markdown content saved to {filename}")