from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import quote

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

def scrape_indeed(query, pages=1):
    """
    Scraper real para Indeed Argentina
    Busca empleos en indeed.com.ar
    """
    resultados = []
    try:
        for page in range(pages):
            start = page * 10
            url = f"https://ar.indeed.com/jobs?q={quote(query)}&start={start}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar tarjetas de empleos en Indeed
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            for job_card in job_cards:
                try:
                    # Extrae información del empleo
                    title_elem = job_card.find('h2', class_='jobTitle')
                    company_elem = job_card.find('span', class_='companyName')
                    location_elem = job_card.find('div', class_='companyLocation')
                    description_elem = job_card.find('div', class_='job-snippet')
                    link_elem = job_card.find('a', class_='jcs-ExpressionAttributeUL')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "No especificada"
                        location = location_elem.get_text(strip=True) if location_elem else "No especificada"
                        description = description_elem.get_text(strip=True)[:200] if description_elem else ""
                        link = link_elem.get('href', '#') if link_elem else '#'
                        if not link.startswith('http'):
                            link = 'https://ar.indeed.com' + link
                        
                        resultados.append({
                            'title': title,
                            'company': company,
                            'location': location,
                            'description': description,
                            'link': link,
                            'source': 'Indeed'
                        })
                except:
                    continue
    except:
        pass
    
    return resultados

def scrape_linkedin(query, pages=1):
    """
    Scraper para LinkedIn (búsqueda básica)
    Retorna resultados simulados para demostración
    """
    resultados = []
    try:
        # LinkedIn bloquea scrapers, retornamos URL de búsqueda directa
        url = f"https://www.linkedin.com/jobs/search/?keywords={quote(query)}&location=Argentina"
        resultados.append({
            'title': f'Búsqueda en LinkedIn - {query}',
            'company': 'LinkedIn',
            'location': 'Argentina',
            'description': 'Haz clic para ver ofertas de empleo en LinkedIn',
            'link': url,
            'source': 'LinkedIn'
        })
    except:
        pass
    
    return resultados

@app.route("/buscar", methods=["POST"])
def buscar():
    query = request.form.get("query", "").strip()
    paginas = int(request.form.get("paginas", 1))
    
    if not query:
        return render_template(
            "resultado.html",
            query="",
            resultados=[],
            total=0
        )
    
    try:
        # Buscar en Indeed
        resultados_indeed = scrape_indeed(query, paginas)
        
        # Buscar en LinkedIn
        resultados_linkedin = scrape_linkedin(query, paginas)
        
        # Combinar resultados
        resultados = resultados_indeed + resultados_linkedin
        
    except Exception as e:
        resultados = []
        print(f"Error en búsqueda: {e}")
    
    return render_template(
        "resultado.html",
        query=query,
        resultados=resultados,
        total=len(resultados)
    )

if __name__ == "__main__":
    app.run(debug=False)
