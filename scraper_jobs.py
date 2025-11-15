import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class JobScraper:
    """Scraper integrado para búsqueda de empleos sin dependencia de proxy externo"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.resultados_cache = {}
    
    def scrape_indeed(self, query, pages=1):
        """Busca empleos en Indeed usando BS4"""
        resultados = []
        try:
            for page in range(pages):
                url = f"https://ar.indeed.com/jobs?q={query}&start={page*10}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs = soup.find_all('div', class_='job_seen_beacon')
                
                for job in jobs[:10]:
                    try:
                        titulo = job.find('h2', class_='jobTitle')
                        empresa = job.find('span', class_='companyName')
                        ubicacion = job.find('div', class_='companyLocation')
                        resumen = job.find('div', class_='job-snippet')
                        link = job.find('a', class_='jcs-JobTitle')
                        
                        if titulo and empresa:
                            item = {
                                'titulo': titulo.get_text(strip=True),
                                'empresa': empresa.get_text(strip=True),
                                'ubicacion': ubicacion.get_text(strip=True) if ubicacion else 'No especificada',
                                'resumen': resumen.get_text(strip=True) if resumen else '',
                                'url': f"https://ar.indeed.com{link['href']}" if link else '',
                                'fuente': 'Indeed',
                                'fecha': datetime.now().isoformat()
                            }
                            resultados.append(item)
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"Error scrapeando Indeed: {e}")
        
        return resultados
    
    def scrape_linkedin_search(self, query, pages=1):
        """Busca empleos - nota: LinkedIn requiere autenticación para scraping completo"""
        # LinkedIn restringe web scraping. Retornamos resultado de demostración
        resultados = []
        try:
            # Este es un endpoint público limitado
            url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{query}"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                # LinkedIn retorna JSON en ciertos endpoints
                data = response.json() if response.text else {}
        except:
            pass
        
        return resultados
    
    def buscar(self, query, pages=1, fuentes=['indeed']):
        """Método principal de búsqueda"""
        todos_resultados = []
        
        if 'indeed' in fuentes:
            resultados_indeed = self.scrape_indeed(query, pages)
            todos_resultados.extend(resultados_indeed)
        
        if 'linkedin' in fuentes:
            resultados_linkedin = self.scrape_linkedin_search(query, pages)
            todos_resultados.extend(resultados_linkedin)
        
        return {
            'query': query,
            'total': len(todos_resultados),
            'resultados': todos_resultados,
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    scraper = JobScraper()
    resultado = scraper.buscar('Analyst', pages=1)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
