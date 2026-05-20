library(ggplot2)
library(tidyr)
library(dplyr)

# Data: counts by category and year
# Note: Analytical on top, then Conceptual, then Theoretical in final plot order
library(readxl)
df <- read_excel("C:/Users/PMPONELA/OneDrive - CGIAR/CIMMYT/SOIL HEALTH WRITESHOP MALAWI 17-20 September/Reading Materials/50integrate/List of frameworks.xlsx")

df_yearly <- df %>%
  filter(no == 1) %>%
  rename(
    Theoretical = `Theoretical/principles`,
    Practical  = `Practical approaches`,
    Analytical  = `Analytical`
  ) %>%
  group_by(Year) %>%
  summarise(
    Theoretical = sum(`Theoretical`, na.rm = TRUE),
    Practical  = sum(`Practical`, na.rm = TRUE),
    Analytical  = sum(`Analytical`, na.rm = TRUE),
    .groups = "drop"
  )


# Pivot to long, drop zeros, set explicit factor order for vertical stacking
df_long <- df_yearly %>%
  pivot_longer(
    cols = c(Theoretical, Practical, Analytical),
    names_to = "Category",
    values_to = "Count"
  ) %>%
  filter(Count > 0) %>%
  mutate(
    Category = factor(
      Category,
      levels = c("Theoretical", "Practical", "Analytical")
    )
  )

# True area-proportional bubbles with counts labeled inside
ggplot(df_long, aes(x = Year, y = Category, size = Count)) +
  geom_point(shape = 21, fill = "grey", color = "black", stroke = 1, alpha = 0.6) +
  geom_text(aes(label = Count), size = 3, vjust = 0.5) +
  scale_size_area(max_size = 15, guide = "none") +
  scale_x_continuous(breaks = unique(df_yearly$Year)) +
  labs(x = "Year", y = "") +
  theme_minimal() +
  theme(
    axis.text.y = element_text(face = "bold"),
    plot.title = element_text(hjust = 0.5)
  )