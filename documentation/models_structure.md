# Struttura del Database per Fantacalcio

Questo documento descrive la struttura dei modelli del database utilizzati per il sistema di gestione del Fantacalcio.

## Struttura dei Modelli

### Modelli di Base

#### Geografia e Identità

- `Continent`: Rappresenta un continente.
- `Nationality`: Rappresenta una nazionalità.
- `Person`: Informazioni base di una persona (nome, cognome, data di nascita, nazionalità).

#### Persone

- `Player`: Rappresenta un calciatore con ruolo, statistiche e valore di mercato.
- `Staff`: Rappresenta un membro dello staff tecnico.
- `Manager`: Rappresenta un allenatore o dirigente.

#### Squadre e Organizzazione

- `Team`: Rappresenta una squadra di calcio reale.
- `RosterSlot`: Rappresenta un posto nella rosa di una squadra.
- `SeasonTeam`: Rappresenta una squadra in una specifica stagione.

#### Statistiche e Storico

- `PlayerStatistics`: Statistiche complete di un giocatore (partite, gol, assist, ecc.).
- `MatchHistory`: Storico delle partite giocate.
- `Ranking`: Classifiche di vari tornei.

#### Tornei e Regole

- `Tournament`: Rappresenta un torneo (es. Serie A, Coppa Italia).
- `TournamentStructure`: Definisce la struttura di un torneo (girone, eliminazione diretta, ecc.).
- `TournamentRule`: Regole specifiche di un torneo.
- `TournamentQualificationRule`: Regole di qualificazione per un torneo.
- `TournamentRanking`: Classifiche specifiche per un torneo.
- `Trophy`: Trofei assegnati ai vincitori dei tornei.

#### Stagioni, Leghe, Giornate

- `Season`: Rappresenta una stagione calcistica.
- `League`: Rappresenta una lega calcistica.
- `Round`: Rappresenta una giornata di campionato.

#### Partite ed Eventi

- `Match`: Rappresenta una partita tra due squadre, con tutti i dettagli e statistiche.
- `MatchEvent`: Eventi durante una partita (gol, ammonizioni, ecc.).

#### Formazioni

- `Formation`: Rappresenta una formazione di una squadra.
- `DefaultFormation`: Formazione predefinita per una squadra.

#### Trasferimenti

- `Transfer`: Rappresenta un trasferimento di un giocatore tra squadre.

### Modelli per il Fantacalcio

#### Squadre Fantacalcio

- `FantaTeam`: Rappresenta una squadra di fantacalcio creata da un utente.
- `FantaTeamPlayer`: Relazione tra squadre di fantacalcio e giocatori con prezzo di acquisto.

#### Leghe Fantacalcio

- `FantaLeague`: Rappresenta una lega privata di fantacalcio tra utenti.
- `FantaLeagueRule`: Regole personalizzate per una lega di fantacalcio.

#### Formazioni Fantacalcio

- `FantaLineup`: Formazione schierata da un utente per una giornata.
- `FantaLineupPlayer`: Giocatore in una formazione di fantacalcio.
- `FantaLineupSubstitution`: Sostituzione automatica in una formazione.

#### Voti e Punteggi

- `FantaScore`: Voto di un giocatore in una partita con bonus/malus.

#### Mercato

- `MarketTransaction`: Transazione di mercato (acquisto, vendita, scambio).
- `AuctionBid`: Offerta in un'asta per un giocatore.

## Relazioni principali

1. Ogni `Player` è associato a una `Person` (dati anagrafici).
2. Ogni `FantaTeam` è associato a un utente `User` (proprietario) e a una `Season`.
3. Ogni `FantaLeague` è associata a un `Tournament` e a una `Season`.
4. Ogni `Match` è associato a un `Tournament` e a un `Round`.
5. Ogni `FantaScore` è associato a un `Player` e a un `Match`.
6. Ogni `FantaLineup` è associata a un `FantaTeam` e a un `Round`.

## Punti di forza del design

1. **Separazione dei concetti**: Distinzione chiara tra entità reali (giocatori, squadre) ed entità del fantacalcio.
2. **Flessibilità**: Supporto per diverse tipologie di competizioni e regole.
3. **Scalabilità**: Possibilità di estendere facilmente il sistema con nuove funzionalità.
4. **Tracciamento completo**: Registrazione dettagliata di statistiche, voti e punteggi.
5. **Sistema di mercato avanzato**: Supporto per diverse modalità di trasferimento e aste.
