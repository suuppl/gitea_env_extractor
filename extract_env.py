from bs4 import BeautifulSoup
import re
import yaml

def extract_h2_with_li_children(html_file_path):
    """
    Extracts all <h2> elements and their associated <li> children from an HTML file.

    :param html_file_path: Path to the HTML file.
    :type html_file_path: str
    :return: A list of dictionaries, each containing the h2 text and a list of li texts.
    :rtype: list[dict]
    """
    results = []
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

        for h2 in soup.find_all('h2'):
            section = {'h2': h2.get_text(strip=True), 'li': []}
            # Find the next sibling that is a <ul> or <ol>
            next_sibling = h2.find_next_sibling()
            while next_sibling and next_sibling.name not in ['ul', 'ol']:
                next_sibling = next_sibling.find_next_sibling()
            if next_sibling and next_sibling.name in ['ul', 'ol']:
                for li in next_sibling.find_all('li'):
                    code_text = ''
                    strong_text = ''
                    rest_text = li.get_text(strip=True)
                    code_tag = li.find('code')
                    strong_tag = li.find('strong')
                    if code_tag:
                        code_text = code_tag.get_text(strip=True)
                        rest_text = rest_text.replace(code_text, '', 1).strip()
                    if strong_tag:
                        strong_text = strong_tag.get_text(strip=True)
                        rest_text = rest_text.replace(strong_text, '', 1).strip()
                    rest_text = rest_text.lstrip(': ')
                    section['li'].append([code_text, strong_text, rest_text])
            results.append(section)
    
    for section in results:
        match = re.search(r'\((.*?)\)', section['h2'])
        if match:
            section['h2'] = match.group(1)
        # else:
            # section['h2'] = ''

    return results

def transform(results:list):
    out = ""

    for section in results:
        out += "#"*40
        out += "\n"
        out += f"# {section['h2']:^36} #"
        out += "\n"
        out += "#"*40
        out += "\n"
        for key, value, comment in section['li']:
            out += "\n"
            for line in comment.splitlines():
                out += f"# {line}\n"
            def is_valid_yaml_value(val):
                """
                Checks if a value is a valid YAML scalar (int, float, bool, or simple string).

                :param val: The value to check.
                :type val: str
                :return: True if valid, False if needs quoting.
                :rtype: bool
                """
                # Try to parse with yaml.safe_load, and check if it is a scalar
                try:
                    loaded = yaml.safe_load(val)
                    # Accept int, float, bool, None, or simple string without special chars
                    if isinstance(loaded, (int, float, bool)) or loaded is None:
                        return True
                    if isinstance(loaded, str):
                        # If string contains special YAML chars, needs quoting
                        if any(c in loaded for c in [':', '{', '}', '[', ']', ',', '&', '*', '#', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`', '"', "'"]):
                            return False
                        if loaded.strip() != loaded or loaded == '' or loaded.lower() in ['null', 'true', 'false', '~']:
                            return False
                        return True
                    return False
                except Exception:
                    return False

            if not is_valid_yaml_value(value):
                value = f'"{value}"'
            out += f"# GITEA__{section['h2']}__{key}: {value}\n"
        out += "\n"
    return out

if __name__ == "__main__":
    """
    Calls extract_h2_with_li_children with 'gitea.html' and prints the results.
    """
    results = extract_h2_with_li_children('gitea.html')
    yaml = transform(results=results)
    print(yaml)
    with open('gitea.env', 'w', encoding='utf-8') as f:
        f.write(yaml)