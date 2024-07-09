# ESP_Vzorkovna_LED

Tento repozitář obsahuje software pro mikrokontroler ESP32. Software slouží k ovládní LED osvětlení umístěného na regálech ve vzorkovně. Software zprostředkovává postupné zapínání jednotlivých LED okruhů za účelem minimalizace zátěže na elektroinsalaci budovy. Software rovněž umožňuje vypnutí osvětlení po vypršení nastaveného časového intervalu, konfiguraci průběhu zapínání jednotlivých LED okruhů, apod. Nastavení parametrů těchto funkcí, tj. např. časového intervalu pro vypnutí osvětlení, je možné změnit buď přímo ve zdrojovém kódu softwaru, či za pomocí rotačního enkodéru a displeje. Tyto periferní zařízení jsou připojené k mikrokontroleru ESP32 skrz zakázkově vyrobenou desku. V rámci této desky je ESP32 mikrokontroler, umístěný ve své vlastní vývojové desce, zapojený.

Sowtware je vyvíjen pouze v jazyce *Micropython*. Jádro softwaru tvoří ovladače pro jednotlivé fyzické prvky instalace, rozdělené do dvou adresářů. V adresáři `/my_drivers` se nachází ovladače zakázkově vyvinuté přimo pro tento projekt, tj. jmenovitě:

* `light_driver.py` - PWM ovladač jednotlivých LED okruhů osvětlení a celého osvětlení jako celku.
* `display_driver.py` - Ovladač zajišťující komunikaci s 4x20 LCD displejem ovládaným integrovaným obvodem *HD44780* za pomocí *I2C* protokolu.

Adresář `/third_party_drivers` je určen pro ovladače třetích stran. Současně obsahuje pouze ovladač rotačního enkodéru, skládající se ze dvou souborů, `rotary.py` a `rotary_irq_esp.py`.

Součástí softwaru jsou dále soubory `boot.py` a `controller.py`. Tyto soubory se nachází v domovském adresáři repozitáře.

Soubor `boot.py` slouží primárně ke konfiguraci čísel pinů jednotlivých periferních zařízení, tj. displeje, LED obvodů apod. V rámci souboru rovněž probíhá inicializaci objektů reprezentujících tyto zařízení. Tyto objekty jsou importovány z jednotlivých ovladačů zmíněných výše.

Soubor `controller.py`  zajištuje fukční propejení všech výše zmíněních objektů a jejich ovládání, tj. např. zapnutí osvětlení při stisknutí  vypínače, tisk změny v nastavení na LCD displej při otočení rotačním enkodérem apod.

## Konfigurace

V souboru `boot.py` se nachází dvě sekce prostého textu určené pro konfiguraci parametrů softwaru. První sekce slouží k nastavení čísel pinů připojeních periferních zařízení. Druhá sekce je určena pro nastavení parametrů jednotlivých funkcí softwaru, tj. např. časového intervalu pro vypnutí osvětlení.

### Konfigurace připojených LED okruhů a zařízení

Software obsažený v tomto repozitáři je již nakonfigurovaný pro provoz s deskou, která byla na vzorkovnu zakázkově vyrobena. V případě použití softwaru na vzorkovně s touto deskou tudíž není třeba konfigurace připojených LED okruhů ani ostatních zařízení nijak měnit. Za těchto okolností je vhodné četbu této sekci přeskočit.

Pokud však dojde v designu desky pro vzorkovnu ke změně, či bude-li kopie tohoto softwaru využívána s jiným hardwarem, lze piny na které jsou jednotlivé zařízení a okruhy připojené konfigurovat následovně:

1. Stáhněte soubour `boot.py` z tohoto repozitáře do svého počítače.

2. Otevřete soubor v jakémkoli textovém editoru či vývojovem prostředí. V sekci souboru vyobrazené pod tímto textem, nacházející se na jeho začátku, změňte čísla jednotlivých pinů. Čísla by měla odpovídat fyzickému zapojení pinů. 

```python
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

3. Soubor uložte. Postup nahrání souboru do mikrokontroleru ESP32 je popsán v nadcházející sekci tohoto dokumentu nazvané *Instalace*.

### Konfigurace nastavení osvětlení

Ačkoli lze nastavení osvětlení jednoduše konfigurovat v rámci provozu softwaru za pomocí připojeného rotačního enkodéru a displeje, toto nastavení je rovněž možné snadno provést úpravou souboru `boot.py`. Tato úprava není k funkčnosti softwaru na mikrokontroleru nutná, software v tomto repozitáři již obsahuje správné výchozí nastavení.  V případě použití softwaru na vzorkovně s deskou pro toto použití určenou a výchozím nastavením tudíž není třeba nastavení osvětlení tímto způsobem nijak měnit. Za těchto okolností je vhodné četbu této sekci přeskočit.

Tento postup je nicméně žádoucí např. při provozu mikrokontroleru bez displeje a rotačního enkodéru. Konfigurace probíhá následovně:

1. Stáhněte soubour `boot.py` z tohoto repozitáře do svého počítače. V případě, že máte soubor již stažený skrz postup v předchozí sekci tohoto dokumentu, použijte v následujícím bodě tento stažený soubor.
  
2. Otevřete soubor v jakémkoli textovém editoru či vývojovem prostředí. V následující sekci souboru, začínající na řádku 18, změňte nastavení osvětlení dle potřeby.

```python
# Set the default setting for the LED lightning in this section ########################################

