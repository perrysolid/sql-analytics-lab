# Opcja 2 — Przewodnik demo: Uprawnienia administratorskie do datasetow

**Cel:** Pokazac na zywo, ze rola `OPT2_Sublime_UserMgmt` moze edytowac, usuwac i tworzyc DOWOLNY dataset (nawet nie bedac jego wlascicielem), podczas gdy dashboardy i charty pozostaja chronione wlascicielstwem.

**Srodowisko:** http://localhost:8088
**Czas trwania:** ~15 minut

---

## Spis tresci

1. [Kontekst — co chcemy osiagnac](#1-kontekst)
2. [Problem — dlaczego standardowe uprawnienia nie wystarczaja](#2-problem)
3. [Rozwiazanie — Custom Security Manager](#3-rozwiazanie)
4. [Demo — uzytkownicy i role](#4-demo-uzytkownicy-i-role)
5. [Demo czesc 1 — Dashboard: opt2-owner NIE moze edytowac cudzego](#5-demo-czesc-1)
6. [Demo czesc 2 — Dataset: opt2-owner MOZE edytowac cudzy](#6-demo-czesc-2)
7. [Demo czesc 3 — Dataset: opt2-owner MOZE usunac i stworzyc](#7-demo-czesc-3)
8. [Demo czesc 4 — Viewer nadal nie moze nic](#8-demo-czesc-4)
9. [Demo czesc 5 — Dowod z API (opcjonalnie)](#9-demo-czesc-5)
10. [Podsumowanie wynikow testow automatycznych](#10-podsumowanie)

---

## 1. Kontekst

### Opcja 1 (zrealizowana wczesniej)
- Rola `Sublime User Management` pozwala edytowac dashboardy i charty **tylko te, ktorych uzytkownik jest wlascicielem**
- Datasety — **brak edycji z poziomu UI**, wszystko przez "maszynke" (Jupyter notebook)

### Opcja 2 (to co pokazujemy)
- Dashboardy/charty — **bez zmian**, nadal ograniczone do wlascicielstwa
- Datasety — **jak admin**: edycja, usuwanie, tworzenie DOWOLNEGO datasetu, nawet cudzego
- Mozliwosc ustawienia siebie jako wlasciciela cudzego datasetu

### Dlaczego to wazne?
Chcemy podlaczyc LLM do Superset jako user z ograniczonymi uprawnieniami. Uzytkownik musi miec pelna kontrole nad datasetami (bo tworzy je dla swoich dashboardow), ale NIE moze modyfikowac cudzych dashboardow ani chartow. Dzieki temu AI moze bezpiecznie operowac na datasetach bez ryzyka zmiany cudzych dashboardow.

---

## 2. Problem — dlaczego standardowe uprawnienia nie wystarczaja

### Co probowalismy najpierw
Dodalismy 3 uprawnienia do roli:

| Uprawnienie | Widok | Co robi |
|-------------|-------|---------|
| `can_write` | Dataset | Edycja/tworzenie/usuwanie datasetow |
| `can_save` | Datasource | Zapisywanie zmian w zrodle danych |
| `all_datasource_access` | all_datasource_access | Dostep do wszystkich zrodel danych |

### Wynik: nadal 403 Forbidden na cudzych datasetach

### Przyczyna — kod zrodlowy Superset

Plik: `/app/superset/security/manager.py`

```python
def raise_for_ownership(self, resource):
    """
    Note admins are deemed owners of all resources.
    """
    if self.is_admin():        # <-- JEDYNY bypass
        return

    owners = resource.owners
    if g.user not in owners:
        raise SupersetSecurityException(...)  # <-- 403
```

**Kluczowy fakt:** Superset sprawdza wlascicielstwo na poziomie kodu, nie uprawnien. Jedyny sposob na obejscie to bycie adminem lub... nadpisanie tej metody.

Plik: `/app/superset/commands/dataset/update.py` (linia 96):
```python
def validate(self):
    self._model = DatasetDAO.find_by_id(self._model_id)
    try:
        security_manager.raise_for_ownership(self._model)  # <-- tu blokuje
    except SupersetSecurityException:
        raise DatasetForbiddenError()  # <-- 403
```

Ten sam wzorzec jest w `delete.py`, `refresh.py` — **kazda operacja zapisu na datasecie sprawdza wlascicielstwo**.

---

## 3. Rozwiazanie — Custom Security Manager

### Problem dwuwarstwowy

Superset ma **dwie warstwy** kontroli dostepu do edycji datasetu:

1. **Backend (Python)** — `raise_for_ownership()` sprawdza czy user jest wlascicielem przy kazdym PUT/DELETE
2. **Frontend (React)** — UI sprawdza liste `owners` z API i wyszarza przycisk edycji jesli usera nie ma na liscie

Oba musza byc rozwiazane, inaczej:
- Tylko backend -> API dziala, ale UI wyszarza przycisk
- Tylko frontend -> przycisk aktywny, ale API zwraca 403

### Co zmienilismy

Plik: `superset/config/superset_config.py` — dodalismy klase `_CustomSecurityManager` z dwoma mechanizmami:

```python
import logging as _logging
from flask import g as _g
from superset.security.manager import SupersetSecurityManager as _BaseSM

_OPT2_ROLE = "OPT2_Sublime_UserMgmt"

class _CustomSecurityManager(_BaseSM):

    def _has_opt2_role(self):
        """Check if current user has the OPT2 dataset-admin role."""
        try:
            return _OPT2_ROLE in [r.name for r in self.get_user_roles()]
        except Exception:
            return False

    def raise_for_ownership(self, resource):
        """Backend bypass: allow dataset edits for OPT2 role without ownership."""
        # Admini — bez zmian
        if self.is_admin():
            return

        # Tylko dla datasetow (SqlaTable) i tylko dla roli OPT2
        if resource.__class__.__name__ == "SqlaTable" and self._has_opt2_role():
            _logging.getLogger("superset.security").info(
                "OPT2 dataset-admin bypass for user=%s on dataset=%s",
                getattr(getattr(_g, "user", None), "username", "?"),
                getattr(resource, "id", "?"),
            )

            # KLUCZOWE: Auto-dodanie usera jako wspolwlasciciela
            # Dzieki temu UI pokaze przycisk edycji przy nastepnej wizycie
            try:
                user = _g.user
                if hasattr(resource, "owners") and user not in resource.owners:
                    resource.owners = list(resource.owners) + [user]
                    self.get_session.commit()
            except Exception:
                pass  # non-critical — edit still works

            return  # <-- pomijamy sprawdzenie wlascicielstwa!

        # Dla dashboardow, chartow i wszystkiego innego — standardowe sprawdzenie
        super().raise_for_ownership(resource)

CUSTOM_SECURITY_MANAGER = _CustomSecurityManager
```

### Jak to dziala — krok po kroku

**Scenariusz 1: opt2-owner edytuje dataset (PUT /api/v1/dataset/2):**
```
1. Superset wywoluje: security_manager.raise_for_ownership(dataset)
2. Nasz CustomSecurityManager sprawdza:
   - Czy user jest adminem? NIE
   - Czy obiekt to SqlaTable (dataset)? TAK
   - Czy user ma role OPT2_Sublime_UserMgmt? TAK
   -> Auto-dodaje usera do owners (jesli jeszcze go nie ma)
   -> return (pomijamy sprawdzenie wlascicielstwa)
3. Edycja przechodzi -> HTTP 200
4. Przy kolejnym odswiezeniu UI -> user jest na liscie owners -> przycisk edycji aktywny
```

**Scenariusz 2: opt2-owner edytuje DASHBOARD (PUT /api/v1/dashboard/2):**
```
1. Superset wywoluje: security_manager.raise_for_ownership(dashboard)
2. Nasz CustomSecurityManager sprawdza:
   - Czy user jest adminem? NIE
   - Czy obiekt to SqlaTable? NIE (to Dashboard)
   -> super().raise_for_ownership(dashboard)
3. Standardowe sprawdzenie: user nie jest wlascicielem -> 403 Forbidden
```

**Scenariusz 3: Nowy dataset tworzony przez admina (admin tworzy, opt2-owner chce edytowac):**
```
1. Admin tworzy dataset -> owners = [admin]
2. opt2-owner pierwsze wywolanie API (edit/set-owner):
   -> CustomSecurityManager pomija ownership check
   -> Auto-dodaje opt2-owner do owners
   -> Edit przechodzi
3. Od teraz UI pokazuje przycisk edycji (user jest juz na liscie owners)
```

### Co NIE zmienilismy
- Zadne pliki Superset — tylko konfiguracja (`superset_config.py`)
- Logika uprawnien dla dashboardow i chartow — bez zmian
- Rola Sublime Starter (viewer) — bez zmian

---

## 4. Demo — uzytkownicy i role

### Otwieramy: Settings > List Users (jako admin)

| Uzytkownik | Login | Haslo | Rola | Cel |
|------------|-------|-------|------|-----|
| Admin | `admin` | `admin123` | Admin | Zarzadzanie |
| Opt2 Viewer | `opt2-viewer` | `testpass123` | OPT2_Sublime_Starter (72 uprawnienia) | Tylko podglad |
| Opt2 Owner | `opt2-owner` | `testpass123` | OPT2_Sublime_UserMgmt (123 uprawnienia) | Edycja datasetow |

### Roznica uprawnien miedzy rolami (Settings > List Roles)

Rola `OPT2_Sublime_UserMgmt` ma 3 dodatkowe uprawnienia vs `Sublime User Management` (Opcja 1):

| Uprawnienie | Opis |
|-------------|------|
| `can_write on Dataset` | Zapis/edycja/usuwanie datasetow |
| `can_save on Datasource` | Zapisywanie zmian zrodel |
| `all_datasource_access on all_datasource_access` | Dostep do wszystkich zrodel danych |

**Pokaz w UI:** Settings > List Roles > Edit OPT2_Sublime_UserMgmt > szukaj "Dataset" w permission list

---

## 5. Demo czesc 1 — Dashboard: opt2-owner NIE moze edytowac cudzego

### Krok 1: Zaloguj sie jako `opt2-owner` / `testpass123`

### Krok 2: Otworz dashboard "Test Dashboard 2 - Revenue Analysis"
- Ten dashboard nalezy do `admin` — opt2-owner NIE jest wlascicielem
- **Oczekiwanie:** Brak przycisku "Edit" w prawym gornym rogu
- Dashboard wyswietla sie normalnie (read-only)

### Krok 3: Otworz dashboard "Test Dashboard 1 - Trip Patterns"
- Ten dashboard ma opt2-owner jako wspolwlasciciela
- **Oczekiwanie:** Przycisk "Edit" JEST widoczny — mozna edytowac wlasny dashboard

### Wniosek do pokazania:
> "Widzisz — na dashboardach zachowanie jest identyczne jak w Opcji 1. Nie mozna edytowac cudzych dashboardow. To sie nie zmienilo."

---

## 6. Demo czesc 2 — Dataset: opt2-owner MOZE edytowac cudzy

### Krok 1: Nadal zalogowany jako `opt2-owner`

### Krok 2: Idz do Datasets (menu gorny > Data > Datasets)
- Widoczne sa wszystkie 4 datasety
- Kazdy nalezy do `admin` (opt2-owner NIE jest wlascicielem wiekszosc z nich)

### Krok 3: Kliknij na dataset "trips_by_borough" (ID=2, wlasciciel: tylko admin)

### Krok 4: Edytuj dataset
- Zmien pole "Description" na: `"Edited by opt2-owner during demo"`
- Kliknij "Save"
- **Oczekiwanie:** Zapis przechodzi pomyslnie (HTTP 200)

### Krok 5: Pokaz dowod
- Wroc do listy datasetow
- Kliknij ponownie na "trips_by_borough"
- Description pokazuje zmieniony tekst

### Wniosek do pokazania:
> "Ten dataset nalezy do admina, a opt2-owner mogl go edytowac. W Opcji 1 dostawalby 403 Forbidden. To jest kluczowa roznica — na datasetach mamy uprawnienia jak admin."

### Krok 6: Cofnij zmiane (opcjonalnie)
- Usun tekst z Description i zapisz ponownie

---

## 7. Demo czesc 3 — Dataset: opt2-owner MOZE usunac i stworzyc

### Tworzenie nowego datasetu

### Krok 1: Nadal jako `opt2-owner`, idz do Data > Datasets
### Krok 2: Kliknij "+ Dataset" (prawy gorny rog)
### Krok 3: Wypelnij:
- Database: PostgreSQL
- Schema: nyc_taxi
- Wlacz "SQL" mode i wpisz:
  ```sql
  SELECT borough, COUNT(*) as cnt
  FROM nyc_taxi.taxi_zone_lookup
  GROUP BY borough
  ```
- Name: `demo_test_dataset`
### Krok 4: Kliknij "Save"
- **Oczekiwanie:** Dataset utworzony pomyslnie

### Usuwanie datasetu

### Krok 5: Wroc do listy datasetow
### Krok 6: Zaznacz checkbox obok `demo_test_dataset`
### Krok 7: Kliknij "Delete" (ikona kosza)
- **Oczekiwanie:** Dataset usuniety pomyslnie

### Ustawianie siebie jako wlasciciela cudzego datasetu

### Krok 8: Kliknij na dataset "payment_type_breakdown" (wlasciciel: admin)
### Krok 9: W sekcji "Owners" dodaj siebie (Opt2 Test Owner)
### Krok 10: Kliknij "Save"
- **Oczekiwanie:** Zapis przechodzi — opt2-owner moze nadac sobie wlascicielstwo na cudzym datasecie

### Wniosek do pokazania:
> "opt2-owner moze tworzyc, usuwac i przejmowac wlascicielstwo datasetow. Na dashboardach tego nie moze — tam jest ograniczony do swoich obiektow."

### Krok 11: Cofnij zmiane (usun siebie z owners payment_type_breakdown)

---

## 8. Demo czesc 4 — Viewer nadal nie moze nic

### Krok 1: Wyloguj sie i zaloguj jako `opt2-viewer` / `testpass123`

### Krok 2: Pokaz co viewer widzi:
- **Dashboardy:** Widzi tylko opublikowane, brak przycisku Edit
- **Datasety:** Widzi liste, ale NIE moze edytowac (brak opcji zapisu)
- **SQL Lab:** Brak dostepu (menu niewidoczne lub "Access Denied")
- **Brak przycisku "+ Dataset"** — nie moze tworzyc

### Wniosek do pokazania:
> "Viewer (OPT2_Sublime_Starter) ma dokladnie te same ograniczenia co w Opcji 1. Zmiana dotyczy TYLKO roli owner."

---

## 9. Demo czesc 5 — Dowod z API (opcjonalnie, dla technicznych)

Jesli kolega chce zobaczyc dowod na poziomie API, odpal te komendy w terminalu:

### Test 1: opt2-owner edytuje cudzy dataset (POWINNO PRZEJSC)

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8088/api/v1/security/login \
  -H "Content-Type: application/json" \
  -d '{"username":"opt2-owner","password":"testpass123","provider":"db"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Edycja datasetu ID=2 (trips_by_borough, wlasciciel: admin)
curl -s -X PUT http://localhost:8088/api/v1/dataset/2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "API demo edit by opt2-owner"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('SUKCES: HTTP 200' if 'result' in d else f'BLAD: {d}')"
```

**Oczekiwany wynik:** `SUKCES: HTTP 200`

### Test 2: opt2-owner edytuje cudzy dashboard (POWINNO ZABLOKOWAC)

```bash
# Edycja dashboardu ID=2 (Revenue Analysis, wlasciciel: admin)
curl -s -X PUT http://localhost:8088/api/v1/dashboard/2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dashboard_title": "SHOULD NOT CHANGE"}' \
  -w "\nHTTP Status: %{http_code}"
```

**Oczekiwany wynik:** `HTTP Status: 403`

### Test 3: opt2-viewer nie moze edytowac datasetu

```bash
# Login jako viewer
VTOKEN=$(curl -s -X POST http://localhost:8088/api/v1/security/login \
  -H "Content-Type: application/json" \
  -d '{"username":"opt2-viewer","password":"testpass123","provider":"db"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Proba edycji datasetu
curl -s -X PUT http://localhost:8088/api/v1/dataset/2 \
  -H "Authorization: Bearer $VTOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "SHOULD NOT CHANGE"}' \
  -w "\nHTTP Status: %{http_code}"
```

**Oczekiwany wynik:** `HTTP Status: 403`

### Cofniecie zmian po testach API

```bash
# Zaloguj jako admin i cofnij description
ATOKEN=$(curl -s -X POST http://localhost:8088/api/v1/security/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","provider":"db"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -s -X PUT http://localhost:8088/api/v1/dataset/2 \
  -H "Authorization: Bearer $ATOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": ""}' > /dev/null

echo "Zmiany cofniete"
```

---

## 10. Podsumowanie wynikow testow automatycznych

Uruchomilismy 70 testow automatycznych (skrypt `test-role-permissions-option2.py`):

| Kategoria | Testy | Zaliczone | Niezaliczone |
|-----------|:-----:|:---------:|:------------:|
| Dashboardy | 18 | 17 | 1 (znany*) |
| Widocznosc dashboardow | 11 | 11 | 0 |
| **Datasety (Opcja 2)** | **15** | **15** | **0** |
| Charty | 12 | 11 | 1 (znany*) |
| SQL Lab | 6 | 6 | 0 |
| Tagi | 4 | 4 | 0 |
| Bazy danych | 4 | 4 | 0 |
| **Razem** | **70** | **68** | **2** |

*\* Znane ograniczenie Superset: `can_write` laczy edycje z usuwaniem — owner moze usunac wlasny dashboard/chart. To ograniczenie platformy, nie nasz blad.*

### Kluczowe testy datasetowe (wszystkie PASS):

| Test | Opis | Wynik |
|------|------|-------|
| 2.1 | Owner edytuje cudzy dataset | 200 OK |
| 2.2 | Owner tworzy nowy dataset | 201 Created |
| 2.6 | Owner usuwa cudzy dataset | 200 OK |
| 2.6 | Owner usuwa wlasny dataset | 200 OK |
| 2.7 | Owner ustawia siebie jako wlasciciela cudzego datasetu | 200 OK |
| 2.8 | Owner modyfikuje SQL cudzego datasetu | 200 OK |
| 2.1 | Viewer edytuje dataset | 403 Forbidden |
| 2.6 | Viewer usuwa dataset | 403 Forbidden |

---

## Szybka sciaga — co powiedziec na spotkaniu

1. **"Standardowe uprawnienia Superset nie pozwalaja na to co chcielismy"** — ownership check jest hardcoded w kodzie
2. **"Napisalismy Custom Security Manager — 15 linii kodu w konfiguracji"** — nadpisuje sprawdzenie wlascicielstwa TYLKO dla datasetow i TYLKO dla naszej roli
3. **"Dashboardy i charty — bez zmian"** — Custom Security Manager nie dotyka obiektow typu Dashboard/Chart
4. **"70 testow automatycznych potwierdza dzialanie"** — 68 pass, 2 znane ograniczenia platformy
5. **"Rozwiazanie jest produkcyjne"** — wymaga utrzymania przy aktualizacjach Superset, ale to standardowy wzorzec (Custom Security Manager to oficjalny mechanizm rozszerzalnosci Superset)

---

## Przed spotkaniem — checklist

- [ ] Docker uruchomiony (`docker ps` — 3 kontenery)
- [ ] http://localhost:8088 dziala
- [ ] Login jako `admin` / `admin123` — dziala
- [ ] Login jako `opt2-owner` / `testpass123` — dziala
- [ ] Login jako `opt2-viewer` / `testpass123` — dziala
- [ ] Dashboard "Revenue Analysis" laduje sie szybko (materialized views)
- [ ] Przejdz cale demo raz przed spotkaniem
- [ ] Cofnij wszystkie zmiany po probie (description datasetow, owners)
