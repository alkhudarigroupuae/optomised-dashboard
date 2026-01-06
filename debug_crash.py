import requests
from bs4 import BeautifulSoup

url = "https://omayaclass.com/Products/5/Ar/5"
print(f"Fetching {url}")
try:
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    print(f"Status: {response.status_code}")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Search for link to 790
    target_link = soup.find('a', href=lambda x: x and '790' in x)
    if target_link:
        print("Found link to 790")
        # Find parent block
        # Usually text-block or product-block
        parent = target_link.find_parent(class_='product-block')
        if not parent:
             parent = target_link.find_parent(class_='text-block')
             if parent:
                 print("Found parent text-block")
             else:
                 print("Could not find parent block")
                 print(target_link.parent.parent.prettify())
        
        if parent:
            print(parent.prettify())
    else:
        print("Link to 790 not found on this page")

except Exception as e:
    print(f"Error: {e}")
