from flask import Flask, session, request, jsonify, render_template, redirect, url_for
from flask_session import Session
import secrets
import re
import uuid
import markdown
import traceback
from chatbot import chatbot, history_default, save_to_html, save_to_md

def md_to_html_for_input(text):
    # text = text.replace('\\', '\\\\')
    # text = text.replace('```', '\n```')
    # text = text.replace('\n', '\n\n')
    # text = re.sub(r'\n+', '\n', text)
    text.replace('<', '< ')
    text.replace('\\(', '\\( ')
    text.replace('\\)', ' \\) ')
    text.replace('\\[', '\\[ ')
    text.replace('\\]', ' \\] ')

    text = re.sub(r'\n+([ \t]+\$\$|[ \t]+\\\])', r'\n\1', text)
    text = re.sub(r'(\$\$|\\\[)\n+', r'\1\n', text)
    text = re.sub(r'\\([()\[\]+])', r'\\\\\1', text)
    
    html_text = markdown.markdown(text, extensions=['extra', 'smarty'])

    html_text = html_text.replace('<pre>', '<div class="code-container">\n <button class="copy-button" onclick="copyToClipboard(this)">Copy</button>\n <pre>')
    html_text = html_text.replace('</pre>', '</pre> </div> \n <div id="notification" class="notification">Code copied to clipboard!</div>')

    return html_text

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = secrets.token_hex(16)
Session(app)

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    return redirect(url_for('new_session'))

@app.route('/new-session')
def new_session():
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    session['chat_history'] = history_default()
    return redirect(url_for('chat', session_id=session_id))

@app.route('/chat/<session_id>')
def chat(session_id):
    if 'session_id' not in session or session['session_id'] != session_id:
        session['session_id'] = session_id
        print("Session id:", session_id)
        session['chat_history'] = history_default()
    return render_template('notebot.html', session_id=session_id)

@app.route('/generate-note/<session_id>', methods=['POST'])
def generate_note(session_id):
    if 'session_id' not in session or session['session_id'] != session_id:
        return jsonify({'error': 'Invalid session ID'}), 400
    history = session.get('chat_history', history_default())
    data = request.json
    user_input = data.get('user_input')
    prompt = data.get('prompt')
    model = data.get('model')
    temperature = data.get('temperature')
    if user_input.strip().lower() == 'clear':
        history = history_default()
        session['chat_history'] = history
        print("History cleared.")
        return jsonify({'note': ''})
    else:
        try:
            history, note = chatbot(user_input, model=model, prompt=prompt, temperature=temperature, history=history)
            session['chat_history'] = history
            print(note)
            html_note = md_to_html_for_input(note)
            return jsonify({'note': html_note})
        except Exception:
            error = "**An error occurred**: \n```\n" + traceback.format_exc() + '```' +'\n*Please contact the developer for this issue.*'
            print(error)
            error = md_to_html_for_input(error)
            return jsonify({'note': error})
        

@app.route('/save-note/<session_id>', methods=['POST'])
def save_note(session_id):
    if 'session_id' not in session or session['session_id'] != session_id:
        return jsonify({'error': 'Invalid session ID'}), 400
    data = request.json
    filename = data.get('filename', '')
    history = session.get('chat_history', history_default())
    if filename == '':
        save_to_md(history[-1]['content'])
    else:
        save_to_html(history[-1]['content'], filename + '.html')
    print("Response saved.")
    return jsonify({'status': 'Response saved'})

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()