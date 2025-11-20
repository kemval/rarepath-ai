import requests
from typing import List, Dict
import xml.etree.ElementTree as ET
import time

class PubMedTool:
    """Tool for searching PubMed medical literature"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
    
    def search(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Search PubMed for articles matching the query
        
        Args:
            query: Search terms (e.g., "Ehlers-Danlos syndrome joint hypermobility")
            max_results: Maximum number of results to return
            
        Returns:
            List of article dictionaries with title, abstract, authors, etc.
        """
        try:
            # Step 1: Search for article IDs
            search_url = f"{self.BASE_URL}esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json',
                'sort': 'relevance'
            }
            
            if self.api_key:
                search_params['api_key'] = self.api_key
            
            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            
            search_results = response.json()
            id_list = search_results.get('esearchresult', {}).get('idlist', [])
            
            if not id_list:
                return []
            
            # Rate limiting - be nice to NCBI servers
            time.sleep(0.34)  # Max 3 requests per second without API key
            
            # Step 2: Fetch article details
            fetch_url = f"{self.BASE_URL}efetch.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(id_list),
                'retmode': 'xml'
            }
            
            if self.api_key:
                fetch_params['api_key'] = self.api_key
            
            fetch_response = requests.get(fetch_url, params=fetch_params, timeout=15)
            fetch_response.raise_for_status()
            
            # Step 3: Parse XML results
            articles = self._parse_pubmed_xml(fetch_response.text)
            
            return articles
            
        except Exception as e:
            print(f"Error searching PubMed: {e}")
            return []
    
    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict]:
        """Parse PubMed XML response into structured data"""
        articles = []
        
        try:
            root = ET.fromstring(xml_text)
            
            for article in root.findall('.//PubmedArticle'):
                try:
                    # Extract title
                    title_elem = article.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None else "No title"
                    
                    # Extract abstract
                    abstract_elem = article.find('.//AbstractText')
                    abstract = abstract_elem.text if abstract_elem is not None else "No abstract available"
                    
                    # Extract PMID
                    pmid_elem = article.find('.//PMID')
                    pmid = pmid_elem.text if pmid_elem is not None else ""
                    
                    # Extract publication year
                    year_elem = article.find('.//PubDate/Year')
                    year = year_elem.text if year_elem is not None else "Unknown"
                    
                    # Extract authors
                    authors = []
                    for author in article.findall('.//Author'):
                        lastname = author.find('LastName')
                        firstname = author.find('ForeName')
                        if lastname is not None and firstname is not None:
                            authors.append(f"{firstname.text} {lastname.text}")
                    
                    articles.append({
                        'pmid': pmid,
                        'title': title,
                        'abstract': abstract,
                        'authors': authors,
                        'year': year,
                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
                    })
                    
                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error parsing XML: {e}")
        
        return articles