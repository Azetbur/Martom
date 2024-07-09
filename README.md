# ESP_Vzorkovna_LED

**Ve zkratce: Tento repozitář obsahuje software na ovládání LED osvětlení vzorkovny za pomocí mikrokontroleru ESP32.**

Tento repozitář obsahuje software pro mikrokontroler ESP32, který slouží pro ovládní LED páskového osvětlení umístěného na regálech ve vzorkovně. Software zprostředkovává postupné zapínání jednotlivých LED okruhů za účelem minimalizace zátěže na elektroinsalaci budovy, rovněž umožňuje vypnutí osvětlení po vypršení nastaveného časového intervalu, konfiguraci průběhu zapnutí jednotlivých LED okruhů, apod. Průběh těchto funkcí, tj. např. interval vypínacího časovače,  je možné konfigurovat buď přímo ve zdrojovém kódu, či za pomocí rotačního enkodéru a displeje připojených k ESP32 mikrokontroleru zkrz zakázkově vyrobenou desku, v rámci které je mikrokontrolej zakomponován.

Sowtware pro tento projekt je vyvíkjen pouze v jazyce *Micropython*. Jádro softwaru tvoří ovladače pro jednotlivé fyzické prvky instalace, rozdělené do dvou adresářů. V adresáři `/my_drivers` se nachází ovladače zakázkově vyvinuté přimo pro tento projekt, tj. jmenovitě:

* `light_driver.py` - PWM ovladač jak jednotlivých okruhů LED osvětlení, tak celého osvětlení jako celku.
* `display_driver.py` - Jednoduchý ovladač běžného 4x20 LCD displeje ovládaného integrovaným obvodem *HD44780*.

Adresář `/third_party_drivers` je určen pro ovladače třetích stran. Momentálně obsahuje pouze ovladač rotačního enkodéru, skládající se ze dvou souborů, `rotary.py` a `rotary_irq_esp.py`.

Součástí softwaru jsou dále soubory `boot.py` a `controller.py` nacházející se v domovském adresáři repozitáře. Soubor `boot.py` slouží primárně ke konfiguraci pinů jednotlivých periferních zařízení, tj. displeje, LED obvodů apod. a inicializaci objektů reprezentujících tyto zařízení importovaných z jednotlivých výše zmíněných ovladačů. Soubor `controller.py`  propojuje všechny tyto jednotlivé prvky dohromady a zajišťuje jejich ovládání, tj. např. zapnutí osvětlení při stisknutí  vypínače, tisk nastavení na LCD displej apod.

## Konfigurace

### Konfigurace připojených LED okruhů a zařízení

Software je již nakonfigurovaný pro  provoz se zakázkově vyrobenou deskou na vzorkovnu. V případě provozu mikrokontroleru ESP32 tímto způsobem není třeba konfigurace připojených LED okruhů a zařízení nijak měnit, a tuto sekci je tudíž v tomto případě žádoucí přeskočit. Pokud však dojde v konfigurace ESP32, či desky do které bude vývojové deska s ESP32 vkládána, ke změně, lze piny na která jsou jednotlivé zařízení a okruhy připojené konfigurovat následovně:

1. Stáhněte si soubour `boot.py` z tohoto repozitáře do svého počítače.

2. Otevřete soubor v jakémkoli textovém editoru či vývojovem prostředí, tedy např. v *Thonny IDE*. V následující sekci souboru, nacházející se hned na jeho začátku:

```
# Set the correct pin numbers for each of the connected peripherals in this section ####################
# Set the correct pin numbers for each of the connected peripherals in this section ####################
DISPLAY_SDA_PIN_NO    = 21
DISPLAY_SCL_PIN_NO    = 22

ENCODER_DT_PIN_NO     = 34
ENCODER_CLK_PIN_NO    = 35

ENCODER_BUTTON_PIN_NO = 13

BUTTON_1_PIN_NO       =	12
BUTTON_2_PIN_NO       = 14
BUTTON_3_PIN_NO       = 27

# An array containing all the pins which belong to LED circuits.
# Correct formating example: [11, 12, 13]
PIN_NUMBER_ARRAY      = [15, 2, 0, 4, 16, 17, 5, 18, 19, 23]
```

... změňte čísla jednotlivých pinů tak, aby odpovídala skutečenému fyzickému připojení pinů k mikrokontroleru.

