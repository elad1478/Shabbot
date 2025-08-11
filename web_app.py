import os
import re
import asyncio
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

from main import create_agent

app = Flask(__name__)
app.config['QR_DIR'] = os.path.join(os.path.dirname(__file__), 'outputs', 'qr_codes')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            return redirect(url_for('index'))
        
        agent = create_agent()
        if agent is None:
            return render_template('index.html', title='Shabbot', error='Agent not available (missing API keys).')
        
        try:
            result = asyncio.run(agent.ainvoke({"input": query}))
            output = result.get('output', '')
            # Extract a QR image path if present inside the output text
            image_path = None
            if isinstance(output, str):
                m = re.search(r"(outputs/qr_codes/[^\s]+\.png)", output)
                if m:
                    image_path = m.group(1)
            return render_template('index.html', title='Shabbot', query=query, output=output, image_path=image_path)
        except Exception as e:
            return render_template('index.html', title='Shabbot', error=str(e))
    
    return render_template('index.html', title='Shabbot')


@app.route('/outputs/qr_codes/<path:filename>')
def serve_qr(filename: str):
    return send_from_directory(app.config['QR_DIR'], filename)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)