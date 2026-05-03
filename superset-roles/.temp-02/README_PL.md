# Opcja 2 — Uprawnienia administratorskie do datasetow

Ten katalog zawiera wszystkie artefakty z badania i testowania **Opcji 2**: nadanie roli wlasciciela (`OPT2_Sublime_UserMgmt`) uprawnien administratorskich do datasetow, przy jednoczesnym zachowaniu uprawnien do dashboardow/chartow opartych na wlascicielstwie (tak jak w Opcji 1).

---

## Kluczowe odkrycie: Wymagany Custom Security Manager

Superset ma na sztywno zakodowane sprawdzanie wlascicielstwa w `raise_for_ownership()` — tylko uzytkownicy z rola **Admin** moga je ominac. Dodanie uprawnien `can_write Dataset` + `all_datasource_access` **nie wystarcza** do edycji/usuwania datasetow, ktorych nie jestesmy wlascicielem.

**Rozwiazanie:** Nadpisanie `CustomSecurityManager` w `superset_config.py`, ktore pomija sprawdzanie wlascicielstwa na obiektach `SqlaTable` dla uzytkownikow z rola `OPT2_Sublime_UserMgmt`.

---

## Porownanie Opcji 1 i Opcji 2

| Obszar | Opcja 1 | Opcja 2 |
|--------|---------|---------|
| Dashboardy | Edycja w zakresie wlascicielstwa | **Bez zmian** |
| Charty | Edycja w zakresie wlascicielstwa | **Bez zmian** |
| **Datasety** | **Brak edycji z poziomu UI** (tylko odczyt) | **Jak admin: edycja/usuwanie/tworzenie DOWOLNEGO datasetu** |
| SQL Lab | Pelny dostep dla wlasciciela | **Bez zmian** |
| Custom Security Manager | Nie wymagany | **Wymagany** |

### Roznica uprawnien (3 dodatkowe uprawnienia w OPT2_Sublime_UserMgmt vs Opcja 1)

| Uprawnienie | Widok | Cel |
|-------------|-------|-----|
| `can_write` | Dataset | Edycja/tworzenie/usuwanie datasetow |
| `can_save` | Datasource | Zapisywanie zmian w zrodle danych |
| `all_datasource_access` | all_datasource_access | Ominiecie kontroli dostepu per-dataset |

---

## Podsumowanie wynikow testow

**70 testow | 68 zaliczonych | 2 znane problemy**

| Kategoria | Testy | Zaliczone | Niezaliczone |
|-----------|:-----:|:---------:|:------------:|
| Dashboardy | 18 | 17 | 1 (znany) |
| Widocznosc dashboardow | 11 | 11 | 0 |
| **Datasety (fokus Opcji 2)** | **15** | **15** | **0** |
| Charty | 12 | 11 | 1 (znany) |
| SQL Lab | 6 | 6 | 0 |
| Tagi | 4 | 4 | 0 |
| Bazy danych | 4 | 4 | 0 |

**Wszystkie 15 testow datasetow ZALICZONE** — wlasciciel moze edytowac, usuwac, tworzyc i nadawac wlasciciela na DOWOLNYM datasecie.

2 znalezione problemy to ten sam blad z Opcji 1 — `can_write` laczy usuwanie z edycja (dashboardy + charty). Nie sa zwiazane ze zmianami w Opcji 2.

---

## Uzytkownicy i role testowe

| Uzytkownik | Nazwa uzytkownika | ID | Rola | Uprawnienia |
|------------|-------------------|:--:|------|:-----------:|
| Przegladajacy | `opt2-viewer` | 4 | `OPT2_Sublime_Starter` | 72 |
| Wlasciciel | `opt2-owner` | 5 | `OPT2_Sublime_UserMgmt` | 123 |

---

## Struktura katalogow

```
.temp-02/
├── README.md                                    ← Wersja angielska
├── README_PL.md                                 ← Jestes tutaj
├── report/
│   └── opt2-test-results.md                     ← Pelne wyniki testow (70 testow)
└── roles-deployment/
    ├── sublime-roles-backup-option2.json         ← Backup rol (72 + 123 uprawnienia)
    └── test-role-permissions-option2.py           ← Automatyczny skrypt testowy
```

---

## Wymagania wdrozeniowe

Aby wdrozyc Opcje 2 na innej instancji Superset:

1. **Dodaj CustomSecurityManager** do `superset_config.py` (zobacz `superset/config/superset_config.py` dla implementacji inline)
2. **Przywroc role** z `sublime-roles-backup-option2.json`
3. **Zaktualizuj nazwe roli** w CustomSecurityManager, jesli uzywasz innej nazwy niz `OPT2_Sublime_UserMgmt`
4. **Zrestartuj Superset**, aby zaladowac custom security manager
5. **Zaktualizuj uprawnienia specyficzne dla zrodel danych** w pliku JSON, aby pasowaly do srodowiska docelowego (tak samo jak w Opcji 1)

---

## Ocena ryzyka

| Ryzyko | Wplyw | Mitygacja |
|--------|-------|-----------|
| `all_datasource_access` daje dostep do WSZYSTKICH obecnych i przyszlych datasetow | Uzytkownicy automatycznie widza wszystkie dane | Akceptowalne dla roli z uprawnieniami administratorskimi do datasetow |
| CustomSecurityManager musi byc utrzymywany przy aktualizacjach Superset | Nadpisanie moze przestac dzialac przy wiekszej zmianie wersji | Przypiac wersje Superset, testowac po aktualizacjach |
| `can_write Dataset` obejmuje usuwanie (tak samo jak dashboardy) | Uzytkownicy moga usunac dowolny dataset | Celowe dla Opcji 2 |
| Dziala tylko dla konkretnej nazwy roli `OPT2_Sublime_UserMgmt` | Trzeba zaktualizowac kod jesli rola zostanie zmieniona | Jasna dokumentacja |
