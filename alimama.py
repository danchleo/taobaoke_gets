# coding=utf-8
import urllib
import urllib2
import cookielib
import re
import hashlib
import json


class Alimama():
    def _prepare(self):
        self._cookie = cookielib.CookieJar()
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cookie))

    def _get_request(self, url):
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)')
        return request

    def _fetch_html(self, request, post_data=None):
        handler = None
        if post_data:
            handler = self._opener.open(request, urllib.urlencode(post_data))
        else:
            handler = self._opener.open(request)

        return handler.url, handler.read()

    def login(self, email, password):
        self._prepare()

        url, html = self._fetch_html(self._get_request('http://www.alimama.com'))
        login_url = re.findall('<iframe.*?id="J_mmLoginIfr".*?src="(.*?)".*?></iframe>', html)[0]

        url, html = self._fetch_html(self._get_request(login_url))

        action = re.findall('<form.*?action=[\'"](.*?)[\'"]', html)[0]
        inputs = re.findall('<input.*?name=[\'"](.*?)[\'"].*?value=[\'"](.*?)[\'"].*?>', html)

        form = {}
        for key, value in inputs:
            form[key] = value

        form['logname'] = email
        form['originalLogpasswd'] = password
        form['logpasswd'] = str(hashlib.md5(password).hexdigest()).lower()

        url, html = self._fetch_html(self._get_request(action), form)
        if 'success' in url:
            return True
        else:
            return False


    def get_top_information(self):
        tops = {
            # 热门词
            'keywords': 'http://top.taobao.com/interface_v2.php?trid=TR_zongbang&f=json&n=100&up=false',
            # 精品箱包
            'bag': 'http://top.taobao.com/interface_v2.php?cat=50006842&n=100&f=json',
            # 时尚女装
            'woman_clothes': 'http://top.taobao.com/interface_v2.php?cat=16&n=100&f=json',
            # 帅气男装
            'man_clothes': 'http://top.taobao.com/interface_v2.php?cat=50006842&n=100&f=json',
            }

        top_infos = {}
        for key in tops:
            url, html = self._fetch_html(self._get_request(tops[key]))
            print html
            if str(html).startswith('var top_data='):
                html = html[len('var top_data='):]
            top_infos[key] = json.loads(html)
        return top_infos

    def get_taobao_promo_url(self, id):
        url = 'http://u.alimama.com/union/spread/common/allCode.htm?specialType=item&auction_id=%s' % id
        url, html = self._fetch_html(self._get_request(url))
        return re.findall('var clickUrl = [\'"](.*?)[\'"];', html)[0]

    def _clear_others(self, words):
        return words.strip().replace('\n', '').replace('\r', '').replace('\t', '')

    def search(self, keywords, page=1, pagesize=40):
        url = 'http://u.alimama.com/union/spread/selfservice/merchandisePromotion.htm?cat=&mid=&searchType=0&page=%s&pagesize=%s&q=%s&_fmu.a._0.so=_commrate' % (page, pagesize, urllib.quote(keywords))

        url, html = self._fetch_html(self._get_request(url))
        # print html
        products = []
        trs = re.findall('<tr.*?>.*?</tr>', html, re.S)
        for tr in trs:
            tds = re.findall('<td.*?>.*?<\/td>', tr, re.S)
            #print tds
            if tds:
                pid = self._clear_others(re.findall('<input.*?value="(.*?)"', tds[0], re.S)[0])
                tmp = re.findall('<img.*?src="(.*?)".*?<a.*?>(.*?)<\/a>.*?<p.*?>(.*?)<span.*<\/p>', tds[1], re.S)[0]
                image = self._clear_others(tmp[0].strip().replace('\t', ''))
                title = self._clear_others(tmp[1])
                saler = self._clear_others(tmp[2])
                discount = self._clear_others(re.findall('<td.*?>(.*?)<\/td>', tds[2], re.S)[0])
                price = self._clear_others(re.findall('<td.*?>(.*?)<\/td>', tds[3], re.S)[0])
                promo_percent = self._clear_others(re.findall('<td.*?>(.*?)<\/td>', tds[4], re.S)[0])

                products.append({
                    'pid': pid,
                    'image': image,
                    'title': title.replace('<span>', '').replace('</span>', ''),
                    'saler': saler,
                    'discount': discount,
                    'price': price,
                    'promo_percent': promo_percent
                })

        #print products
        #print len(products)
        #print html
        tmp = re.findall('\{count:(.*?),size:(.*?),index:(.*?),goTo:false,pageCount:false\}', html, re.S)

        if tmp:
            tmp = tmp[0]
            record_count = int(tmp[0])
            page_size = int(tmp[1])
            current_page = int(tmp[2])
            page_sum = record_count/page_size

            if record_count % page_size > 0:
                page_sum += 1

        else:
            record_count = len(products)
            page_size = pagesize
            current_page = 1
            page_sum = 1

        return {
            'current_page': current_page,
            'page_sum': page_sum,
            'page_size': page_size,
            'record_count': record_count,
            'data': products
        }



ali = Alimama()
if ali.login('xxx@gmail.com', 'password'):
    #print ali.get_taobao_promo_url(10449760543)
    print ali.search('女装')
    #ali.get_top_information()


