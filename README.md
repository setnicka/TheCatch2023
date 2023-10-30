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
