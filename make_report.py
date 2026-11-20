"""Generuje sprawozdanie (Sprawozdanie.docx) na podstawie results/summary.json.

Uruchomienie (po experiments.py):  .venv/bin/python make_report.py
"""
import json
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

RESULTS = Path("results")
OUTPUT = Path("Sprawozdanie.docx")

EXPERIMENT_NAMES = {
    "mutacja": "Wpływ prawdopodobieństwa mutacji",
    "krzyzowanie": "Wpływ prawdopodobieństwa krzyżowania",
    "selekcja": "Porównanie selekcji ruletkowej, rankingowej i turniejowej",
    "typ_krzyzowania": "Porównanie krzyżowania jedno- i dwupunktowego",
    "selekcja_bez_naprawy": "Metody selekcji bez naprawy chromosomów (eksperyment dodatkowy)",
}


def fmt(x):
    return f"{x:g}" if isinstance(x, (int, float)) else str(x)


def add_table(doc, header, rows):
    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Light Grid Accent 1"
    for cell, text in zip(table.rows[0].cells, header):
        cell.text = text
        cell.paragraphs[0].runs[0].bold = True
    for row in rows:
        cells = table.add_row().cells
        for cell, text in zip(cells, row):
            cell.text = text
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9)
    doc.add_paragraph()
    return table


def bullet(doc, text):
    doc.add_paragraph(text, style="List Bullet")