### Konfigurace nastavení osvětlení

Ačkoli lze jednoduše konfigurovat nastavení osvětlení ovládaného ESP32 mikrokontrolerem pomocí rotačního enkodéru a displeje připojeních jako periferní zařízení, toto nastavení je rovněž možné velmi snadno provést úpravou souboru `boot.py` před jeho nahráním na ESP32 dle postupu v sekci *Instalace* tohoto dokumentu. Tato konfigurace tedy není k funkčnosti softwaru na mikrokontroleru nutná, a tudíž lze sekci tohoto dokumentu při instalaci zcela přeskočit. Tato konfigurace je nicméně žádoucí např. při provozu mikrokontroleru bez displeje a rotačního enkodéru. Konfigurace v rámci souboru `boot.py` probíhá následovně:

1. Stáhněte si soubour `boot.py` z tohoto repozitáře do svého počítače.


## Instalace

Instalační postup je zcela standardní pro *micropython* program na  mikrokontroleru ESP32, tj. k němu lze využít nezpočet běžně dostupných nástrojů jako např. *uPyCraft IDE*, *Thonny IDE*, či nástroje přímo v příkazové řádce.

Následujíci sekce je určena primárně pro osoby neználé těchto nástrojů. Obsahuje detailní postup, jak naistalovat Micropython i tento software na ESP32 pomocí *Thonny IDE*.

