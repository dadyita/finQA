import json
import re

output_path = "economics.html"
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


def balanced_parentheses(text):
    count = 0
    result = ''
    for c in text:
        if c == '{':
            count += 1
        elif c == '}':
            count -= 1
        result += c
        if count == 0:
            break
    return result


with open('output/economics_formula_list.json', encoding='utf8') as f:
    data = json.load(f)
latex_count = len(data)
html_str += f"<h1>{latex_count} formulas</h1>"

for page_name in data:
    example = data[page_name]
    url = page_name.replace(" ", "_")
    html_str += f"<a href = {url}>{url}</a>"
    if "text_formula" in example:
        text = example['text_formula']
        html_str += f'<h3>Text Formula</h3>'
        for i, text_str in enumerate(text):
            if "<div" in text_str:
                continue
            html_str += f'<p>{text_str}</p>'

    if "latex_formula" in example:
        latex = example['latex_formula']
        html_str += f'<h3>Latex Formula</h3>'
        # write them to an HTML format
        for i, latex_str in enumerate(latex):
            if "{\\displaystyle" not in latex_str:
                html_str += f'<p>{latex_str}</p>'
            else:
                pattern = r'{\\displaystyle'
                text = latex_str

                while re.search(pattern, text):
                    match = re.search(pattern, text)
                    if match:
                        start = match.start()
                        content = balanced_parentheses(text[start:])
                        content_with_dollar = content.replace("{\\displaystyle", "")[:-1]
                        text = text[:start] + f"${content_with_dollar}$" + text[start + len(content):]
                html_str += f'<p>{text}</p>'

    html_str += "<hr>"

html_str += """
</body>
</html>
"""

with open(output_path, 'w', encoding='utf8') as f:
    f.write(html_str)