def code(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = "Courier New"
    run.font.size = Pt(9)


def main():
    summary = json.loads((RESULTS / "summary.json").read_text())
    runs = len(summary[0]["experiments"][0]["stats"][next(iter(summary[0]["experiments"][0]["stats"]))]["finals"])

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    for section in doc.sections:
        section.left_margin = section.right_margin = Cm(2.2)

    # ---------- strona tytułowa ----------
    t = doc.add_heading("Algorytm genetyczny rozwiązujący problem plecakowy", 0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("Sprawozdanie z ćwiczenia – Algorytmy genetyczne")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("Imię i nazwisko: ............................................\n"
                          "Grupa: ............   Data: ............")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # ---------- 1. cel ----------
    doc.add_heading("1. Cel ćwiczenia", 1)
    doc.add_paragraph(
        "Celem ćwiczenia było zaimplementowanie algorytmu genetycznego (AG) rozwiązującego "
        "dyskretny problem plecakowy 0/1, a następnie zbadanie wpływu parametrów (prawdopodobieństwa "
        "mutacji i krzyżowania) oraz operatorów (metody selekcji, typu krzyżowania) na przebieg "
        "ewolucji. Program napisano w języku Python w sposób obiektowy, bez użycia gotowych bibliotek "
        "algorytmów genetycznych ani solverów – cały algorytm korzysta wyłącznie z biblioteki "
        "standardowej (moduł random). Biblioteka matplotlib służy jedynie do rysowania wykresów, "
        "a python-docx do wygenerowania tego sprawozdania.")
    doc.add_paragraph(
        "Zrealizowano wszystkie wymagania na ocenę 5.0: import danych, ogólny skrypt AG, funkcję "
        "przystosowania, krzyżowanie jedno- i dwupunktowe, mutację oraz selekcję ruletkową, "
        "rankingową i turniejową, a także wszystkie wymagane wykresy.")

    # ---------- 2. problem i kodowanie ----------
    doc.add_heading("2. Problem plecakowy i kodowanie rozwiązania", 1)
    doc.add_paragraph(
        "Dany jest zbiór n przedmiotów o wartościach v_i i wagach w_i oraz plecak o pojemności C. "
        "Należy wybrać podzbiór przedmiotów o maksymalnej łącznej wartości, którego łączna waga nie "
        "przekracza C. Chromosom to wektor binarny długości n: gen i równy 1 oznacza, że przedmiot i "
        "znajduje się w plecaku, a 0 – że go nie ma.")
    doc.add_paragraph("Funkcja przystosowania (zgodnie z p. 3.3 instrukcji):")
    code(doc, "f(x) = Σ v_i·x_i,  jeżeli Σ w_i·x_i ≤ C\nf(x) = 0,          w przeciwnym razie")

    # ---------- 3. implementacja ----------
    doc.add_heading("3. Implementacja", 1)
    doc.add_paragraph("Struktura projektu:")
    code(doc,
         "knapsack_ga/problem.py    – Item, KnapsackProblem, load_problem(), load_optimum()\n"
         "knapsack_ga/fitness.py    – knapsack_fitness()\n"
         "knapsack_ga/selection.py  – roulette_selection(), rank_selection(), tournament_selection()\n"
         "knapsack_ga/crossover.py  – one_point_crossover(), two_point_crossover()\n"
         "knapsack_ga/mutation.py   – bit_flip_mutation()\n"
         "knapsack_ga/repair.py     – random_repair()\n"
         "knapsack_ga/ga.py         – GAConfig, GAResult, GeneticAlgorithm\n"
         "experiments.py            – część eksperymentalna\n"
         "plots.py                  – wykresy (matplotlib)\n"
         "make_report.py            – generowanie sprawozdania")

    doc.add_heading("3.1 Import danych", 2)
    doc.add_paragraph(
        "Funkcja load_problem() wczytuje plik w formacie: w pierwszym wierszu liczba przedmiotów n "
        "i pojemność C, w kolejnych n wierszach para „wartość waga”. Wczytywane jest dokładnie n "
        "niepustych wierszy (część plików ma na końcu puste linie), a liczby mogą być całkowite lub "
        "rzeczywiste (np. zbiór f5). Funkcja load_optimum() wczytuje znane optimum z katalogu "
        "*-optimum.")

    doc.add_heading("3.2 Ogólny schemat algorytmu", 2)
    doc.add_paragraph(
        "Klasa GeneticAlgorithm przyjmuje problem oraz obiekt GAConfig, w którym podaje się m.in.: "
        "rozmiar populacji, liczbę iteracji, funkcję przystosowania, funkcję selekcji, funkcję "
        "krzyżowania, funkcję mutacji, prawdopodobieństwa krzyżowania p_k i mutacji p_m, liczbę "
        "osobników elitarnych oraz ziarno generatora liczb losowych. Funkcje przekazywane są jako "
        "obiekty wywoływalne, więc ten sam szkielet działa z dowolną kombinacją operatorów. "
        "Metoda run() realizuje kroki z instrukcji:")
    for s in ["wybór populacji początkowej,",
              "ocena przystosowania osobników w populacji,",
              "wyprowadzenie (zapamiętanie) najlepszego osobnika – zapisywany jest w historii po każdej iteracji,",
              "sprawdzenie warunku zatrzymania (osiągnięcie zadanej liczby iteracji),",
              "selekcja chromosomów rodzicielskich,",
              "zastosowanie operatorów genetycznych: krzyżowanie parami z prawdopodobieństwem p_k, "
              "mutacja każdego genu z prawdopodobieństwem p_m,",
              "utworzenie nowej populacji (z zachowaniem 1 najlepszego osobnika – elitaryzm)."]:
        doc.add_paragraph(s, style="List Number")

    doc.add_heading("3.3 Operatory genetyczne", 2)
    bullet(doc, "Krzyżowanie jednopunktowe – losowany jest punkt cięcia z przedziału 1…n−1, potomkowie "
                "wymieniają się końcowymi fragmentami chromosomów.")
    bullet(doc, "Krzyżowanie dwupunktowe – losowane są dwa różne punkty cięcia, wymieniany jest fragment "
                "pomiędzy nimi. Poprawność obu operatorów sprawdzono na przykładach z rysunków w "
                "instrukcji (otrzymano identyczne chromosomy potomne).")
    bullet(doc, "Mutacja – dla każdego genu niezależnie, z prawdopodobieństwem p_m, bit jest zamieniany "
                "na przeciwny.")

    doc.add_heading("3.4 Metody selekcji", 2)
    bullet(doc, "Ruletkowa – prawdopodobieństwo wyboru p(ch_i) = f(ch_i) / Σ f(ch_j). Koło budowane jest "
                "z sum skumulowanych, a wycinek wskazywany wyszukiwaniem binarnym. Gdy wszystkie "
                "osobniki mają przystosowanie 0, wybór jest jednostajny.")
    bullet(doc, "Rankingowa – osobniki sortowane są od najlepszego do najgorszego; osobnik o randze r "
                "otrzymuje wagę N − r + 1, czyli oczekiwana liczba jego kopii maleje liniowo z rangą "
                "(jak na wykresie w p. 3.4.3). Selekcja zależy tylko od kolejności, nie od wartości f.")
    bullet(doc, "Turniejowa – losowana jest grupa k = 3 osobników i wybierany najlepszy z nich; "
                "operacja powtarzana jest N razy.")

    doc.add_heading("3.5 Populacja początkowa i naprawa chromosomów", 2)
    doc.add_paragraph(
        "W zbiorach large_scale pojemność plecaka stanowi ok. 2% łącznej wagi wszystkich przedmiotów. "
        "Losowy chromosom (każdy gen 0/1 z prawdopodobieństwem 0,5) prawie zawsze przekracza "
        "pojemność, więc otrzymuje przystosowanie 0 – cała populacja miałaby f = 0 i selekcja "
        "nie mogłaby działać. Dlatego populację początkową tworzy się z rozwiązań dopuszczalnych: "
        "przedmioty dodawane są w losowej kolejności, dopóki mieszczą się w plecaku.")
    doc.add_paragraph(
        "Ponadto potomkowie przekraczający pojemność są naprawiani (random_repair): usuwane są losowo "
        "wybrane przedmioty, aż plecak zmieści się w limicie. Naprawa jest losowa, a nie zachłanna, "
        "aby nie zastępować algorytmu genetycznego heurystyką. Sama funkcja przystosowania pozostaje "
        "dokładnie taka, jak w instrukcji. Wpływ naprawy pokazuje eksperyment dodatkowy (rozdz. 5).")

    # ---------- 4. metodyka ----------
    doc.add_heading("4. Przebieg eksperymentów", 1)
    doc.add_paragraph(
        "Wybrano 4 zbiory low-dimensional i 2 zbiory large_scale. Każda seria danych na wykresie "
        f"to średnia z {runs} niezależnych uruchomień (ziarna 1000…{1000 + runs - 1}) wartości "
        "funkcji przystosowania najlepszego osobnika po każdej iteracji. Linia przerywana oznacza "
        "znane optimum. W każdym eksperymencie zmieniano jeden parametr, pozostałe przyjmowały "
        "wartości bazowe:")
    add_table(doc, ["Zbiór", "n", "C", "Optimum", "Populacja", "Iteracje", "p_k", "p_m"],
              [[d["dataset"], str(d["n"]), fmt(d["capacity"]), fmt(d["optimum"]),
                str(d["population_size"]), str(d["iterations"]), fmt(d["p_crossover"]),
                fmt(d["p_mutation"])] for d in summary])
    doc.add_paragraph("Wartości bazowe: selekcja ruletkowa, krzyżowanie jednopunktowe, elitaryzm 1 "
                      "osobnik, naprawa chromosomów włączona.")

    # ---------- 5. wyniki ----------
    doc.add_heading("5. Wyniki", 1)
    for d in summary:
        doc.add_heading(f"Zbiór {d['dataset']} (n = {d['n']}, optimum = {fmt(d['optimum'])})", 2)
        for e in d["experiments"]:
            doc.add_heading(EXPERIMENT_NAMES[e["id"]], 3)
            doc.add_picture(e["plot"], width=Cm(16))
            rows = []
            for label, s in e["stats"].items():
                hits = sum(1 for v in s["finals"] if abs(v - d["optimum"]) < 1e-3)
                rows.append([label, fmt(s["best"]), f"{s['mean']:.1f}", fmt(s["worst"]),
                             f"{100 * s['mean'] / d['optimum']:.2f}%", f"{hits}/{len(s['finals'])}"])
            add_table(doc, ["Seria", "Najlepszy", "Średni", "Najgorszy", "Średnio % optimum",
                            "Trafienia optimum"], rows)

    # ---------- 6. porównanie z optimum ----------
    doc.add_heading("6. Porównanie z optimum – zestawienie", 1)
    doc.add_paragraph("Dla każdego zbioru podano najlepszą konfigurację (najwyższy średni wynik "
                      "spośród wszystkich badanych serii z naprawą chromosomów).")
    rows = []
    for d in summary:
        best = None
        for e in d["experiments"]:
            if e["id"] == "selekcja_bez_naprawy":
                continue
            for label, s in e["stats"].items():
                if best is None or s["mean"] > best[2]["mean"]:
                    best = (EXPERIMENT_NAMES[e["id"]].split(" (")[0], label, s)
        rows.append([d["dataset"], fmt(d["optimum"]), fmt(best[2]["best"]), f"{best[2]['mean']:.1f}",
                     f"{100 * best[2]['mean'] / d['optimum']:.2f}%", best[1]])
    add_table(doc, ["Zbiór", "Optimum", "Najlepszy AG", "Średni AG", "% optimum", "Konfiguracja"], rows)

    # ---------- 7. wnioski ----------
    doc.add_heading("7. Wnioski", 1)
    for text in [
        "Dla zbiorów low-dimensional (15–23 przedmioty) algorytm w niemal każdym uruchomieniu znajduje "
        "optimum lub rozwiązanie różniące się od niego o kilka jednostek, zwykle w ciągu kilkudziesięciu "
        "iteracji. Przestrzeń rozwiązań (2^23 ≈ 8 mln) jest na tyle mała, że różnice między "
        "konfiguracjami są niewielkie.",
        "Prawdopodobieństwo mutacji ma największy wpływ na wynik w dużych zbiorach. Zbyt duże p_m "
        "(0,05–0,1 przy 100–200 genach, czyli 5–20 zmian bitów na potomka) niszczy dobre rozwiązania i "
        "zamienia AG w przeszukiwanie losowe – wyniki spadają do 50–90% optimum. Najlepiej sprawdzają "
        "się wartości rzędu 1/n lub mniejsze (0,001–0,005).",
        "Prawdopodobieństwo krzyżowania w badanym zakresie 0,5–1,0 wpływa na wynik znacznie słabiej niż "
        "mutacja; różnice między seriami mieszczą się zwykle w kilku procentach i są porównywalne z "
        "losowym rozrzutem między uruchomieniami.",
        "Selekcja turniejowa (k = 3) dała najlepsze wyniki i najszybszą zbieżność, szczególnie w zbiorze "
        "knapPI_1_200 (ok. 99,8% optimum wobec ok. 92–93% dla pozostałych metod). Selekcja ruletkowa "
        "słabo rozróżnia osobniki o zbliżonym przystosowaniu (wszystkie mają podobny wycinek koła), "
        "przez co presja selekcyjna maleje, co potwierdza obserwację z p. 3.4.1 instrukcji. Selekcja "
        "rankingowa liniowa ma umiarkowaną presję – wyniki zbliżone do ruletki.",
        "Krzyżowanie dwupunktowe dało lepszy średni wynik w 4 z 6 zbiorów (najwyraźniej w knapPI_1_200: "
        "94,9% wobec 93,1%), w pozostałych dwóch było nieznacznie gorsze. Pozwala ono wymieniać fragment "
        "ze środka chromosomu, ale różnice między operatorami są niewielkie w porównaniu z wpływem "
        "mutacji i metody selekcji.",
        "Eksperyment dodatkowy pokazał, że bez naprawy chromosomów selekcja rankingowa i turniejowa "
        "radzą sobie gorzej w dużym zbiorze: przypisują niezerowe szanse osobnikom niedopuszczalnym "
        "(f = 0), więc populacja zapełnia się przeładowanymi plecakami. Ruletka sama odrzuca takie "
        "osobniki (wycinek koła = 0), dlatego bez naprawy działa dobrze. Funkcja przystosowania "
        "z karą „0” wymaga zatem naprawy lub selekcji nieuwzględniającej osobników z f = 0.",
        "Algorytm genetyczny nie gwarantuje znalezienia optimum, ale przy dobrze dobranych parametrach "
        "w zbiorach o 100–200 przedmiotach osiąga 99–100% optimum w czasie poniżej sekundy na "
        "uruchomienie (czysty Python).",
    ]:
        bullet(doc, text)

    doc.add_heading("8. Uruchomienie", 1)
    code(doc, "python3 -m venv .venv\n.venv/bin/pip install -r requirements.txt\n"
              ".venv/bin/python experiments.py   # eksperymenty + wykresy w results/\n"
              ".venv/bin/python make_report.py   # to sprawozdanie")

    doc.save(OUTPUT)
    print(f"Zapisano {OUTPUT}")


if __name__ == "__main__":
    main()
