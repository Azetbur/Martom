# ESP_Vzorkovna_LED

Tento repozitář obsahuje software pro mikrokontroler ESP32. Software slouží k ovládní LED osvětlení umístěného na regálech ve vzorkovně. Software zprostředkovává postupné zapínání jednotlivých LED okruhů za účelem minimalizace zátěže na elektroinstalaci budovy. Software rovněž umožňuje vypnutí osvětlení po vypršení nastaveného časového intervalu, konfiguraci průběhu zapínání jednotlivých LED okruhů, apod. Nastavení parametrů těchto funkcí, tj. např. časového intervalu pro vypnutí osvětlení, je možné změnit buď přímo ve zdrojovém kódu softwaru, nebo za pomocí rotačního enkodéru a displeje. Tato periferní zařízení jsou připojené k mikrokontroleru ESP32 skrz zakázkově vyrobenou desku. V rámci této desky je ESP32 mikrokontroler, umístěný ve své vlastní vývojové desce, zapojený.

Software je vyvíjen v jazyce *Micropython*. Jádro softwaru tvoří ovladače pro jednotlivé fyzické prvky instalace, rozdělené do dvou adresářů. V adresáři `/my_drivers` se nachází ovladače zakázkově vyvinuté přimo pro tento projekt, tj. jmenovitě:

* `light_driver.py` - PWM ovladač jednotlivých LED okruhů osvětlení a celého osvětlení jako celku
* `display_driver.py` - Ovladač zajišťující komunikaci s 4x20 LCD displejem ovládaným integrovaným obvodem *HD44780* za pomocí *I2C* protokolu

Adresář `/third_party_drivers` je určen pro ovladače třetích stran. Aktuálně obsahuje pouze ovladač rotačního enkodéru skládající se ze dvou souborů, `rotary.py` a `rotary_irq_esp.py`.

Součástí softwaru jsou dále soubory `boot.py` a `controller.py`. Tyto soubory se nachází v kořenovém adresáři repozitáře.

Soubor `boot.py` slouží primárně ke konfiguraci čísel pinů jednotlivých periferních zařízení, tj. displeje, LED obvodů, apod. V rámci souboru rovněž probíhá inicializace objektů reprezentujících tato zařízení. Tyto objekty jsou importovány z jednotlivých ovladačů zmíněných výše.

Soubor `controller.py` zajištuje fukční propojení všech výše zmíněných objektů a jejich ovládání, tj. např. zapnutí osvětlení při stisknutí vypínače, zobrazení změny v nastavení na LCD displeji při otočení rotačního enkodéru, apod.

## Konfigurace

V souboru `boot.py` se nachází dvě sekce určené pro konfiguraci parametrů softwaru. První sekce slouží k nastavení čísel pinů připojených periferních zařízení. Druhá sekce je určena pro nastavení parametrů jednotlivých funkcí softwaru, tj. např. časového intervalu vypnutí osvětlení.

### Konfigurace připojených LED okruhů a zařízení

Software obsažený v tomto repozitáři je již nakonfigurovaný pro provoz s deskou, která byla na vzorkovnu zakázkově vyrobena. V případě použití softwaru na vzorkovně s touto deskou tudíž není třeba měnit konfigurace připojených LED okruhů ani ostatních zařízení. Za těchto okolností je vhodné četbu této sekce přeskočit.

Pokud však dojde v designu desky pro vzorkovnu ke změně, či bude-li kopie tohoto softwaru použita s jiným hardwarem, lze piny, na které jsou jednotlivé zařízení a okruhy připojené, konfigurovat následovně:

1. Stáhněte soubour `boot.py` z tohoto repozitáře do svého počítače.

2. Otevřete soubor v jakémkoli textovém editoru či vývojovem prostředí. V sekci souboru vyobrazené pod tímto textem, nacházející se na jeho začátku, změňte čísla jednotlivých pinů. Čísla by měla odpovídat fyzickému zapojení pinů. Způsob očíslování pinů na vaší vývojové pro ESP32 naleznete v dokumentaci výrobce dané desky.

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

