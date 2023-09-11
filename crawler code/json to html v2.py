import html
import json
import re

output_path = "formula.html"
html_str = """
<!DOCTYPE html>
<html>
<head>
    <script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>

    <script type="text/x-mathjax-config">
    MathJax.Hub.Config({
        tex2jax: {inlineMath: [['$', '$']]},
        messageStyle: "none"
    });
    </script>   
</head>
<body>
"""


def balanced_parentheses(t):
    count = 0
    result = ''
    for c in t:
        if c == '{':
            count += 1
        elif c == '}':
            count -= 1
        result += c
        if count == 0:
            break
    return result


with open('formula.json', encoding='utf8') as f:
    data = json.load(f)
latex_count = len(data)
html_str += f"<h1>{latex_count} formulas</h1>"

for formula in data:
    html_str += "<hr>"
    if "{\\displaystyle" not in formula:
        html_str += f'<h4>{html.escape(formula)}</h4>'
    else:
        pattern = r'{\\displaystyle'
        text = formula

        while re.search(pattern, text):
            match = re.search(pattern, text)
            if match:
                start = match.start()
                content = balanced_parentheses(text[start:])
                content_with_dollar = content.replace("{\\displaystyle", "")[:-1]
                text = text[:start] + f"${content_with_dollar}$" + text[start + len(content):]
        html_str += f'<h4>{html.escape(text)}</h4>'
    flag = 0
    a = ['Before', 'After', 'Url']
    # write them to an HTML format
    for item in data[formula]:
        add_str = data[formula][item]
        html_str += f'<b>' + a[flag] + '</b>'
        flag += 1
        if flag != 3:
            if "{\\displaystyle" not in add_str:
                html_str += f'<p>{html.escape(add_str)}</p>'
            else:
                pattern = r'{\\displaystyle'
                text = add_str

                while re.search(pattern, text):
                    match = re.search(pattern, text)
                    if match:
                        start = match.start()
                        content = balanced_parentheses(text[start:])
                        content_with_dollar = content.replace("{\\displaystyle", "")[:-1]
                        text = text[:start] + f"${content_with_dollar}$" + text[start + len(content):]
                html_str += f'<p>{html.escape(text)}</p>'
        else:
            url = add_str.replace(" ", "_")
            html_str += f"<p></p><a href = {html.escape(url)}>{html.escape(url)}</a>"

html_str += "<hr>"

html_str += """
</body>
</html>
"""

with open(output_path, 'w', encoding='utf8') as f:
    f.write(html_str)
