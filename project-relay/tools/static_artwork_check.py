#!/usr/bin/env python3
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[2]
html=ROOT/'index.html'
required=['Upload failed','Sending the message failed','Connection attempt failed','Reconnecting…','Failed','Do you want to report the problem?','Reporting the problem…','Reporting failed']
errors=[]
if not html.is_file(): errors.append('index.html missing')
else:
    text=html.read_text(encoding='utf-8')
    for line in required:
        if line not in text: errors.append('missing locked line: '+line)
    if re.search(r'<script[^>]+src=["\']https?://|<link[^>]+href=["\']https?://',text,re.I): errors.append('external runtime asset found')
if errors:
    print('STATIC_ARTWORK_FAIL'); [print('-',e) for e in errors]; sys.exit(1)
print('STATIC_ARTWORK_PASS')
