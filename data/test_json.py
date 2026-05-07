import json

with open('data/kb.json', 'r', encoding='utf-8') as f:
    content = f.read()

print('Karakter sayisi:', len(content))
print('Ilk 100 karakter:', content[:100])
print('Son 100 karakter:', content[-100:])