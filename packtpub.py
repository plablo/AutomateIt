import re
import requests
from bs4 import BeautifulSoup

host = 'https://www.packtpub.com'
main_url = host + '/packt/offers/free-learning'
login_url = main_url
books_url = host + '/account/my-ebooks'
EMAIL = 'your_email'
PASS = 'your_pass'

user_agents = ['Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'
                ,'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36']
headers = {'user-agent':user_agents[1],
           'Referer':'https://www.packtpub.com/packt/offers/free-learning'}
def test_main_page(s):
    """ s must be a requests.sessions.Session object """
    print 'Main url'
    s.headers.update(headers)
    r = s.get(main_url)
    return {'is_ok':r.status_code == requests.codes.ok, 'response':r}



#To do: create and handle excepcions, divide code but keep same session.
with requests.Session() as s:
    #Main url: test the web page.
    print 'Main url'
    s.headers.update(headers)
    r = s.get(main_url)
    if r.status_code == requests.codes.ok:
        #Login page: find the form data and log in.
        print 'Login'
        soup = BeautifulSoup(r.text, 'html.parser')
        form_id = soup.find("input", attrs={"name":"form_build_id"})
        if form_id:
            data = {'email':EMAIL,
                    'password':PASS,
                    'op':'Login',
                    'form_build_id':form_id["value"].encode('unicode-escape'),
                    'form_id':'packt_user_login_form'}
            s.headers.update({'Content-Type':'application/x-www-form-urlencoded'})
            r = s.post(login_url, data=data)
            if r.status_code == requests.codes.ok and r.url == login_url:
                print 'Claim book'
                del s.headers['Content-Type']
                soup = BeautifulSoup(r.text, 'html.parser')
                free_book_link = soup.select("a[class~=twelve-days-claim]")
                if free_book_link:
                    free_book_url = host + free_book_link[0]["href"]
                    print '\t', free_book_url
                    r = s.get(free_book_url)
                    if r.status_code == requests.codes.ok:
                        #Books page: go to my ebooks page and retrieve the list of books.
                        print 'Books'                
                        r = s.get(books_url)
                        if r.status_code == requests.codes.ok:
                            soup = BeautifulSoup(r.text, 'html.parser')
                            books = soup.select("div[class~=product-line]")
                            #With each book.
                            for i in range(len(books)-1):
                                book_title = books[i].find("div", class_="title").text.strip().encode('unicode-escape')
                                book_author = books[i].find("div", class_="author").text.strip()#.encode('unicode-escape')
                                book_url = host + books[i].find(href=re.compile("pdf"))["href"].encode('unicode-escape')
                                out_line = '\n\t\t'.join([book_title, book_author, str(int(s.get(book_url, stream=True).headers['Content-length'])/(1024**2))+' Mb'])
                                if i == 0:                                    
                                    print '\tDownloading last book:'
                                    print '\t\t', out_line
                                    try:
                                        f = open(book_title+'('+book_author+').pdf', 'wb')
                                        f.write(s.get(book_url).content)
                                        f.close()
                                        print '\tDone'
                                    except IOError as e:
                                        print '\tCannot download. May be already on disk and open.'                                    
                                    print '\tOther titles:'
                                else:
                                    print '\t\t', out_line
none = raw_input('Press any key to close program')
