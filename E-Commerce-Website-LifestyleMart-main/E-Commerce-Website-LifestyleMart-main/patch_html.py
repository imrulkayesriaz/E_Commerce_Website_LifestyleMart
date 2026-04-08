import os
import glob

SIZE_HTML = """<input type="hidden" name="quantity" value="1">
                        <select name="size" class="form-select form-select-sm mb-2" style="font-size: 0.8rem; padding: 0.25rem 0.5rem;" required>
                            <option value="" disabled selected>Select Size</option>
                            <option value="S">S</option>
                            <option value="M">M</option>
                            <option value="L">L</option>
                            <option value="XL">XL</option>
                            <option value="XXL">XXL</option>
                        </select>"""

for filepath in glob.glob('templates/*.html'):
    if 'cart.html' in filepath:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        target = '<h6>{{ item.product.name }}</h6>'
        replacement = '<h6>{{ item.product.name }}</h6>\n                                {% if item.size %}\n                                <p class="text-muted mb-1">Size: <strong>{{ item.size }}</strong></p>\n                                {% endif %}'
        
        if target in content and '{% if item.size %}' not in content:
            content = content.replace(target, replacement)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print('patched', filepath)
            
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        old_input = '<input type="hidden" name="quantity" value="1">'
        
        if old_input in content:
            content = content.replace(old_input, SIZE_HTML)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print('patched', filepath)
