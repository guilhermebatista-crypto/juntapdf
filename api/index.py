import io
import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from pypdf import PdfReader, PdfWriter

# Aponta a pasta de templates para a raiz do projeto
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.environ.get("SECRET_KEY", "chave_secreta_padrao")

app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("pdf_files")

        valid_files = [
            f for f in files 
            if f and f.filename and f.filename.lower().endswith(".pdf")
        ]

        if len(valid_files) < 2:
            flash("Selecione pelo menos 2 arquivos PDF para juntar.", "error")
            return redirect(url_for("index"))

        try:
            writer = PdfWriter()

            for file in valid_files:
                reader = PdfReader(file.stream)
                for page in reader.pages:
                    writer.add_page(page)

            output_stream = io.BytesIO()
            writer.write(output_stream)
            writer.close()
            output_stream.seek(0)

            return send_file(
                output_stream,
                mimetype="application/pdf",
                as_attachment=True,
                download_name="documento_unificado.pdf"
            )

        except Exception as e:
            flash(f"Ocorreu um erro ao processar os arquivos: {str(e)}", "error")
            return redirect(url_for("index"))

    return render_template("index.html")

# O Vercel busca a variável `app` diretamente, dispensa app.run() em produção
if __name__ == "__main__":
    app.run(debug=True)