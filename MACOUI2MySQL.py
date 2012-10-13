from compiler.ast import Or

#######################
##  Script Settings  ##
#######################

MailFrom = "user <user@server.name>"
MailTo = "Your Name <Name@Your.MailBox>"
MailSubject = "MAC OUI Import"

OUIDateiURL = "http://standards.ieee.org/develop/regauth/oui/oui.txt"
OUITmpDatei = "/tmp/oui.txt"

LogErrorFile = "MACOUI2MySQL.err.log"
LogOutputFile = "MACOUI2MySQL.out.log"

MySQLUsername = ""
MySQLPassword = ""
MySQLHostname = "localhost"
MySQLDatabase = ""
MySQLTable = "MACOUI"

#############################
##      Python Script      ##
#############################

import MySQLdb
import sys
import os
import time
import urllib2
import email
import smtplib


# Standard Output / Error Streams
sys.stdout = open(LogOutputFile, "w")
sys.stderr = open(LogErrorFile, "w")


# MAC OUI Datei Downloaden und speichern
DownloadOUI = urllib2.urlopen(OUIDateiURL)

tmpOUI = open(OUITmpDatei, "w")
tmpOUI.write(DownloadOUI.read())
tmpOUI.close()


# Temp Datei oui.txt oeffnen
fobj = open(OUITmpDatei, "r")


# Datenbank Verbindung aufbauen
conn = MySQLdb.connect (host=MySQLHostname, user=MySQLUsername, passwd=MySQLPassword, db=MySQLDatabase)

# Datenbank Cursor
cursor = conn.cursor()


# Variablen fuer den Import in die DB
MAC = ""
Address = ""
Organization = ""
CountImport = 0
CountUpdate = 0
CountError = 0
CountAddressError = 0

# Datei auslesen und importieren
i = 0
for Zeile in fobj: 
    
    i += 1       
    if i > 6:
        
        # Preufe auf erste Zeile
        if Zeile.find("(hex)\t\t") != -1:
            
            tmp = Zeile.replace("   (hex)\t\t", ";").split(";")
            
            Address = ""
            MAC = tmp[0].replace("-", ":")
            Organization = tmp[1].replace("\n", "").replace("'", "&lsquo;")            
            
            
        # Zweite Zeile ueberspringen
        elif Zeile.find("(base 16)") != -1:
            continue
        
        # Adresse zusammen packen
        elif Zeile.find("\t\t\t\t") != -1:
            
            tmp = Zeile.replace("\t\t\t\t", "")
            Address += tmp.replace("'", "&lsquo;")
            
        
        # Werte in der Datenbank sichern
        else:
            if i > 6:
                
                try:    
                    # Datensatz einfuegen
                    cursor.execute("INSERT INTO " + MySQLTable + " ( OUI, Organization, Address ) VALUES ('" + MAC + "', '" + str(Organization) + "', '" + str(Address) + "')")
                    conn.commit()
                    CountImport += 1
                    
                except:
                    
                    # Datensatz ohne Address einpflegen                    
                    try:
                        cursor.execute("INSERT INTO " + MySQLTable + " ( OUI, Organization, Address ) VALUES ('" + MAC + "', '" + str(Organization) + "', '')")
                        conn.commit()
                        CountImport += 1
                        CountAddressError += 1
                        sys.stderr.write(time.strftime("%d.%m.%Y %H:%M:%S Uhr\n") )
                        sys.stderr.write("SQL Fehlgeschlagen: INSERT INTO " + MySQLTable + " ( OUI, Organization, Address ) VALUES ('" + MAC + "', '" + str(Organization) + "', '" + str(Address) + "')")
                        
                    except:
                    
                        try:
                            # Datensatz updaten
                            cursor.execute("UPDATE " + MySQLTable + " SET Organization = '" + str(Organization) + "', Address = '" + str(Address) + "' WHERE OUI = '" + MAC + "'")
                            conn.commit()
                            CountUpdate += 1
                            
                        except:
                            
                            try:
                                # Datensatz updaten ohne Address
                                cursor.execute("UPDATE " + MySQLTable + " SET Organization = '" + str(Organization) + "' WHERE OUI = '" + MAC + "'")
                                conn.commit()
                                CountUpdate += 1
                                CountAddressError += 1
                                sys.stderr.write(time.strftime("%d.%m.%Y %H:%M:%S Uhr\n") )
                                sys.stderr.write("SQL Fehlgeschlagen: UPDATE " + MySQLTable + " SET Organization = '" + str(Organization) + "', Address = '" + str(Address) + "' WHERE OUI = '" + MAC + "'\n\n")
                                
                            except:
                                # Next Line
                                CountError += 1
                                sys.stderr.write(time.strftime("%d.%m.%Y %H:%M:%S Uhr\n") )
                                sys.stderr.write("SQL Fehlgeschlagen: UPDATE " + MySQLTable + " SET Organization = '" + str(Organization) + "' WHERE OUI = '" + MAC + "'\n\n")                        
                                continue


# Ausgabe Text nach dem Import Vorgang
sys.stdout.write("MAC OUI nach MySQL importieren\n\n")   
sys.stdout.write("Es wurden " + str(CountImport) + " Datensaetze importiert\n")
sys.stdout.write("Es wurden " + str(CountUpdate) + " Datensaetze aktualisiert\n")


try:
    cursor.execute("OPTIMIZE TABLE  computer.macoui")
    conn.commit()
except:
    sys.stdout.write("\n\nFehler: Die Tabelle MACOUI konnte nicht optimiert werden !")           


if CountAddressError > 0:    
    sys.stdout.write("\n" + str(CountAddressError) + " OUI sind ohne Adresse vorhanden !\n")
    
if CountError > 0 :
    sys.stdout.write("\nWaehrend des Importvorganges sind " + str(CountError) + " Fehler aufgetreten !\n")


# Schliessen der ARP Datei
fobj.close()

# Schliessen der DB Verbindung
cursor.close()
conn.close()

# Schliessen der Logs
sys.stderr.close()
sys.stdout.close()


# E-Mail versenden
    
from email.message import Message

msg = Message()
log = open(LogOutputFile, "r")

# Error Log Datei auslesen
Text = ""
for line in log:
    Text += line

log.close()

# EMail erzeuegen
msg.attach(LogErrorFile) # toDo
msg.set_payload(Text) 
msg["Subject"] = MailSubject 
msg["From"] = MailFrom
msg["To"] = MailTo

# EMail verschicken
server = smtplib.SMTP('localhost')
server.sendmail(MailFrom, MailTo, msg.as_string())
server.quit()


# Alle Dateien loeschen
os.remove(OUITmpDatei)
os.remove(LogOutputFile)
os.remove(LogErrorFile)

