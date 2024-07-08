# ESP_Vzorkovna_LED

**Ve zkratce: Tento repozitář obsahuje software na ovládání LED osvětlení vzorkovny za pomocí mikrokontroleru ESP32.**

Tento repozitář obsahuje software pro mikrokontroler ESP32, který slouží pro ovládní LED páskového osvětlení umístěného na regálech ve vzorkovně. Software zprostředkovává postupné zapínání jednotlivých LED okruhů za účelem minimalizace zátěže na elektroinsalaci budovy, rovněž umožňuje vypnutí osvětlení po vypršení nastaveného časového intervalu, konfiguraci průběhu zapnutí jednotlivých LED okruhů, apod. Průběh těchto funkcí, tj. např. interval vypínacího časovače,  je možné konfigurovat buď přímo ve zdrojovém kódu, či za pomocí rotačního enkodéru a displeje připojených k ESP32 mikrokontroleru zkrz zakázkově vyrobenou desku, v rámci které je mikrokontrolej zakomponován.

Sowtware pro tento projekt je vyvíkjen pouze v jazyce *Micropython*. Jádro softwaru tvoří ovladače pro jednotlivé fyzické prvky instalace, rozdělené do dvou adresářů. V adresáři `/my_drivers` se nachází ovladače zakázkově vyvinuté přimo pro tento projekt, tj. jmenovitě:

* `light_driver.py` - PWM ovladač jak jednotlivých okruhů LED osvětlení, tak celého osvětlení jako celku.
* `display_driver.py` - Jednoduchý ovladač běžného 4x20 LCD displeje ovládaného integrovaným obvodem *HD44780*.

Adresář `/third_party_drivers` je určen pro ovladače třetích stran. Momentálně obsahuje pouze ovladač rotačního enkodéru, skládající se ze dvou souborů, `rotary.py` a `rotary_irq_esp.py`.

Součástí softwaru jsou dále soubory `boot.py` a `controller.py` nacházející se v domovském adresáři repozitáře. Soubor `boot.py` slouží primárně ke konfiguraci pinů jednotlivých periferních zařízení, tj. displeje, LED obvodů apod. a inicializaci objektů reprezentujících tyto zařízení importovaných z jednotlivých výše zmíněných ovladačů. Soubor `controller.py`  propojuje všechny tyto jednotlivé prvky dohromady a zajišťuje jejich ovládání, tj. např. zapnutí osvětlení při stisknutí  vypínače, tisk nastavení na LCD displej apod.

## Instalace

Instalační postup je zcela standardní pro *micropython* program na  mikrokontroleru ESP32, tj. k němu lze využít nezpočet běžně dostupných nástrojů jako např. *uPyCraft IDE*, *Thonny IDE*, či nástroje přímo v příkazové řádce.

Následujíci sekce je určena primárně pro osoby neználé těchto nástrojů. Obsahuje detailní postup, jak naistalovat Micropython i tento software na ESP32 pomocí *Thonny IDE*.

*Thonny IDE* je volně dostupné vývojové prostředí pro *Windows*, *Linux* i *Mac*. Zde je odkaz na [webové stránky Thonny IDE](https://thonny.org/ "Thonny").

### Flash *MicroPython* Softwaru

*MicroPython* není v procesorech ESP32 naistalovaný z výroby, před instalací tohoto softwaru je tedy třeba na ESP32 jako první naistalovat _MicroPython_. Instalace probíhá následovně:

1. **Propojte ESP32 s počítačem, na kterém je software *Thonny IDE* naistalovaný**. Toto propojení je bežně provedeno propojením Micro-USB či USB-C portu, který se nachází na vývojové desce mikrokontroleru s počítačem za pomocí vhodného kabelu. **Ujistěte se, že kabel neslouží pouze k nabíjení, tj. že obsahuje i datové propoje.**

2. V *Thonny IDE* klikněte v levém horním okraji obrazovky na **Run**, v rozbalené nabídce následně klikněte na položku **Configure interpreter...**

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install foobar
```

## Usage

```python
import foobar

# returns 'words'
foobar.pluralize('word')

# returns 'geese'
foobar.pluralize('goose')

# returns 'phenomenon'
foobar.singularize('phenomena')
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)