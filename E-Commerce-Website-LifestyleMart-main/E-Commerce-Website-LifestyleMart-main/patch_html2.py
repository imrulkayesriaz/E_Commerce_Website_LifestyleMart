import os
import glob
import re

for filepath in glob.glob('templates/*.html'):
    if 'product.html' in filepath or 'cart.html' in filepath:
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    new_content = re.sub(
        r'\s*<select name=\"size\" class=\"form-select form-select-sm mb-2\"[^>]*>.*?<\/select>', 
        '', 
        content, 
        flags=re.DOTALL
    )
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('Removed select from', filepath)
