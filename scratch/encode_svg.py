import base64
s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="#777780"><path d="M50 20c8.3 0 15 6.7 15 15s-6.7 15-15 15-15-6.7-15-15 6.7-15 15-15zm0 35c16.6 0 30 10 30 20v5H20v-5c0-10 13.4-20 30-20z"/></svg>'
print(base64.b64encode(s.encode('utf-8')).decode('utf-8'))
