import random
import string

class UrlShortner:
    def __init__(self):
        self.url_map = {}
        self.code_map = {}
    
    def _generate_code(self, length=6):
        """Generate code"""
        code = string.ascii_letters + string.digits
        return ''.join(random.choice(code) for _ in range(length))
    
    def short(self, url):
        code = self._generate_code()
        self.url_map[code] = url
        self.code_map[url] = code
        return code 
    
    def redirect(self, code):
        return self.url_map.get(code)


#execution
shortner = UrlShortner()
url = 'wwww.google.com'
shorted_url = shortner.short(url)
print(shorted_url)
longer_url = shortner.redirect(shorted_url)
print(longer_url)
    