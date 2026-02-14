library(readr)
library(dplyr)
library(ggplot2)
library(lme4)
library(lmerTest)

df <- read_csv("WA_Marketing-Campaign.csv") %>%
  mutate(
    Promotion = factor(Promotion),
    week = factor(week),
    MarketSize = factor(MarketSize),
    LocationID = factor(LocationID)
  )

dir.create("docs/figs", recursive = TRUE, showWarnings = FALSE)

p1 <- ggplot(df, aes(x = Promotion, y = SalesInThousands)) +
  geom_boxplot() +
  labs(title = "Sales by Promotion", x = "Promotion", y = "Sales (Thousands)")

ggsave("docs/figs/01_sales_by_promo.png", p1, width = 8, height = 5, dpi = 200)
