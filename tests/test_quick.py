# test_quick.py
import asyncio
from config import Config
from tools.pubmed_tool import PubMedTool

async def test_pubmed():
    tool = PubMedTool()
    results = tool.search("Ehlers-Danlos syndrome joint hypermobility", max_results=3)
    
    print(f"Found {len(results)} articles:")
    for article in results:
        print(f"\n- {article['title']}")
        print(f"  PMID: {article['pmid']}")
        print(f"  Year: {article['year']}")

asyncio.run(test_pubmed())