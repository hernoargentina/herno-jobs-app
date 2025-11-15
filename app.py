from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/buscar", methods=["POST"])
def buscar():
    query = request.form.get("query")
    paginas = int(request.form.get("paginas", 1))
    
    # URL de tu PROXY EN RENDER
    PROXY_URL = "https://flask-hello-world-7ck3.onrender.com/scrape"
    
    try:
        # Realizar peticion al proxy con timeout
        r = requests.post(
            PROXY_URL,
            json={"query": query, "pages": paginas},
            timeout=30
        )
        
        # Validar que la respuesta HTTP sea exitosa
        if r.status_code != 200:
            return f"<h2>Error del proxy (HTTP {r.status_code}):</h2><pre>El servidor proxy no responde correctamente. Por favor, inténtalo más tarde.</pre>"
        
        # Validar que la respuesta tenga contenido
        if not r.text or r.text.strip() == "":
            return f"<h2>Error: Respuesta vacía del proxy</h2><pre>El servidor proxy no devuelve datos. Esto puede suceder si está en mantenimiento o inactivo en Render. Por favor, inténtalo más tarde.</pre>"
        
        # Intentar parsear JSON con manejo de error específico
        try:
            raw = r.json()
        except json.JSONDecodeError as je:
            return f"<h2>Error al procesar respuesta del proxy:</h2><pre>Respuesta inválida: {str(je)}</pre><p>Contenido recibido: {r.text[:200]}</p>"
        
    except requests.Timeout:
        return f"<h2>Error de timeout:</h2><pre>El servidor proxy tardó más de 30 segundos en responder. Por favor, inténtalo más tarde.</pre>"
    except requests.ConnectionError:
        return f"<h2>Error de conexión:</h2><pre>No se puede conectar al servidor proxy. Verifica que el URL sea correcto: {PROXY_URL}</pre>"
    except Exception as e:
        return f"<h2>Error inesperado:</h2><pre>{type(e).__name__}: {str(e)}</pre>"
    
    # Extraer y limpiar resultados
    resultados = raw.get("results", [])
    limpios = []
    
    for item in resultados:
        if isinstance(item, dict):
            limpios.append(item)
        else:
            try:
                limpios.append(json.loads(item))
            except:
                continue
    
    # Renderizar template con resultados
    return render_template(
        "resultado.html",
        query=query,
        resultados=limpios,
        total=len(limpios)
    )

if __name__ == "__main__":
    app.run(debug=True)
