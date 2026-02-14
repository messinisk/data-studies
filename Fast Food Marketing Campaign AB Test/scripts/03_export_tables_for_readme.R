library(lme4)
library(lmerTest)

m <- lmer(SalesInThousands ~ Promotion + week + MarketSize + AgeOfStore + (1|LocationID), data=df)

s <- summary(m)

# -------------------------
# Random effects table
# -------------------------
vc <- as.data.frame(VarCorr(m))  # grp, var1, vcov, sdcor
re_tbl <- vc[, c("grp", "var1", "vcov", "sdcor")]
names(re_tbl) <- c("Group", "Effect", "Variance", "Std.Dev.")
re_tbl$Variance <- round(re_tbl$Variance, 2)
re_tbl$`Std.Dev.` <- round(re_tbl$`Std.Dev.`, 3)

# -------------------------
# Fixed effects table
# -------------------------
fe <- as.data.frame(coef(s))     # Estimate, Std. Error, df, t value, Pr(>|t|)
fe$Term <- rownames(fe)
fe <- fe[, c("Term", "Estimate", "Std. Error", "df", "t value", "Pr(>|t|)")]
names(fe) <- c("Term", "Estimate", "Std.Error", "df", "t", "p")
fe$Estimate  <- round(fe$Estimate, 5)
fe$Std.Error <- round(fe$Std.Error, 5)
fe$df        <- round(fe$df, 2)
fe$t         <- round(fe$t, 3)
fe$p         <- format.pval(fe$p, digits = 3, eps = 2e-16)

# -------------------------
# Print as GitHub Markdown tables (pipe)
# -------------------------
to_pipe <- function(d){
  header <- paste0("|", paste(names(d), collapse="|"), "|")
  sep    <- paste0("|", paste(rep("---", ncol(d)), collapse="|"), "|")
  rows <- apply(d, 1, function(r) paste0("|", paste(r, collapse="|"), "|"))
  paste(c(header, sep, rows), collapse="\n")
}

cat("### Random effects\n\n")
cat(to_pipe(re_tbl))
cat("\n\n### Fixed effects\n\n")
cat(to_pipe(fe))
cat("\n")
