import markdown
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