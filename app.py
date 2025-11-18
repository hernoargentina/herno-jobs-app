from flask import Flask, render_template, request
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import quote
import re

app = Flask(__name__, template_folder="templates", static_folder="static")

# Scraper para LinkedIn
def scrape_linkedin(query, pages=1):
    resultados = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for page in range(pages):
            url = f"https://www.linkedin.com/jobs/search/?keywords={quote(query)}&start={page*25}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs = soup.find_all('li', class_='base-card')
                
                for job in jobs:
                    try:
                        title_elem = job.find('h3', class_='base-search-card__title')
                        company_elem = job.find('h4', class_='base-search-card__subtitle')
                        link_elem = job.find('a', class_='base-card__full-link')
                        
                        if title_elem and company_elem:
                            resultados.append({
                                'titulo': title_elem.get_text(strip=True),
                                'empresa': company_elem.get_text(strip=True),
                                'url': link_elem.get('href') if link_elem else '#',
                                'fuente': 'LinkedIn',
                                'tipo': 'Publicación de empleo'
                            })
                    except:
                        continue
    except Exception as e:
        print(f"Error scrapeando LinkedIn: {e}")
    
    return resultados

# Scraper para Indeed Argentina
def scrape_indeed(query, pages=1):
    resultados = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for page in range(pages):
            url = f"https://ar.indeed.com/jobs?q={quote(query)}&start={page*10}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs = soup.find_all('div', class_='job_seen_beacon')
                
                for job in jobs:
                    try:
                        title_elem = job.find('h2', class_='jobTitle')
                        company_elem = job.find('span', class_='companyName')
                        link_elem = job.find('a')
                        
                        if title_elem and company_elem:
                            resultados.append({
                                'titulo': title_elem.get_text(strip=True),
                                'empresa': company_elem.get_text(strip=True),
                                'url': f"https://ar.indeed.com{link_elem.get('href')}" if link_elem else '#',
                                'fuente': 'Indeed Argentina',
                                'tipo': 'Publicación de empleo'
                            })
                    except:
                        continue
    except Exception as e:
        print(f"Error scrapeando Indeed: {e}")
    
    return resultados

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/buscar", methods=["POST"])
def buscar():
    query = request.form.get("query")
    paginas = int(request.form.get("paginas", 1))
    
    if not query:
        return render_template(
            "resultado.html",
            query=query,
            resultados=[],
            total=0,
            error="Por favor ingresa una palabra clave"
        )
    
    try:
        # Ejecutar ambos scrapers
        resultados_linkedin = scrape_linkedin(query, paginas)
        resultados_indeed = scrape_indeed(query, paginas)
        
        # Combinar resultados
        resultados = resultados_linkedin + resultados_indeed
        
        return render_template(
            "resultado.html",
            query=query,
            resultados=resultados,
            total=len(resultados)
        )
    
    except Exception as e:
        return render_template(
            "resultado.html",
            query=query,
            resultados=[],
            total=0,
            error=f"Error durante la búsqueda: {str(e)}"
        )

if __name__ == "__main__":
    app.run(debug=True)
