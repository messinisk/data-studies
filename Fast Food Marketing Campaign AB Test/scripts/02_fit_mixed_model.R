p2 <- ggplot(df, aes(x = Promotion, y = SalesInThousands)) +
  geom_boxplot() +
  facet_wrap(~ MarketSize) +
  labs(title = "Sales by Promotion across Market Size", x = "Promotion", y = "Sales (Thousands)")

ggsave("docs/figs/02_sales_by_promo_market.png", p2, width = 10, height = 5, dpi = 200)

sum_week <- df %>%
  group_by(Promotion, week) %>%
  summarise(
    mean = mean(SalesInThousands),
    se = sd(SalesInThousands) / sqrt(n()),
    .groups = "drop"
  ) %>%
  mutate(
    lo = mean - 1.96 * se,
    hi = mean + 1.96 * se
  )

p3 <- ggplot(sum_week, aes(x = week, y = mean, group = Promotion)) +
  geom_line() +
  geom_point() +
  geom_errorbar(aes(ymin = lo, ymax = hi), width = 0.15) +
  labs(title = "Weekly mean sales by Promotion (±95% CI)", x = "Week", y = "Mean Sales (Thousands)")

ggsave("docs/figs/03_weekly_means_ci.png", p3, width = 9, height = 5, dpi = 200)

m <- lmer(SalesInThousands ~ Promotion + week + MarketSize + AgeOfStore + (1|LocationID), data = df)

ri <- ranef(m)$LocationID
ri$LocationID <- rownames(ri)
colnames(ri)[1] <- "b0"

ri <- ri %>% arrange(b0) %>% mutate(LocationID = factor(LocationID, levels = LocationID))

p4 <- ggplot(ri, aes(x = LocationID, y = b0)) +
  geom_point() +
  coord_flip() +
  labs(title = "Random intercepts per Location (store effects)", x = "LocationID", y = "Random intercept (b0)")

ggsave("docs/figs/04_random_intercepts.png", p4, width = 8, height = 10, dpi = 200)

df_diag <- data.frame(
  fitted = fitted(m),
  resid = resid(m)
)

p5 <- ggplot(df_diag, aes(x = fitted, y = resid)) +
  geom_point(alpha = 0.6) +
  geom_hline(yintercept = 0, linetype = "dashed") +
  labs(title = "Residuals vs Fitted", x = "Fitted", y = "Residuals")

ggsave("docs/figs/05_resid_vs_fitted.png", p5, width = 8, height = 5, dpi = 200)

p6 <- ggplot(df_diag, aes(sample = resid)) +
  stat_qq() +
  stat_qq_line() +
  labs(title = "QQ plot of residuals")

ggsave("docs/figs/06_qq_residuals.png", p6, width = 8, height = 5, dpi = 200)

