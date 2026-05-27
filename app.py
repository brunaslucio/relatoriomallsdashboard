import os, io, shutil, logging
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from services.excel_service import ExcelService
from services.pptx_service import PPTXService
from services.ai_service import AIService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s – %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for d in ["data", "templates"]:
    os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)

# Copiar frontend para dist
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "dist")
os.makedirs(STATIC_DIR, exist_ok=True)
_src = os.path.join(BASE_DIR, "frontend", "index.html")
if os.path.exists(_src):
    shutil.copy(_src, os.path.join(STATIC_DIR, "index.html"))

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB

DATA_FOLDER = os.environ.get("DATA_FOLDER", os.path.join(BASE_DIR, "data"))
TEMPLATES_FOLDER = os.environ.get("TEMPLATES_FOLDER", os.path.join(BASE_DIR, "templates"))

excel_svc = ExcelService(DATA_FOLDER)
pptx_svc = PPTXService(TEMPLATES_FOLDER)
ai_svc = AIService()


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/status")
def status():
    excel_path = os.path.join(DATA_FOLDER, os.environ.get("EXCEL_FILENAME", "dados.xlsx"))
    tmpl_path = os.path.join(TEMPLATES_FOLDER, os.environ.get("TEMPLATE_FILENAME", "template.pptx"))
    ctx = {}
    try:
        if os.path.exists(excel_path):
            ctx = excel_svc.get_context_data()
    except Exception as e:
        logger.warning(f"Could not read context: {e}")
    return jsonify({
        "success": True,
        "excel_loaded": os.path.exists(excel_path),
        "template_loaded": os.path.exists(tmpl_path),
        "mes_referencia": ctx.get("mes_referencia", ""),
        "abl_atual": ctx.get("abl_atual"),
    })


@app.route("/api/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(force=True) or {}
        include_ai = data.get("include_ai_comments", True)
        custom_context = data.get("custom_context", "")

        logger.info(f"Iniciando geração — ai={include_ai}")

        # 1. Contexto de dados
        ctx = excel_svc.get_context_data()
        mes = ctx.get("mes_referencia", "")
        logger.info(f"  Mês de referência: {mes}")

        # 2. Extrair tabelas
        tables = excel_svc.extract_tables()
        logger.info(f"  {len(tables)} tabelas extraídas")

        # 3. Extrair gráficos
        charts = excel_svc.extract_charts()
        logger.info(f"  {len(charts)} gráficos extraídos")

        # 4. Gerar comentários IA
        comments = {}
        if include_ai:
            if custom_context:
                ctx["custom_context"] = custom_context
            comments = ai_svc.generate_all_comments(ctx, tables, charts)
            logger.info(f"  {len(comments)} comentários gerados")

        # 5. Montar PPTX
        pptx_bytes = pptx_svc.generate_report(
            charts=charts,
            tables=tables,
            comments=comments,
            month=mes,
        )
        logger.info(f"  PPTX gerado: {len(pptx_bytes):,} bytes")

        mes_file = mes.replace(" ", "_").replace("/", "-") if mes else "relatorio"
        filename = f"Riza_Malls_{mes_file}.pptx"

        return send_file(
            io.BytesIO(pptx_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            as_attachment=True,
            download_name=filename,
        )

    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        logger.error(f"generate error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/upload/excel", methods=["POST"])
def upload_excel():
    try:
        f = request.files.get("file")
        if not f:
            return jsonify({"success": False, "error": "Arquivo não enviado"}), 400
        if not f.filename.lower().endswith((".xlsx", ".xls")):
            return jsonify({"success": False, "error": "Use .xlsx ou .xls"}), 400
        path = os.path.join(DATA_FOLDER, "dados.xlsx")
        os.makedirs(DATA_FOLDER, exist_ok=True)
        f.save(path)
        logger.info(f"Excel salvo: {path}")
        ctx = excel_svc.get_context_data()
        return jsonify({
            "success": True,
            "message": "Excel atualizado com sucesso",
            "mes_referencia": ctx.get("mes_referencia", ""),
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/upload/template", methods=["POST"])
def upload_template():
    try:
        f = request.files.get("file")
        if not f:
            return jsonify({"success": False, "error": "Arquivo não enviado"}), 400
        if not f.filename.lower().endswith(".pptx"):
            return jsonify({"success": False, "error": "Use .pptx"}), 400
        path = os.path.join(TEMPLATES_FOLDER, "template.pptx")
        os.makedirs(TEMPLATES_FOLDER, exist_ok=True)
        f.save(path)
        return jsonify({"success": True, "message": "Template atualizado com sucesso"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