*Thonny IDE* je volně dostupné vývojové prostředí pro *Windows*, *Linux* i *Mac*. Zde je odkaz na [webové stránky Thonny IDE](https://thonny.org/ "Thonny").

### Flash *MicroPython* Softwaru

*MicroPython* není v procesorech ESP32 naistalovaný z výroby, před instalací tohoto softwaru je tedy třeba na ESP32 jako první naistalovat _MicroPython_. Instalace probíhá následovně:

1. **Propojte ESP32 s počítačem, na kterém je software *Thonny IDE* naistalovaný**. Toto propojení je bežně provedeno propojením Micro-USB či USB-C portu, který se nachází na vývojové desce mikrokontroleru s počítačem za pomocí vhodného kabelu. **Ujistěte se, že kabel neslouží pouze k nabíjení, tj. že obsahuje i datové propoje.**

![IMG_2683](https://github.com/Azetbur/Martom/assets/47574514/b1790ea6-0c3a-460e-b10b-ea2a8cb330c3)

3. V *Thonny IDE* klikněte v levém horním okraji obrazovky na **Run**, v rozbalené nabídce následně klikněte na položku **Configure interpreter...**

4. Pod řádkem **Which kind of interpreter should Thonny use for running your code?** vyberte z rozbalovací nabídky možnost **MicroPython (ESP32)**.

5. Pod řádkem **Port or WebREPL** vyberte port, přes který je ESP32 k počítači připojeno. Pravděpodobně půjde o možnost se slovy **USB to UART Bridge Controller** v názvu.

6. V pravém dolním rohu okna stiskněte text modré barvy **Install or update MicroPython (esptool)**.
7. V nově zobrazeném okně vyberte pod řákem **MicroPython family** typ ESP32 mikrokontroleru, který máte k počítači připojený (typ zařízení je obvykle vytištění ESP32 čipu samotném, běžné vývojové desky jsou obvykle osazeny typem **ESP32**.

8. Pod řádkem variant vyberte výrobce - varianut ESP32 mikrokontroleru, která je připojená k počítači (tento údaj lze obvykle rovněž zjistit z textu vytištěném na čipu, pro běžné vývojové desky se bude obvykle jednat o možnost **Espressif • ESP32 / WROOM**.

9. Stiskněte tlačítko **Install**. Proces instalace může zabrat až několik minut.

### Flash jednotlivých souborů

Nyní je třeba pomocí *Thonny IDE* na ESP32 mikrokontroler flashnout - nahrát všechny soubory tohoto softwaru. Nejdřív je však pro ně třeba vytvořit příslušné adresáře. 

1. Ujistěte se, že je mikrokontroler ESP32 připojený k počítači a připraven přijímat data. Mikrokontroler se v tomto stavu nachází, pokud v okénku **Shell** v *Thonny IDE* obsahují zprávu obdobné této:

```
MPY: soft reboot
MicroPython v1.23.0 on 2024-06-02; Generic ESP32 module with ESP32
Type "help()" for more information.
>>> 
```

... či pokud se na posledních několika řádcích nachází pouze symboly `>>>`, tj.:

```
>>>
>>>
>>>
```

V opačném připadě je třeba stisknout červené tlačítko **Stop/Restart backend (Ctrl+F2)**. Pokud se v okénku **Shell** po stisknutí červeného tlačítko **Stop** nezobrazí jedna z dvou výše uvedených možností, zkuste tlačítko zmáčknout znovu. Pokud se výsledek stále nedostaví, zkuste mikrokontroler odpojit a znovu připojit k počítači, načež znovu stiskněte červené tlačítko **Stop**. Pokud přesto nelze docílit žádoucího stavu v okenků **Shell** po několika opakovaných odpojení a připojení zařízení a zmáčknutích  tlačítka **Stop**, opakujte znovu všechny kroky v sekci *Flash MicroPython Softwaru*.

2. V rozbalovacím menu vedle modrého textu **MicroPython device** vyberte možnost **New directory...**.

3. Pod řádkem **Enter name for new directory under /** napište do textového pole `my_drivers`,  načež stiskněte tlačítko **OK**. 

4. Body 2 a 3 opakujte, při opakování bodu 3 však do textového pole nyní napiště ``third_party_drivers``.

Nyní je třeba nahrát do ESP32 jednotlivé soubory v tomto repozitáři. Soubory musí být pro následující kroky již staženy na vašem počítači, pokud teda ještě nejsou, nyní si obsah tohoto repozitáře do počítače zkopírujte.

5. Stiskněte **File**, v rozbalené nabídce následně stiskněte možnost **Open**.

6. V nově otevřeném okně stiskněte možnost **This computer**.

6. Opět v nově otevřeném okně najděte soubor `controller.py`, vyberte ho, načež stiskněte tlačítko **Open**. Vzhledm okna pro výběr souborů se bude dle operačního systému na vašem počítači lyšit, screenshot níže je z počítače s operačním systémem Mac OS.

8. Opět stiskněte **File**, v rozbalené nabídce však nyní stiskněte možnost **Save as...**. 

9. V nově otevřeném okně nyní stiskněte možnost **MicroPython device**.

10. Na řádku **File name:** napiště do textového pole `controller.py`, načež zmáčkněte tlačítko **OK**.

11. Opakujte kroky 5. až 10. pro soubory, tj. `light_driver.py`, `display_driver.py`, `rotary.py`, `rotary_irq_esp.py` a oba soubory `__init__.py`. Pozor, tyto soubory musí být uloženy ve svých příslušných složkách, tak, jak jsou v tomto repozitáři. K tomuto je v kroku 10. potřeba před stisknutím tlačítka **Ok** nejdřív vybrat správný adresář, do kterého bude soubor vložen.

V případě uložení souboru s jiným jménem či do špatné složky lze daný soubor vymazat stisknutím souboru pravým tlačítkem myši v okénku na pravé straně obrazovky pod řádkem **MicroPython device** a následným stisknutím možnosti **Delete**.

12. Nyní opakujte kroky 5. až 10. pro soubor `boot.py`, který patří spolu se souborem `controller.py` do domovského adresáře na ESP32.

13. ESP32 kontroler je nyní připraven k provozu. Program lze spustit pomocí stisknutí tlačítka **Stop**. Soubor `boot.py` se spustí při každém restartu ESP32, tj. i při každém stisknutí tlačítka **Stop**. K nahrání nových či přepsání existujících souborů po restartu ESP32 s funkčním souborem `boot.py` je tedy třeba průběh tohoto programu nejdříve přerušit. Tohoto může být možné dosáhnout několika opakovanými stisky tlačítka **Stop**, či dvěma stisky zeleného tlačítka **Run** s prodlevou zhruba jedné vteřiny, toto však nemusí vždy fungovat. V případě selhání těchto postupů je třeba znovu opakovat postup v sekci *Flash MicroPython Softwaru* tohoto dokumentu, načež je rovněž potřeba znovu nahrát všechny soubory opakováním postupu v sekci *Flash jednotlivých souborů*.



Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install foobar
```

## Použití



## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