Ačkoli lze nastavení osvětlení jednoduše konfigurovat v rámci provozu softwaru za pomocí připojeného rotačního enkodéru a displeje, toto nastavení je rovněž možné snadno provést úpravou souboru `boot.py`. Tato úprava není k funkčnosti softwaru na mikrokontroleru nutná; software v tomto repozitáři již obsahuje správné výchozí nastavení.  V případě použití softwaru na vzorkovně s deskou pro toto použití určenou a výchozím nastavením tudíž není třeba nastavení osvětlení tímto způsobem nijak měnit. Za těchto okolností je vhodné četbu této sekce přeskočit.

Tento postup je nicméně žádoucí např. při provozu mikrokontroleru bez displeje a rotačního enkodéru. Konfigurace probíhá následovně:

1. Stáhněte soubour `boot.py` z tohoto repozitáře do svého počítače. V případě, že máte soubor již stažený skrz postup v předchozí sekci tohoto dokumentu, použijte v následujícím bodě tento stažený soubor.
  
2. Otevřete soubor v jakémkoli textovém editoru či vývojovem prostředí. V následující sekci souboru, která začíná na řádku 18, změňte nastavení osvětlení dle potřeby.

```python
# Set the default setting for the LED lightning in this section ########################################

# The brightness percentage value should be a multiple of 5
BRIGHTNESS_PERCENTAGE_DEFAULT = 90

TIMER_TIME_MIN_DEFAULT        = 60
UPTIME_TIME_SEC_DEFAULT       = 1
DOWNTIME_TIME_SEC_DEFAULT     = 2
OVERLAP_PERCENTAGE_DEFAULT    = 50

# Set this to True if you want the timer function to be active, False if not
TIMER_ON_OFF_BOOL_DEFAULT     = True

# End of section #######################################################################################
```

* `BRIGHNTESS_PERCENTAGE_DEFAULT` - Nastavení jasu osvětlení v procentech. Lze nastavit na hodnotu `0` až `100`. Hodnota by měla být násobek pěti.
* `UPTIME_TIME_SEC_DEFAULT` - Nastavení intervalu zapnutí jedno LED okruhu v sekundách. Nastavte hodnotu mezi `1` až `60`.
* `DOWNTIME_TIME_SEC_DEFAULT` - Nastavení intervalu vypnutí jednoho LED okruhu v sekundách. Nastave hodnotu mezi `1` až `60`.
* `OVERLAP_PERCENTAGE_DEFAULT` - Nastavení míry překrytí zapínání jednotlivých LED okruhů v procentech. Lze nastavit na hodnotu `0` až `100`. Hodnota by měla být násobek pěti. Při nastavení hodnoty `100` se všechny okruhy zapínají zároveň. Při nastavení hodnoty `0` se okruhy zapínají postupně, bez překrývání.
* `TIMER_ON_OFF_DEFAULT_BOOL` - Nastavení zapnutí časovače. Nastave na hodnotu `True` pokud má být funkce časovače zapnutá, v opačném případě nastavte hodnotu `False`.

3. Soubor uložte. Postup nahrání souboru do mikrokontroleru ESP32 je popsán v nadcházející sekci tohoto dokumentu nazvané *Instalace*.

## Instalace

Instalační proces pro tento software je zcela standardním postupem, který se nijak nelyší od postupu instalace jakéhokoli jiného *Micropython* program na ESP32 mikrokontroler. K instalaci lze tudíž využít nespočet volně dostupných vývojových prostředí jako např. *uPyCraft IDE*, *Thonny IDE*, apod., či volně dostupné nástroje zabudované přímo do příkazové řádky.

Následujíci sekce je určena primárně pro osoby neználé těchto nástrojů. Obsahuje detailní popis instalace *Micropythonu* a následně tohoto software na ESP32 mikrokontroler za pomocí vývojového prostředí *Thonny IDE*. Pokud se v této technologii orientujete, můžete  zvolit jakýkoli jiný postup instalace bez očekávání nadbytečných problémů a četbu této sekce přeskočit.

