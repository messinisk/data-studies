import pandas as pd
from matplotlib import pyplot as plt


# diabazi csv
df = pd.read_csv("data/income_distribution/100_Largest_companies/Largest_Companies.csv")
df.head()

# anikatista  telia  me komma
df["Revenue (USD millions)"] = (
    df["Revenue (USD millions)"]
      .astype(str)
      .str.replace(",", ".", regex=False)
      .astype(float)
)

# anikatista  telia  me komma

df["Employees"] = (
    df["Employees"]
      .astype(str)
      .str.replace(".", "", regex=False)
      .str.replace(",", "", regex=False)
      .astype(float)
      
)

#  diagramma 1
rev_by_industry = (
    df.groupby("Industry")["Revenue (USD millions)"]
      .sum()
      .sort_values(ascending=False)
)

rev_by_industry.plot(kind="bar", figsize=(12,5), title="Συνολικά Έσοδα ανά Κλάδο")

#  diagramma 2
emp_by_industry = (
    df.groupby("Industry")["Employees"].sum()
      .sort_values(ascending=False)
)

emp_by_industry.plot(kind="bar", logy=True, figsize=(12,5))


#  diagramma 3
agg = (
    df.groupby("Industry")[["Revenue (USD millions)", "Employees"]]
      .sum()
)

agg.plot(
    kind="scatter",
    x="Employees",
    y="Revenue (USD millions)",
    figsize=(6,6),
    title="Έσοδα vs Εργαζόμενοι ανά Κλάδο"
)

#  diagramma 4
rev_by_hq = (
    df.groupby("Headquarters")["Revenue (USD millions)"]
      .sum()
      .sort_values(ascending=False)
      .head(10)
)

rev_by_hq.plot(kind="bar", title="Top-10 Έδρες βάσει Εσόδων")

#  apouikeysi  topika
rev_by_industry.plot(kind="bar", figsize=(12,5))
plt.tight_layout()
plt.savefig("figures/fig_01_revenue_by_industry.png", dpi=150)
plt.close()


"> pandoc  100_Largest_companies.md   -o 100_Largest_companies.html"


"""
μετανομασια  στηλων 
df = df.rename(columns={
    "Revenue (USD millions)": "revenue",
    "Employees": "employees",
    "Industry": "industry",
    "Headquarters": "hq"
})




Κανονικοποίηση όλων των στηλών (γενικός κανόνας)

df.columns = (
    df.columns
      .str.strip()
      .str.lower()
      .str.replace(" ", "_")
      .str.replace("[^a-z0-9_]", "", regex=True)
)


Πού μπαίνει η πληροφορία που “χάθηκε” (μονάδες);
plt.title("Συνολικά Έσοδα ανά Κλάδο (εκατ. USD)")
plt.ylabel("Έσοδα (εκατ. USD)")

❌ Με index

df.iloc[:, 3]


Πότε επιτρέπεται index (λίγες περιπτώσεις)

✔ Μόνο όταν:

γράφεις γενική συνάρτηση

δουλεύεις με temporary matrices

κάνεις καθαρά αριθμητικούς υπολογισμούς (π.χ. PCA)


X = df.select_dtypes("number").to_numpy()


"""