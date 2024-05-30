from flask import Flask, render_template, request, redirect
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def calcular_decimas(porcentaje):
    if porcentaje == 100:
        return 2
    elif 90 <= porcentaje <= 99:
        return 9
    elif 80 <= porcentaje <= 89:
        return 8
    elif 70 <= porcentaje <= 79:
        return 7
    elif 60 <= porcentaje <= 69:
        return 6
    elif 50 <= porcentaje <= 59:
        return 5
    elif 40 <= porcentaje <= 49:
        return 4
    elif 30 <= porcentaje <= 39:
        return 3
    elif 20 <= porcentaje <= 29:
        return 2
    elif 10 <= porcentaje <= 19:
        return 1
    elif 1 <= porcentaje <= 9:
        return 0
    elif porcentaje == 0:
        return 0

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Procesar el archivo CSV
            df = pd.read_csv(filepath)
            df['decimas obtenidas'] = df['Porcentaje completado'].apply(calcular_decimas)
            df['Porcentaje completado'] = df['Porcentaje completado'].astype(str) + '%'
            columnas_seleccionadas = df[['Nombre del estudiante', 'Porcentaje completado', 'decimas obtenidas']]
            
            # Convertir el DataFrame a una tabla HTML
            table_html = columnas_seleccionadas.to_html(classes='table table-striped', index=False)

            return render_template('index.html', table_html=table_html, filename=filename)
    
    return render_template('index.html', table_html=None)

@app.route('/grafica/<filename>')
def grafica(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(filepath)
    result = {}

    for column in df.columns:
        result[column] = df[column].value_counts().to_dict()

    return render_template('grafica.html', chart_data=result)

if __name__ == '__main__':
    app.run(debug=True)
