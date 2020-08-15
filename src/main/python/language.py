end="\nDrücken sie 'STRG + C' ('STEUERUNG CANCEL') <ENTER> um das Program zu beenden"
input_date = "Geben sie den Zeitpunkt an, an dem der Plot {} soll! \n\
\nDatum/Uhrzeit im Format 'DD-MM-YYYY HH:MM:SS'. Wird die Uhrzeit weggelassen, \n\
so wird 00:00:00 (Startzeit) bzw. 23:59:59 (Endzeit) angenommen.\n\
Werden Jahr oder Monat weggelassen wird (versucht) ein passendes Datum zu wählen.\n\
Lassen sie die Zeile leer um mit dem ersten existierenden Wert anzufangen \n\n\
list<ENTER> um eine Übersicht über die gefunden Datenwerte zu erhalten\n\n\
Beispiele für Formate (angenommen es ist der 12.01.2017): \n\n\
    11 12            -> 11.01.2017 12:00:00 \n\
    11-01            -> 11.01.2017 00:00:00 \n\
    13               -> 13.12.2016 00:00:00 \n\
    13-01-2017       -> 13.01.2017 00:00:00 \n\
    13-1-2017 17:1:4 -> 13.01.2017 17:01:04 (nuller können also weggelassen werden)\n"
hilfe=" oder h/help/hilfe <ENTER> für Hilfe\n"

LAN = {"DE":{},"EN":{}}

LAN["DE"]["input_first_date_help"]  = input_date.format("beginnen") + end + "\n"
LAN["DE"]["input_second_date_help"] = input_date.format("enden")    + end + "\n"
LAN["DE"]["input_first_date"]       = "\nStartzeit"+hilfe+"(Format: DD-MM-YY HH:MM:SS): "
LAN["DE"]["input_second_date"]      = "\nEndzeit  "+hilfe+"(Format: DD-MM-YY HH:MM:SS): "
LAN["DE"]["cannot_parse_date"]      = "Konnte Datum/Uhrzeit nicht verarbeiten! \n"
LAN["DE"]["dstart_bigger_dend"]     = "Startzeit > Endzeit. MÖÖÖÖP \n"
