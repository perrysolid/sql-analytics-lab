# Raport uprawnien ról w Superset

**Data wygenerowania:** 2026-03-02
**Instancja Superset:** http://localhost:8088

---

## Spis tresci

- [Podsumowanie](#podsumowanie)
- [Decyzje projektowe](#decyzje-projektowe)
- [Dostep do menu nawigacji](#dostep-do-menu-nawigacji)
- [Macierz uprawnien wg obiektów](#macierz-uprawnien-wg-obiektów)
  - [1. Dashboardy](#1-dashboardy)
  - [2. Charty](#2-charty)
  - [3. Datasety (Opcja 1 — Zarzadzane przez Notebook)](#3-datasety-opcja-1--zarzadzane-przez-notebook)
  - [4. Bazy danych](#4-bazy-danych)
  - [5. SQL Lab](#5-sql-lab)
  - [6. Tagi](#6-tagi)
  - [7. Eksploracja / Wizualizacja](#7-eksploracja--wizualizacja)
  - [8. Uzytkownicy i bezpieczenstwo](#8-uzytkownicy-i-bezpieczenstwo)
  - [9. Motywy](#9-motywy)
- [Kopia zapasowa i przywracanie](#kopia-zapasowa-i-przywracanie)

---

## Podsumowanie

Dwie dedykowane role zaprojektowane na podstawie dokumentu wymagan definiujacego model uprawnien per obiekt.
Datasety sa zarzadzane wylacznie przez zewnetrzne narzedzia (Jupyter notebook) — niedostepne do edycji z poziomu UI (Opcja 1).
Usuwanie dashboardów jest wykluczone z obu ról — obslugiwane przez zewnetrzna automatyzacje ("maszynke").

| Rola | ID | Przeznaczenie | Liczba uprawnien |
|------|----|---------------|-----------------|
| Sublime Starter | 6 | Przegladajacy — dostep tylko do odczytu z mozliwoscia kopiowania | 72 |
| Sublime User Management | 7 | Wlasciciel — pelne zarzadzanie posiadanymi obiektami + SQL Lab | 120 |

---

## Decyzje projektowe

1. **Zarzadzanie datasetami (Opcja 1):** Zadna z ról nie posiada `can_write Dataset`. Wszystkie zmiany w datasetach sa wykonywane przez automatyzacje Jupyter notebook. Pozwala to uniknac zlozonosci uprawnien zwiazanych z wlascicielstwem datasetów.

2. **Usuwanie dashboardów wykluczone:** Obie role nie maja uprawnien do usuwania dashboardów. Usuwanie jest obslugiwane przez zewnetrzna "maszynke" (Jupyter notebook), co zapewnia kontrolowany proces czyszczenia.

3. **Usuwanie chartów wykluczone:** Zadna z ról nie moze usuwac chartów z poziomu UI. Charty sa zarzadzane w ramach cyklu zycia dashboardu.

4. **Edycja ograniczona do wlasciciela:** Superset wymusza, ze `can_write Dashboard` pozwala na edycje tylko tych dashboardów, w których uzytkownik jest wymieniony jako wlasciciel. Dashboardy nienalezace do uzytkownika pozostaja w trybie tylko do odczytu nawet dla roli Wlasciciela.

5. **SQL Lab tylko dla Wlasciciela:** SQL Lab zapewnia bezposredni dostep do zapytan bazodanowych. Ograniczony do roli Wlasciciela, aby zapobiec niekontrolowanym zapytaniom do danych produkcyjnych przez uzytkowników przegladajacych.

6. **Kontrola dostepu na poziomie datasource:** Obie role uzywaja jawnych uprawnien `datasource_access` per dataset zamiast ogólnego `all_datasource_access`. Nowe datasety wymagaja aktualizacji uprawnien.

---

## Dostep do menu nawigacji

| Element menu | Sublime Starter | Sublime User Management |
|-------------|:-:|:-:|
| Home | T | T |
| Dashboards | T | T |
| Charts | T | T |
| Datasets | T | T |
| Databases | T | T |
| Data | T | T |
| Tags | T | T |
| SQL Lab | - | T |
| SQL Editor | - | T |
| Saved Queries | - | T |
| Query Search | - | T |
| Action Log | - | T |
| Themes | - | T |
| Plugins | - | - |

---

## Macierz uprawnien wg obiektów

### 1. Dashboardy

| Funkcjonalnosc | Sublime Starter | Sublime User Management | Uwagi |
|----------------|:-:|:-:|-------|
| Przegladanie dashboardów | T | T | `can_read Dashboard` |
| Kopiowanie / Zapisz jako | T | T | Przez `can_explore`, `can_slice` |
| Eksport / Pobieranie | T | T | `can_export Dashboard` |
| Edycja (jako wlasciciel) | - | T | `can_write Dashboard` |
| Przypisywanie wlascicieli | - | T | Przez `can_write Dashboard` |
| Przelaczanie Publish / Draft | - | T | Przez `can_write Dashboard` |
| Tagowanie dashboardów | - | T | `can_tag Dashboard` |
| Ustawianie/Usuwanie embedded | - | T | `can_set_embedded`, `can_delete_embedded` |
| Usuwanie dashboardu | - | - | Zablokowane na obu rolach; obslugiwane przez notebook |
| Drill into data | T | T | `can_drill Dashboard` |
| Podglad chartu jako tabela | T | T | `can_view_chart_as_table Dashboard` |
| Podglad zapytania | T | T | `can_view_query Dashboard` |
| Cache zrzutu ekranu | T | T | `can_cache_dashboard_screenshot Dashboard` |
| Udostepnianie linku | T | T | `can_share_dashboard Superset` |
| Stan filtrów (odczyt/zapis) | T | T | `DashboardFilterStateRestApi` |
| Permalink (odczyt/zapis) | T | T | `DashboardPermalinkRestApi` |

### 2. Charty

| Funkcjonalnosc | Sublime Starter | Sublime User Management | Uwagi |
|----------------|:-:|:-:|-------|
| Przegladanie chartów | T | T | `can_read Chart` |
| Eksport chartów | T | T | `can_export Chart` |
| Tworzenie nowych chartów | - | T | `can_write Chart` |
| Zapisz jako kopie | T | T | Przez explore + slice |
| Edycja (jako wlasciciel) | - | T | `can_write Chart` |
| Tagowanie chartów | - | T | `can_tag Chart` |
| Rozgrzewanie cache | - | T | `can_warm_up_cache Chart` |
| Udostepnianie linku | T | T | `can_share_chart Superset` |
| Usuwanie chartów | - | - | Zablokowane na obu rolach |

### 3. Datasety (Opcja 1 — Zarzadzane przez Notebook)

| Funkcjonalnosc | Sublime Starter | Sublime User Management | Uwagi |
|----------------|:-:|:-:|-------|
| Przegladanie datasetów | T | T | `can_read Dataset` |
| Informacje o drill | T | T | `can_get_drill_info Dataset` |
| Edycja datasetów | - | - | Zablokowane — Opcja 1 |
| Tworzenie datasetów | - | - | Zablokowane — Opcja 1 |
| Duplikowanie datasetów | - | T | `can_duplicate Dataset` |
| Eksport datasetów | - | T | `can_export Dataset` |
| Pobranie/Utworzenie referencji | - | T | `can_get_or_create_dataset` (do tworzenia chartów) |
| Rozgrzewanie cache | - | T | `can_warm_up_cache Dataset` |
| Podglad wartosci kolumn | - | T | `can_get_column_values Datasource` |
| Podglad próbek danych | - | T | `can_samples Datasource` |

### 4. Bazy danych

| Funkcjonalnosc | Sublime Starter | Sublime User Management | Uwagi |
|----------------|:-:|:-:|-------|
| Przegladanie baz danych | T | T | `can_read Database` |
| Edycja baz danych | - | - | Zablokowane na obu rolach |
| Upload do bazy danych | - | - | Zablokowane na obu rolach |

### 5. SQL Lab

| Funkcjonalnosc | Sublime Starter | Sublime User Management | Uwagi |
|----------------|:-:|:-:|-------|
| Dostep do SQL Lab | - | T | `can_sqllab Superset` |
| Wykonywanie zapytan | - | T | `can_execute_sql_query SQLLab` |
| Formatowanie SQL | - | T | `can_format_sql SQLLab` |
| Eksport CSV | - | T | `can_export_csv SQLLab` |
| Szacowanie kosztu zapytania | - | T | `can_estimate_query_cost SQLLab` |
| Podglad wyników | - | T | `can_get_results SQLLab` |
| Historia zapytan | - | T | `can_sqllab_history Superset` |
| Zapisane zapytania (odczyt) | T | T | `can_read SavedQuery` |
| Zapisane zapytania (zapis) | - | T | `can_write SavedQuery` |
| Zapisane zapytania (eksport) | - | T | `can_export SavedQuery` |
| Zarzadzanie zakladkami | - | T | `TabStateView` (activate, get, post, put, delete) |
| Przegladarka schematów tabel | - | T | `TableSchemaView` (post, expanded, delete) |
| SQL Lab permalink | - | T | `SqlLabPermalinkRestApi` |

### 6. Tagi

| Funkcjonalnosc | Sublime Starter | Sublime User Management | Uwagi |
|----------------|:-:|:-:|-------|
| Przegladanie tagów | T | T | `can_read Tag`, `can_list Tags` |
| Tworzenie/Edycja tagów | - | T | `can_write Tag`, `can_bulk_create Tag` |

### 7. Eksploracja / Wizualizacja

| Funkcjonalnosc | Sublime Starter | Sublime User Management | Uwagi |
|----------------|:-:|:-:|-------|
| Widok Explore | T | T | `can_read Explore` |
| Dane JSON z Explore | T | T | `can_explore_json Superset` |
| Dane formularza (odczyt/zapis) | T | T | `ExploreFormDataRestApi` |
| Permalink (odczyt/zapis) | T | T | `ExplorePermalinkRestApi` |
| Pobieranie metadanych datasource | T | T | `can_fetch_datasource_metadata Superset` |
| Eksport CSV | T | T | `can_csv Superset` |

### 8. Uzytkownicy i bezpieczenstwo

| Funkcjonalnosc | Sublime Starter | Sublime User Management | Uwagi |
|----------------|:-:|:-:|-------|
| Podglad wlasnych danych | T | T | `can_userinfo UserDBModelView` |
| Reset wlasnego hasla | T | T | `resetmypassword`, `ResetMyPasswordView` |
| Odczyt informacji o bezpieczenstwie | T | T | `can_read security`, `SecurityRestApi` |
| Odczyt danych uzytkownika | T | T | `can_read user` |
| Zapis biezacego uzytkownika | - | T | `can_write CurrentUserRestApi` |
| Podglad logu audytowego | - | T | `can_read Log`, `menu_access Action Log` |
| Row level security (odczyt) | T | T | `can_read RowLevelSecurity` |

### 9. Motywy

| Funkcjonalnosc | Sublime Starter | Sublime User Management | Uwagi |
|----------------|:-:|:-:|-------|
| Przegladanie motywów | T | T | `can_read Theme` |
| Edycja motywów | - | T | `can_write Theme` |
| Eksport motywów | - | T | `can_export Theme` |

---

## Kopia zapasowa i przywracanie

Konfiguracje ról sa przechowywane jako artefakty w `superset/config/role-backups/`:

| Plik | Przeznaczenie |
|------|---------------|
| `sublime-roles-backup.json` | Snapshot JSON obu ról z pelnym mapowaniem uprawnien |
| `restore-roles.py` | Skrypt Python przywracajacy role z kopii zapasowej JSON do Superset |

### Zawartosc kopii zapasowej

`sublime-roles-backup.json` zawiera dla kazdej roli:
- ID i nazwe roli
- Pelna liste uprawnien, kazde z `permission_view_id`, nazwa `permission` i nazwa `view_menu`
- Znacznik czasu eksportu i URL instancji zródlowej

### Przywracanie ról

Po swiezym `docker-compose down -v && docker-compose up -d --build` lub na nowej instancji Superset:

```bash
# 1. Skopiuj pliki kopii zapasowej do dzialajacego kontenera
docker cp superset/config/role-backups/restore-roles.py <SUPERSET_CONTAINER>:/app/
docker cp superset/config/role-backups/sublime-roles-backup.json <SUPERSET_CONTAINER>:/app/

# 2. Uruchom skrypt przywracania
docker exec <SUPERSET_CONTAINER> python3 /app/restore-roles.py
```

Skrypt wykona nastepujace operacje:
1. Utworzy role, jesli nie istnieja, lub zaktualizuje ich nazwy jesli ID juz istnieja
2. Usunie wszystkie istniejace uprawnienia dla kazdej roli
3. Ponownie wstawi wszystkie uprawnienia dopasowujac po nazwach `permission` + `view_menu` (nie po ID)
4. Wyswietli raport z liczba przywróconych uprawnien i liste pominionych

### Przenosnosc

Skrypt przywracania dopasowuje uprawnienia po **nazwie**, a nie po wewnetrznym ID. Oznacza to:
- Dziala na róznych instancjach Superset, gdzie ID moga sie róznic
- Jesli docelowa instancja nie posiada danego uprawnienia (np. datasource nie zostal jeszcze utworzony), zostanie ono pominiete z ostrzezeniem

### Uprawnienia specyficzne dla datasource

Plik kopii zapasowej (`sublime-roles-backup.json`) zawiera uprawnienia odwolujace sie do konkretnych polaczen z bazami danych, schematów i datasetów. Sa one **specyficzne dla projektu** i musza byc zaktualizowane w pliku JSON zgodnie z docelowa instancja Superset przed przywróceniem:

| Typ uprawnienia | Format w `view_menu` | Przyklad |
|----------------|----------------------|---------|
| `schema_access` | `[<NAZWA_BAZY>].[<NAZWA_DB>].[<NAZWA_SCHEMATU>]` | `[PostgreSQL].[playground].[nyc_taxi]` |
| `datasource_access` | `[<NAZWA_BAZY>].[<NAZWA_DATASETU>](id:<ID_DATASETU>)` | `[PostgreSQL].[trips_by_hour](id:1)` |

Przed przywróceniem ról w innym projekcie:
1. Otworz `sublime-roles-backup.json`
2. Znajdz wszystkie wpisy gdzie `permission` to `datasource_access` lub `schema_access`
3. Zaktualizuj wartosci `view_menu` aby odpowiadaly nazwie bazy danych, schematu i datasetów w docelowej instancji Superset
4. Odpowiednie datasety i polaczenia z bazami danych musza juz istniec w docelowym Superset przed przywróceniem

### Tworzenie nowej kopii zapasowej

Aby wyeksportowac biezacy stan ról jako nowa kopie zapasowa:

```bash
docker exec <SUPERSET_CONTAINER> python3 -c "
import sqlite3, json
from datetime import datetime

conn = sqlite3.connect('/app/superset_home/superset.db')
c = conn.cursor()

backup = {
    'exported_at': datetime.utcnow().isoformat() + 'Z',
    'superset_instance': 'http://localhost:8088',
    'roles': []
}

for role_id in [6, 7]:
    c.execute('SELECT id, name FROM ab_role WHERE id = ?', (role_id,))
    role_row = c.fetchone()
    c.execute('''
        SELECT pvr.id, p.name, vm.name
        FROM ab_permission_view_role pvr_role
        JOIN ab_permission_view pvr ON pvr_role.permission_view_id = pvr.id
        JOIN ab_permission p ON pvr.permission_id = p.id
        JOIN ab_view_menu vm ON pvr.view_menu_id = vm.id
        WHERE pvr_role.role_id = ?
        ORDER BY vm.name, p.name
    ''', (role_id,))
    permissions = [{'permission_view_id': r[0], 'permission': r[1], 'view_menu': r[2]} for r in c.fetchall()]
    backup['roles'].append({'id': role_row[0], 'name': role_row[1], 'permission_count': len(permissions), 'permissions': permissions})

conn.close()
print(json.dumps(backup, indent=2))
" > superset/config/role-backups/sublime-roles-backup.json
```
