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
    """Scrape jobs from Indeed Argentina"""
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        for page in range(pages):
            url = f"https://ar.indeed.com/jobs?q={quote(query)}&start={page*10}"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = soup.find_all('div', class_='job_seen')
            
            for job in jobs:
                try:
                    title_elem = job.find('h2', class_='jobTitle')
                    title = title_elem.get_text(strip=True) if title_elem else 'N/A'
                    
                    company_elem = job.find('span', class_='companyName')
                    company = company_elem.get_text(strip=True) if company_elem else 'N/A'
                    
                    location_elem = job.find('div', class_='companyLocation')
                    location = location_elem.get_text(strip=True) if location_elem else 'N/A'
                    
                    link_elem = job.find('h2').find('a')
                    link = 'https://ar.indeed.com' + link_elem['href'] if link_elem else '#'
                    
                    results.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'description': 'Ver detalles en Indeed'
                    })
                except Exception as e:
                    continue
    except Exception as e:
        print(f"Error scraping Indeed: {e}")
    
    return results

def scrape_linkedin(query, pages=1):
    """Return LinkedIn search link (LinkedIn blocks scrapers)"""
    return [{
        'title': 'Buscar en LinkedIn',
        'company': 'LinkedIn',
        'location': 'Argentina',
        'link': f'https://www.linkedin.com/jobs/search/?keywords={quote(query)}&location=Argentina',
        'description': 'Resultados de LinkedIn'
    }]

@app.route("/buscar", methods=["POST"])
def buscar():
    query = request.form.get("query")
    paginas = int(request.form.get("paginas", 1))
    
    try:
        # Get results from Indeed
        indeed_results = scrape_indeed(query, paginas)
        # Get LinkedIn link
        linkedin_results = scrape_linkedin(query)
        # Combine results
        resultados = indeed_results + linkedin_results
    except Exception as e:
        return f"<h2>Error en la búsqueda:</h2><pre>{e}</pre>"
    
    return render_template(
        "resultado.html",
        query=query,
        resultados=resultados,
        titulo=f"Resultados - {query}"
    )
