import json
import re
from bs4 import BeautifulSoup

def parse_mit_json(json_content):
    # (No changes here, kept for completeness)
    try:
        data = json.loads(json_content)
        assignments = []
        if isinstance(data, dict) and 'content' in data:
            raw_text = data['content']
            parts = re.split(r'(Problem set \d+)', raw_text)
            for i in range(1, len(parts), 2):
                assignments.append({
                    "title": parts[i].strip(),
                    "content": parts[i+1].strip()
                })
            return assignments
        iterable = data if isinstance(data, list) else data.get('items', [])
        for item in iterable:
            title = item.get('title') or item.get('label') or "Untitled"
            description = item.get('description') or item.get('summary') or ""
            if any(x in str(title).lower() for x in ['assignment', 'problem set', 'exam']):
                assignments.append({"title": str(title), "content": str(description)})
        return assignments
    except Exception as e:
        print(f"JSON Parsing Error: {e}")
        return []

def parse_mit_assignments(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    assignments = []

    # === STEP 0: FIND THE REAL ONLINE URL ===
    base_url = "https://ocw.mit.edu"
    meta_url = soup.find("meta", property="og:url")
    
    course_home_url = ""
    if meta_url and meta_url.get("content"):
        full_meta = meta_url.get("content")
        if "/courses/" in full_meta:
            parts = full_meta.split('/courses/')
            if len(parts) > 1:
                slug = parts[1].split('/')[0] 
                course_home_url = f"https://ocw.mit.edu/courses/{slug}/"

    if not course_home_url:
        course_home_url = "https://ocw.mit.edu/"

    # --- STRATEGY 1: RESOURCE ITEMS ---
    resource_items = soup.find_all(class_='resource-item')
    
    if resource_items:
        for item in resource_items:
            title_tag = item.find(class_='resource-list-title')
            if not title_tag: continue
            title = title_tag.get_text(strip=True)
            
            parent = item.find_parent(class_='collapse')
            category = "Resource"
            if parent and parent.get('id'):
                cat_id = parent.get('id')
                category = cat_id.replace('resource-list-container-', '').replace('-', ' ').title()

            thumb_link = item.find('a', class_='resource-thumbnail')
            href = thumb_link.get('href', '') if thumb_link else title_tag.get('href', '')

            # === KEY FIX: HANDLE ABSOLUTE URLS ===
            final_link = ""
            
            # 1. If it's already a full web address, USE IT AS IS.
            if href.startswith('http') or href.startswith('//'):
                final_link = href
            
            # 2. If it's a static resource (PDFs inside zip), re-route to course home
            elif "static_resources" in href:
                filename = href.split('/')[-1]
                final_link = f"{course_home_url}{filename}"
                
            # 3. If it's a relative course link
            elif "courses" in href:
                clean_path = href.replace('..', '')
                if clean_path.startswith('/'):
                    final_link = f"https://ocw.mit.edu{clean_path}"
                else:
                    final_link = f"https://ocw.mit.edu/{clean_path}"
            
            # 4. Unknown relative link
            else:
                clean_path = href.replace('..', '').replace('/', '', 1)
                final_link = f"{course_home_url}{clean_path}"

            assignments.append({
                "title": f"[{category}] {title}",
                "content": final_link
            })
            
        return assignments

    # --- STRATEGY 2: TABLE PARSING ---
    main_section = soup.find(id='course-content-section') or soup.find('body')
    table = main_section.find('table')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                title = cols[0].get_text(strip=True)
                desc = cols[1].get_text(separator='\n', strip=True)
                if title and "Assn" not in title:
                    assignments.append({"title": title, "content": desc})
        if assignments: return assignments

    # --- STRATEGY 3: GENERIC LINKS ---
    links = main_section.find_all('a')
    for link in links:
        text = link.get_text(strip=True)
        href = link.get('href', '')
        if any(k in text.lower() for k in ['assignment', 'problem set', 'exam']):
            
            # Also fix generic links here
            if href.startswith('http'):
                 final_link = href
            else:
                 clean_path = href.replace('..', '')
                 final_link = f"https://ocw.mit.edu{clean_path}"
                 
            assignments.append({
                "title": text.replace("(PDF)", "").strip(),
                "content": final_link
            })

    return assignments