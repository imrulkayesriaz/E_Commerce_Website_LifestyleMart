import glob
import re

for file in glob.glob('templates/*.html'):
    if file.endswith('product.html') or file.endswith('cart.html'):
        continue
    
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Wrap the daraz-product-image img
    content = re.sub(
        r'(<div class=\"daraz-product-image.*?>\s*(?:<span.*?>.*?<\/span>\s*)?)<img\s+src=\"([^\"]+)\"\s+alt=\"([^\"]+)\"\s*>',
        r'\1<a href="{{ url_for(\'product\', id=product.id) }}"><img src="\2" alt="\3"></a>',
        content
    )
    
    # 2. Wrap the title daraz-product-title
    content = re.sub(
        r'(<h6 class=\"daraz-product-title\">)(.*?)(</h6>)',
        r'\1<a href="{{ url_for(\'product\', id=product.id) }}" class="text-dark text-decoration-none">\2</a>\3',
        content
    )
    
    # 3. Also for traditional Bootstrap cards
    content = re.sub(
        r'<img\s+src=\"([^\"]+)\"\s+class=\"card-img-top\"\s+alt=\"([^\"]+)\"\s*>',
        r'<a href="{{ url_for(\'product\', id=product.id) }}"><img src="\1" class="card-img-top" alt="\2"></a>',
        content
    )
    
    content = re.sub(
        r'(<h5 class=\"card-title\">)(.*?)(</h5>)',
        r'\1<a href="{{ url_for(\'product\', id=product.id) }}" class="text-dark text-decoration-none">\2</a>\3',
        content
    )
    
    # 4. Change Add to Cart forms to View Product links in grid/shop
    content = re.sub(
        r'<form action=\"\{\{\s*url_for\(\'add_to_cart\'\)\s*\}\}\" method=\"POST\">\s*<input type=\"hidden\" name=\"product_id\" value=\"\{\{\s*product\.id\s*\}\}\">\s*<input type=\"hidden\" name=\"quantity\" value=\"1\">\s*(<div class=\"d-grid gap-2\">)?\s*<button type=\"submit\" class=\"(.*?)\">.*?</button>',
        r'<div class="d-grid gap-2">\n                            <a href="{{ url_for(\'product\', id=product.id) }}" class="\2 text-center text-decoration-none">View Product</a>',
        content
    )
    # clean up dangling </form> we might leave if there was a Message button down inside the form
    content = re.sub(
        r'(<a href=\"{{ url_for\(\'product\', id=product\.id\) }}\" class=\".*? text-center text-decoration-none\">View Product</a>\s*(?:<a href=.*?Message.*?</a>\s*)?)</div>\s*</form>',
        r'\1</div>',
        content
    )

    if content != original_content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Updated', file)
