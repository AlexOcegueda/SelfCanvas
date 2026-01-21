from bs4 import BeautifulSoup

def parse_mit_assignments(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    main_section = soup.find(id='course-content-section')
    if not main_section:
        return {"error": "Could not find course-content-section"}
        
    table = main_section.find('table')
    if not table:
        return {"error": "No assignment table found"}

    assignments = []
    rows = table.find_all('tr')
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            title = cols[0].get_text(strip=True)
            description = cols[1].get_text(separator='\n', strip=True)
            assignments.append({"title": title, "content": description})

    return assignments