*Thonny IDE* je volně dostupné vývojové prostředí podporující operační systémy *Windows*, *Linux* i *Mac*. [Odkaz na webové stránky Thonny IDE](https://thonny.org/ "Thonny").

Z těchto webových stránek je potřeba vývojové prostředí, tj. program *Thonny*, stáhnout a naistalovat na váš počítač, před provedením kroků popsaných v následujících sekcích tohoto dokumentu.

### Flash *MicroPython* firmwaru

*MicroPython* není v procesorech ESP32 instalovaný z výroby, před instalací tohoto softwaru je tedy třeba na ESP32 mikrokontroler nejdříve naistalovat _MicroPython_. Instalace probíhá následovně:

1. **Propojte ESP32 s počítačem, na kterém je vývojové prostředí *Thonny IDE* naistalované**. Toto propojení je bežně realizováno pomocí Micro-USB či USB-C kabelu; typ kabelu závisí na portu na vývojové desce ESP32. **Ujistěte se, že vámi vybraný kabel neslouží pouze k nabíjení, tj. že obsahuje datové propoje.** V opačném případe se nebude možné k ESP32 mikrokontroleru skrz kabel připojit.

![ESP_Vzorkovna_LED_0](https://github.com/Azetbur/Martom/assets/47574514/c727c0de-3a68-4a53-adfc-54ceb72e8d9d)

2. Spusťte vývojové prostředí *Thonny IDE*. Po spuštění programu vyberte v levém horním okraji obrazovky '**Run**', v nově rozbalené nabídce následně stiskněte '**Configure interpreter...**'.

![ESP_Vzorkovna_LED_1](https://github.com/Azetbur/Martom/assets/47574514/4ec4c0c1-81d0-4c24-8f35-fe16968904aa)

3. Pod řádkem '**Which kind of interpreter should Thonny use for running your code?**' vyberte z rozbalovací nabídky možnost '**MicroPython (ESP32)**'.

![ESP_Vzorkovna_LED_2](https://github.com/Azetbur/Martom/assets/47574514/a729c2b5-c52e-418a-963c-c280719064bb)

4. Pod řádkem '**Port or WebREPL**' vyberte port, přes který je ESP32 mikrokontroler k počítači připojený. Pravděpodobně se bude jednat o možnost s názvem obsahujícím termín '**USB to UART Bridge Controller**'.
![ESP_Vzorkovna_LED_3](https://github.com/Azetbur/Martom/assets/47574514/3a6f3038-c4df-4462-9989-30266ada73a4)

5. V pravém dolním rohu okna stiskněte text modré barvy '**Install or update MicroPython (esptool)**'.

![ESP_Vzorkovna_LED_4](https://github.com/Azetbur/Martom/assets/47574514/0cc25a01-176b-4332-81e0-ebc0e2abcd24)

6. V nově zobrazeném okně vyberte pod řádkem '**MicroPython family**' typ ESP32 mikrokontroleru, který máte k počítači připojený. Typ mikrokontroleru je obvykle vytištěný na ESP32 čipu samotném. Běžné vývojové desky jsou zpravidla osazeny typem '**ESP32**'.

![ESP_Vzorkovna_LED_5](https://github.com/Azetbur/Martom/assets/47574514/87d35f86-d72e-44e5-ba62-946505216e4c)

7. Pod řádkem '**variant**' vyberte výrobce - variantu ESP32 mikrokontroleru, kterou máte k počítači připojenou. Tento údaj lze obvykle rovněž zjistit z textu vytištěného na ESP32 čipu samotném. U běžných vývojových desek se bude zpravidla jednat o možnost '**Espressif • ESP32 / WROOM**'.

![ESP_Vzorkovna_LED_6](https://github.com/Azetbur/Martom/assets/47574514/4bec7afa-3f73-408f-a622-2dee30af7e45)

8. Stiskněte tlačítko '**Install**'. Proces instalace může trvat až několik minut.

9. Po dokončení instalace zavřete aktivní okno stisknutím tlačítka '**Close**', následně rovněž zavřete zbylé aktivní okno stisknutím tlačítka '**Ok**'.

Na vašem ESP32 mikrokontroleru je nyní nainstalovaný *MicroPython* firmware.

### Flash jednotlivých souborů

Po instalaci *MicroPython* firmwaru na ESP32 mikrokontroler je na mikrokontroler nutné nahrát soubory tohoto softwaru. Nejdříve je však pro soubory třeba vytvořit příslušné adresáře. Vytvoření adresářů probíhá následovně:

1. Ujistěte se, že je ESP32 mikrokontroler připojený k počítači a připravený přijímat data. Mikrokontroler je přiravený přijímat data, pokud okénko '**Shell**' v *Thonny IDE* obsahuje zprávu obdobné této:

```
MPY: soft reboot
MicroPython v1.23.0 on 2024-06-02; Generic ESP32 module with ESP32
Type "help()" for more information.
>>> 
```

Mikrokontroler je rovněž připravený přijímat data, pokud se na posledních několika řádcích okenká '**Shell**' nachází pouze symboly `>>>`, tj.:

```
>>>
>>>
>>>
```

V opačném připadě je třeba stisknout červené tlačítko '**Stop/Restart backend (Ctrl+F2)**'. Pokud se v okénku '**Shell**' po stisknutí červeného tlačítko '**Stop**' nezobrazí jeden ze dvou výše uvedených textů, zmáčkněte tlačítko znovu. Pokud se jeden z textů stále nezobrazí, odpojte a znovu zapojet ESP32 mikrokontroler k počítači, načež znovu stiskněte červené tlačítko '**Stop**'.

Pokud stále nelze docílit žádoucího stavu v okenků '**Shell**' po několika opakovaných odpojení a připojení mikrokontroleru a stisknutí tlačítka '**Stop**', znovu opakujte všechny kroky v sekci *Flash MicroPython Softwaru* tohoto dokumentu.

2. V rozbalovacím menu vedle modrého textu '**MicroPython device**' vyberte možnost '**New directory...**'.

![ESP_Vzorkovna_LED_7](https://github.com/Azetbur/Martom/assets/47574514/e781a0a9-f4f2-4e1b-bd12-9ed74d9f3dd9)

3. Pod řádkem '**Enter name for new directory under /**' napište do textového pole `my_drivers`,  načež stiskněte tlačítko '**OK**'.

![ESP_Vzorkovna_LED_8](https://github.com/Azetbur/Martom/assets/47574514/8fd73568-30a5-493a-99ae-14a53b92d8f8)

4. Body 2 a 3 opakujte, při opakování bodu 3 však do textového pole napiště ``third_party_drivers``.

V tento okamžik je třeba nahrát do ESP32 jednotlivé soubory softwaru, nacházející se v tomto repozitáři. Soubory musí být pro následující kroky již stažené na vašem počítači. Pokud nemáte soubory stažené, učiňte tak nyní.

5. Stiskněte '**File**', v rozbalené nabídce následně stiskněte možnost '**Open**'.

![ESP_Vzorkovna_LED_9](https://github.com/Azetbur/Martom/assets/47574514/efc171c9-c826-4fa8-883d-dcb6112bbaac)

6. V nově otevřeném okně stiskněte možnost '**This computer**'.

![ESP_Vzorkovna_LED_10](https://github.com/Azetbur/Martom/assets/47574514/fe0dda21-345a-4912-bccd-b3fcc33efb22)

7. Opět v nově otevřeném okně najděte soubor `controller.py` stažený z tohoto repozitáře. Vyberte ho a stiskněte tlačítko '**Open**'.

![ESP_Vzorkovna_LED_11](https://github.com/Azetbur/Martom/assets/47574514/f2992f21-234f-4ec6-b2dd-b12f2ecb2e78)

8. Opět stiskněte '**File**', v rozbalené nabídce však nyní stiskněte možnost '**Save copy...**'.

![ESP_Vzorkovna_LED_12](https://github.com/Azetbur/Martom/assets/47574514/80fa8477-225a-4bbd-b6dc-74d3b1be9f83)

9. V nově otevřeném okně nyní stiskněte možnost '**MicroPython device**'.

![ESP_Vzorkovna_LED_13](https://github.com/Azetbur/Martom/assets/47574514/7c2e3de1-8cf0-49a8-9429-00db82946af6)

10. Na řádku '**File name:**' napiště do textového pole `controller.py`, načež zmáčkněte tlačítko '**OK**'.

![ESP_Vzorkovna_LED_14](https://github.com/Azetbur/Martom/assets/47574514/55d84c07-991a-48ea-84b7-873da655f52d)

11. Opakujte kroky 5. až 10. pro soubory `light_driver.py`, `display_driver.py`, `rotary.py`, `rotary_irq_esp.py` a oba soubory `__init__.py`. Tyto soubory musí být uloženy ve svých příslušných adresářích ve stejné adresářové sturktuře jako v tomto repozitáři. K uložení souborů do odpovídajících adresářů je v kroku 10. potřeba před stisknutím tlačítka '**Ok**' nejdříve vybrat odpovídající adresář, do kterého bude soubor uložen.

V případě uložení souboru pod chybním názvem či do neodpovídajícího adresáře lze tento soubor vymazat. K vymazání daného souboru stiskněte v okénku na pravé straně obrazovky pod řádkem '**MicroPython device**' jméno tohoto souboru pravým tlačítkem. Následným stisknutím možnosti '**Delete**' soubor vymažete.

![ESP_Vzorkovna_LED_15](https://github.com/Azetbur/Martom/assets/47574514/404a74e9-3fd4-4faa-89d7-b551a12088e3)

12. Nyní opakujte kroky 5. až 10. pro soubor `boot.py`, který patří spolu se souborem `controller.py` do domovského adresáře ESP32 mikrokontroleru.

13. Software je nyní připraven ke spuštění. Software lze spustit stisknutím červeného tlačítka '**Stop**' v *Thonny IDE* či stisknutím fyzického tlačítka '**RST**' na vývojové desce ESP32 mikrokontroleru.

Soubor `boot.py` se spouští automaticky při každém restartu mikrokontroleru, tj. i při každém stisknutí tlačítka '**Stop**'. Pokud je soubor `boot.py` v mikrokontroleru přítomen a software byl již spušťen, je k nahrání nových či přepsání existujících souborů v ESP32 mikrokontroleru nejdříve třeba přerušit činnost softwaru. Toto lze docílit stisknutím jakékoli části **'Shell** okénka a následným stisknutím klávesnicové zkratky '**Ctrl**' + '**D**'.

## Použití

Ovládání softwaru při jeho provozu je vzhledem k minimálnímu počtu ovládacích prvků a omezeném počtu funkcí relativně intuitivní.

K zapnutí a vypnutí osvětlení slouží tlačítka připojená na pinech nakonfigurovaných v rámci souboru `boot.py`, tj. `BUTTON_1_PIN_NO`, `BUTTON_2_PIN_NO` a `BUTTON_3_PIN_NO`. Stiskem jakéhokoli z těchto tlačítkem během procesu zapínání osvětlení dojde k okamžitému zapnutí všech LED okruhů zároveň, stisknutím jakéhokoli tlačítka při vypínání dojde k jejich okamžitému vypnutí.

Změny nastavení osvětlení lze při běhu softwaru jednoduše provést pomocí enkodéru a displeje. Software umožňuje konfiguraci šesti různých nastavení rozprostřených na dvě stránky. Otáčením enkodéru je možné přecházet mezi jednotlivými možnostmi nastavení. Kurzor tvořený symbolem `>>` indikuje, na kterém nastavení se uživatel právě nachází. 

Stisknutím enkodéru je vybráno nastavení k editaci, načež se otáčením enkodéru mění hodnoty nastavení. Opětovaným stisknutím enkodéru je nové nastavení uloženo a enkodér přechází zpět do režimu výběru nového nastavení ke změně.

## Autorství

Software vyvinul Jindřich Kocman pro firmu Holweka s.r.o. [Odkaz na Github stránku autora](https://github.com/Azetbur).

## Licence

Software je vyvíjen pod licencí [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/).