BRIGHTNESS_PERCENTAGE_DEFAULT = 90
TIMER_TIME_MIN_DEFAULT        = 60
UPTIME_TIME_SEC_DEFAULT       = 1
DOWNTIME_TIME_SEC_DEFAULT     = 2
OVERLAP_PERCENTAGE_DEFAULT    = 50

# Set this to True if you want the timer function to be active, False if not
TIMER_ON_OFF_BOOL_DEFAULT     = True

# End of section #######################################################################################
```

3. Soubor uložte. Postup nahrání souboru do mikrokontroleru ESP32 je popsán v nadcházející sekci tohoto dokumentu nazvané *Instalace*.

## Instalace

Instalační proces pro tento software je zcela standardním postupem, který se nijak nelyší od postupu instalace jakéhokoli jiného *Micropython* program na ESP32 mikrokontroler. K instalaci lze tudíž využít nespočet volně dostupných vývojových prostředí jako např. *uPyCraft IDE*, *Thonny IDE*, apod., či volně dostupné nástroje zabudované přímo do příkazové řádky.

Následujíci sekce je určena primárně pro osoby neználé těchto nástrojů. Obsahuje detailní popis instalace *Micropythonu* a následně tohoto software na ESP32 mikrokontroler za pomocí vývojového prostředí *Thonny IDE*. Pokud se v tomto odvětví orientujete, můžete  zvolit jakýkoli jiný postup instalace bez očekávání žádných nadbytečných problémů.

*Thonny IDE* je volně dostupné vývojové prostředí pro *Windows*, *Linux* i *Mac*. [Odkaz na webové stránky Thonny IDE](https://thonny.org/ "Thonny").

Z těchto webových stránek je potřeba vývojové prostředí, tj. program *Thonny*, stáhnout a naistalovat na váš počítač před provedením kroků popsaných v následujících sekcích tohoto dokumentu.

### Flash *MicroPython* firmwaru

*MicroPython* není v procesorech ESP32 naistalovaný z výroby, před instalací tohoto softwaru je tedy třeba na ESP32 mikrokontroler nejdříve naistalovat _MicroPython_. Instalace probíhá následovně:

1. **Propojte ESP32 s počítačem, na kterém je vývojové prostředí *Thonny IDE* naistalované**. Toto propojení je bežně realizováno pomocí Micro-USB či USB-C kabelu; typ kabelu závisí na portu na vývojové desce ESP32. **Ujistěte se, že vámi vybraný kabel neslouží pouze k nabíjení, tj. že obsahuje datové propoje.** V opačném případe se nebude možné k ESP32 mikrokontroleru skrz kabel připojit.

![ESP_Vzorkovna_LED_0](https://github.com/Azetbur/Martom/assets/47574514/c727c0de-3a68-4a53-adfc-54ceb72e8d9d)

2. V *Thonny IDE* klikněte v levém horním okraji obrazovky na **Run**, v rozbalené nabídce následně klikněte na položku **Configure interpreter...**

![ESP_Vzorkovna_LED_1](https://github.com/Azetbur/Martom/assets/47574514/4ec4c0c1-81d0-4c24-8f35-fe16968904aa)

3. Pod řádkem **Which kind of interpreter should Thonny use for running your code?** vyberte z rozbalovací nabídky možnost **MicroPython (ESP32)**.

![ESP_Vzorkovna_LED_2](https://github.com/Azetbur/Martom/assets/47574514/a729c2b5-c52e-418a-963c-c280719064bb)

4. Pod řádkem **Port or WebREPL** vyberte port, přes který je ESP32 k počítači připojeno. Pravděpodobně půjde o možnost se slovy **USB to UART Bridge Controller** v názvu.

![ESP_Vzorkovna_LED_3](https://github.com/Azetbur/Martom/assets/47574514/3a6f3038-c4df-4462-9989-30266ada73a4)

5. V pravém dolním rohu okna stiskněte text modré barvy **Install or update MicroPython (esptool)**.

![ESP_Vzorkovna_LED_4](https://github.com/Azetbur/Martom/assets/47574514/5a9e1af2-1b41-40db-8253-64371c697c8e)

6. V nově zobrazeném okně vyberte pod řákem **MicroPython family** typ ESP32 mikrokontroleru, který máte k počítači připojený (typ zařízení je obvykle vytištění ESP32 čipu samotném, běžné vývojové desky jsou obvykle osazeny typem **ESP32**.

![ESP_Vzorkovna_LED_5](https://github.com/Azetbur/Martom/assets/47574514/87d35f86-d72e-44e5-ba62-946505216e4c)

7. Pod řádkem variant vyberte výrobce - varianut ESP32 mikrokontroleru, která je připojená k počítači (tento údaj lze obvykle rovněž zjistit z textu vytištěném na čipu, pro běžné vývojové desky se bude obvykle jednat o možnost **Espressif • ESP32 / WROOM**.

![ESP_Vzorkovna_LED_6](https://github.com/Azetbur/Martom/assets/47574514/4bec7afa-3f73-408f-a622-2dee30af7e45)

8. Stiskněte tlačítko **Install**. Proces instalace může zabrat až několik minut.



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
