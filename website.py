import flask
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import subprocess
import time

app = Flask(__name__)

ROOT_FOLDER = '/home/ridhima/Downloads/neural-style'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['UPLOAD_FOLDER'] = ROOT_FOLDER

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		# check if the post request has the file part
		if ('content' not in request.files) or ('style' not in request.files):
			flash('No file')
			return redirect(request.url)
		content = request.files['content']
		style = request.files['style']
		
		if content.filename == '' or style.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if content and allowed_file(content.filename) and style and allowed_file(style.filename):
			content.save(os.path.join(app.config['UPLOAD_FOLDER'], "content.jpg"))
			style.save(os.path.join(app.config['UPLOAD_FOLDER'], "style.jpg"))
			return redirect(url_for('index'))

	return '''
	<!DOCTYPE html>
	<head>
		<style>
			label {
				font-size: 1.1em;
				font-weight: bold;
			}
		</style>
	</head>
	<body>
		<center>
			<title>Neural Style Transfer</title>
			<h1>Upload images</h1>
			<form method="post" enctype="multipart/form-data">
				<label for="content">Content image</label>
				<input type="file" name="content" id="content"></br></br>
				<label for="style">Style image</label>
				<input type="file" name="style" id="style"></br></br>
				<input type="submit" value="Upload">
			</form>
		</center>
	</body>
	</html>
	'''

@app.route('/computation')
def index():
	first_time = True
	def inner():
		os.chdir(ROOT_FOLDER)
		proc = subprocess.Popen(['python neural_style.py --content content.jpg --styles style.jpg --output output.jpg --overwrite'], shell=True, stdout=subprocess.PIPE)
		# proc = subprocess.Popen(['cat log.txt'], shell=True, stdout=subprocess.PIPE)

		if first_time:
			yield '<title>Neural Style Transfer</title>'
			yield '<center><h1>Processing the input</h1></center>'

		for line in iter(proc.stdout.readline,''):
			time.sleep(0.1)
			output_line = str(line.rstrip())
			if output_line == "b''":
				print("Complete")
				yield '<script>document.location.href="http://localhost:5000/output"</script>'

			yield output_line.split("'")[1] + "<br/>" + "<script>window.scrollTo(0,document.body.scrollHeight);</script>"

	return flask.Response(inner(), mimetype='text/html')

@app.route('/output')
def output():
	return '''
	<!DOCTYPE html>
	<head></head>
	<body>
		<center>
			<title>Neural Style Transfer</title>
			<h1>Result</h1>
			<image src="output.jpg">
		</center>
	</body>
	</html>
	'''
@app.route('/<path:filename>') 
def send_file(filename):
	# cache-timeout to reload new file everytime 
	# otherwise new output is not rendered on the 
	# final screen
	return flask.send_from_directory(ROOT_FOLDER, filename, cache_timeout=0)

if __name__ == '__main__':
	app.run(debug=True, port=5000, host='0.0.0.0')