# Über die Daten
Bei den Datenquellen haben wir uns an bereits öffentlich zugänglichen Daten orientiert, die einen direkten oder mittelbaren Rückschlusss auf Aktivitäten des öffentlichen Lebens erlauben. Weitere Datenquellen sind jederzeit integrierbar und willkommen.


## Daten im Dashboard
### Autoverkehr
**Basis:** [TomTom](https://developer.tomtom.com/)

Basierend auf Daten von TomTom kann die Verkehrsdichte auf den Strassen ausgelesen werden. 
### Menschen an Haltestellen des ÖPNV
**Basis:** [Google Maps](https://maps.google.com)

Google bietet über seinen Dienst Google Maps Transit die Funktion an, zu zeigen, wann ÖPNV Haltestellen wie stark frequentiert sind. Diese Daten haben Philipp auf die Projektidee gebracht und waren die erste Datenquelle.
### Fußgänger in Innenstädten (Laserscanner-Messung) 
**Basis:** [hystreet.com](https://hystreet.com)

hystreet.com misst die Passantenfrequenz innerstädtischer Einzelhandelslagen mit Hilfe von Laserscannern an 117 Standorten in 57 Städten. Hystreet hat uns API-Zugriff gewährt und wir können daher sowohl auf stündlich aktualisierte Zahlen, als auch auf mehrere Jahre zurückliegende Daten zugreifen.

![Hystreet Aufbau](https://images.everyonecounts.de/hystreet.jpg)

### Fußgänger auf öffentlichen Webcams
Es gibt viele öffentliche Webcams, die belebte und beliebte Orte in unseren Städten zeigen. Durch Bilderkennungsprozesse werden Menschen auf den Bildern als solche erkannt und gezählt. Die Webcams werden zur Zeit stündlich abgefragt.

![Beispiel Webcamauswertung](https://images.everyonecounts.de/webcam.jpg)

### Fahrradfahrer 
**Basis:** [Eco-Compteur](https://www.eco-compteur.com/)

In vielen Innenstädten werden Fahrradfahrer an automatisierten Messstellen gezählt und von [Eco-Compteur](https://www.eco-compteur.com/) online gestellt. Die Daten der 42 deutschen Messstellen werden für unseren Datenpool abgerufen. Beispiel: http://eco-public.com/public2/?id=100004595

![Fahradzählstation](https://images.everyonecounts.de/fahrradzaehler.jpg)

## weitere Daten die schon aggregiert werden
### Lemgo Digital
**Basis:** [Lemgo Digital - Frauenhofer IOSB-INA](https://lemgo-digital.de/index.php/de/)

Diese Daten stammen aus dem Fraunhofer IoT-Reallabor Lemgo Digital. Sie umfassen Passantenfrequenzen sowie Lärm- und Verkehrsdaten an verschiedenen Orten der Stadt. Die Echtzeitdaten werden über entsprechende Sensoren durch das Fraunhofer IOSB-INA selber erfasst und werde in der Urban Data Platform auf Basis von FIWARE verarbeitet. Die Bereitstellung für das Projekt erfolgt als csv-Datei per https Request.

### Parkhäuser
**Basis:** Webseiten von Parkhäusern

Viele Parkhausbetreiber stellen die Auslastungsdaten ihrer Parkhäuser über Webseiten zur Verfügung. Über diese Auslastung lässt sich ebenfalls ablesen, wie frequentiert die Innenstädte noch sind. 

### Luftqualität
**Basis:** [World Air Qwuality Project](https://waqi.info/de/)

Durch die Auswertung von Sensoren für die Luftqualität lassen sich Rückschlüsse auf das Verkehrsaufkommen schliessen. Daher werden auch diese Sensoren für die Erkennung des social distancing genutzt. Wir verwenden die Daten von 402 deutschen Messstationen des World Air Quality Projects und haben so Einblick in Parameter wie die lokale Konzentration von Stickoxiden, Schwefeldioxid, Kohlenstoffmonoxid Feinstaub, Ozon und lokale Wetterdaten (Temperatur, Luftfeuchtigkeit, Luftdruck).

## Aggregation und Datenaufbereitung
Da jede Datenquelle andere Daten bereitstellt und sich die Granularität unterscheidet, werden die Daten aggregiert in einer Datenbank gespeichert. Dabei werden die Geokoordinaten den Landkreisen und Bundesländern zugewiesen. Als zeitliche Aggregation haben wir uns fürs erste auf eine Tagesbasis festgelegt. So liegen die Daten auch in der Datenbank vor. Die aggregierten Daten werden jeweils gegen Referenzdaten des gleichen Wochentags berechnet. Der Score ergibt sich aus der prozentualen Abweichung des aktuellen Wertes im Vergleich zu einem Referenzpunkt. Dabei entsprechen 100% einem normalem Aktivitätsniveau und somit normalem Social Distancing. Kleinere Werte sind ein Indiz für ein gutes Social Distancing, da weniger Menschen unterwegs sind.

## Abfragezeitraum

Unsere Daten sind prinzipiell tagesaktuell. Der Zeitraum, ab dem wir Daten vorliegen haben unterscheidet sich je nach Quelle. Hier ist aufgelistet, wie weit unsere Rohdaten zurück reichen:

| Datenquelle  | verfügbar ab  |
|--------------|---------|
| Fahrräder  |  01.01.2013 |
| Google Places  | 22.03.2020  |
| Google Places Shops  | 28.03.2020  |
| Google Places Supermarket | 27.03.2020 |
| Hystreet (Fußgänger) | 01.05.2018  |
| Fraunhofer Reallabor Lemgo | 26.03.2020  |
| TomTom | 18.03.2020  |
| Webcams | 21.03.2020 |

## Datenzugriff

Wenn Du als Data Scientist, Datenjournalist oder auch einfach "interessierter Bürger" Zugriff auf die Rohdaten des Dashboards möchtest um Deine eigenen Analysen anzustellen musst Du nicht einmal fragen. Die Daten aus dem Dashboard kannst Du ganz einfach [hier herunterladen](https://im6qye3mc3.execute-api.eu-central-1.amazonaws.com/prod) (es gilt die [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt)). Zudem gibt es einen Web Feature Service (WFS) mit den Daten unter [geoserver.everyonecounts.de](https://geoserver.everyonecounts.de/). 

Manche der oben genannten Daten sind (noch) nicht im Dashboard integriert. Sie sollen über eine API verfügbar gemacht werden, die sich bereits in Arbeit befindet. Du kannst uns aber gerne kontaktieren, wenn Du diese Daten bereits jetzt nutzen möchtest.


<!-- Matomo Image Tracker-->
<img src="https://matomo.everyonecounts.de/matomo.php?idsite=1&amp;rec=1&amp;action_name=about_our_data" style="border:0" alt="" />
<!-- End Matomo -->