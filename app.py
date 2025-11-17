from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__, template_folder="templates", static_folder="static")

# Simulación de scraper para Indeed
def scrape_indeed(query, pages=1):
    """
    Scraper simplificado para Indeed.
    Por limitaciones de scraping, retorna datos de ejemplo realistas.
    """
    try:
        results = []

        # Datos de ejemplo - en producción, usar Selenium o API válida
        sample_jobs = [
            {
                "title": f"Especialista en {query.upper()} - Buenos Aires",
                "company": "Tech Argentina SA",
                "location": "Buenos Aires, CABA",
                "salary": "$80.000 - $120.000",
                "description": f"Buscamos profesional con experiencia en {query}.",
                "link": "https://indeed.com/jobs",
                "source": "Indeed"
            },
            {
                "title": f"Developer {query.upper()} Senior",
                "company": "Innovation Labs",
                "location": "Córdoba",
                "salary": "$100.000 - $150.000",
                "description": f"Empresa en crecimiento busca {query} senior.",
                "link": "https://indeed.com/jobs",
                "source": "Indeed"
            }
        ]

        # Repetir resultados según páginas solicitadas
        for page in range(pages):
            for job in sample_jobs:
                results.append({
                    **job,
                    "page": page + 1,
                    "retrieved_at": "2024-01-15T10:30:00"
                })

        return results
    except Exception as e:
        return {"error": str(e)}


def scrape_linkedin(query, pages=1):
    """
    Scraper simplificado para LinkedIn.
    Por limitaciones de scraping, retorna datos de ejemplo realistas.
    """
    try:
        results = []

        sample_jobs = [
            {
                "title": f"Analista {query.upper()}",
                "company": "Enterprise Solutions",
                "location": "La Plata",
                "salary": "$70.000 - $100.000",
                "description": f"Posición de {query} en empresa líder del sector.",
                "link": "https://linkedin.com/jobs",
                "source": "LinkedIn"
            },
            {
                "title": f"{query.upper()} Engineer",
                "company": "Digital Transformation Co",
                "location": "Mendoza",
                "salary": "$90.000 - $130.000",
                "description": f"Ingeniero/a con expertise en {query} requerido/a.",
                "link": "https://linkedin.com/jobs",
                "source": "LinkedIn"
            }
        ]

        for page in range(pages):
            for job in sample_jobs:
                results.append({
                    **job,
                    "page": page + 1,
                    "retrieved_at": "2024-01-15T10:30:00"
                })

        return results
    except Exception as e:
        return {"error": str(e)}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/buscar", methods=["POST"])
def buscar():
    query = request.form.get("query", "").strip()
    páginas = int(request.form.get("páginas", 1))

    # Validación básica
    if not query:
        return render_template("resultado.html", query=query, resultados=[], total=0, error="Por favor ingresa una palabra clave")

    if páginas < 1 or páginas > 10:
        páginas = 1

    try:
        # Scrapers integrados - sin proxy externo
        indeed_results = scrape_indeed(query, páginas)
        linkedin_results = scrape_linkedin(query, páginas)

        # Combinar resultados
        results = indeed_results + linkedin_results

        return render_template(
            "resultado.html",
            query=query,
            resultados=results,
            total=len(results),
            error=None
        )

    except Exception as e:
        return render_template(
            "resultado.html",
            query=query,
            resultados=[],
            total=0,
            error=f"Error en la búsqueda: {str(e)}"
        )


if __name__ == "__main__":
    app.run()
