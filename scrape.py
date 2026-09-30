import re,json,time,html
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
BASE='https://www.boatrace.jp/owpc/pc/data/racersearch/result'
s=requests.Session();s.headers.update({'User-Agent':'Mozilla/5.0 (compatible; BOATRACE-Sukigao9/1.0)'})
items={}
for lo in range(0,5600,100):
    hi=lo+99
    try:
        r=s.get(BASE,params={'prevpgid':'TDAT320','toban_left':f'{lo:04d}','toban_right':f'{hi:04d}'},timeout=30)
        r.raise_for_status(); soup=BeautifulSoup(r.text,'html.parser')
    except Exception as e:
        print('skip',lo,hi,e); continue
    # The official result page presents racer number/name/grade and links the photo to the profile.
    for a in soup.find_all('a',href=True):
        href=a['href']
        if 'racersearch/profile' not in href: continue
        img=a.find('img')
        if not img: continue
        src=img.get('src') or img.get('data-src')
        if not src: continue
        txt=' '.join(a.stripped_strings)
        parent=' '.join(a.parent.stripped_strings) if a.parent else txt
        m=re.search(r'(?<!\d)(\d{4})(?!\d)',parent)
        if not m: continue
        rid=m.group(1)
        name=re.sub(r'\s+',' ',txt).strip()
        if not name or name==rid: 
            mm=re.search(r'\d{4}\s*(.+)',parent); name=mm.group(1).strip() if mm else rid
        gm=re.search(r'級別\s*[：:]\s*(A1|A2|B1|B2)',parent)
        items[rid]={'id':rid,'name':name,'grade':gm.group(1) if gm else '', 'photo':urljoin(r.url,src), 'profile':urljoin(r.url,href)}
    time.sleep(.15)
print('racers',len(items))
open('racers.js','w',encoding='utf-8').write('window.RACERS='+json.dumps(list(items.values()),ensure_ascii=False,separators=(',',':'))+';\n')
