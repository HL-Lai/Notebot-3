from flask import Flask, session, request, jsonify, render_template, redirect, url_for
from flask_session import Session
import secrets
import re
import uuid
import markdown
import traceback
from chatbot import chatbot, history_default
from utils import save_to_html, save_to_md
from dotenv import load_dotenv

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
    image_input = data.get('image_input')
    prompt = data.get('prompt')
    model = data.get('model')
    temperature = data.get('temperature')
    keyUpdated = data.get('keyUpdated')

    if keyUpdated:
        api_key = keyUpdated
    else:
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')

    if user_input.strip().lower() == 'clear':
        history = history_default()
        session['chat_history'] = history
        print("History cleared.")
        return jsonify({'note': ''})
    else:
        try:
            history, note = chatbot(message=user_input, image=image_input, model=model, prompt=prompt, temperature=temperature, history=history, api_key=api_key)
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

# @app.route('/set-api-key/<session_id>', methods=['POST'])
# def set_api_key(session_id):
#     if 'session_id' not in session or session['session_id'] != session_id:
#         return jsonify({'error': 'Invalid session ID'}), 400
#     data = request.json
#     api_key = data.get('api_key', '')
#     session['api_key'] = api_key
#     # Optionally persist the key for next time (e.g., in a DB or file) if you want
#     return jsonify({'status': 'API Key saved'})

import os

@app.route('/set-api-key/<session_id>', methods=['POST'])
def set_api_key(session_id):
    if 'session_id' not in session or session['session_id'] != session_id:
        return jsonify({'error': 'Invalid session ID'}), 400

    data = request.json
    api_key = data.get('api_key', '')
    session['api_key'] = api_key

    env_path = '.env'
    updated = False
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY = ') and not updated:
                    lines.append(f'OPENAI_API_KEY = "{api_key}"\n')
                    updated = True
                elif not line.startswith('OPENAI_API_KEY = '):
                    lines.append(line)
            # If we never found the key, add it at the end
    if not updated:
        lines.append(f'OPENAI_API_KEY = "{api_key}"\n')
    with open(env_path, 'w') as f:
        f.writelines(lines)

    return jsonify({'status': 'API Key saved'})

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()

    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8081, threads=2)