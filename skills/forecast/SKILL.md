---
name: forecast
description: >
  Forecast time series data using R's forecast::auto.arima. Use when the user
  wants to forecast numeric time series, predict future values, or fit ARIMA models.
  Do NOT use for classification, non-time-series regression, or when the user
  explicitly requests a different forecasting method.
allowed-tools: Bash(Rscript *)
---

Forecast time series using R's `forecast::auto.arima`.

## Quick Forecast

```r
Rscript -e '
library(forecast)

# Read data (CSV with date and value columns)
data <- read.csv("INPUT_FILE")
ts_data <- ts(data$VALUE_COLUMN, frequency=FREQUENCY)

# Fit auto.arima and forecast
fit <- auto.arima(ts_data)
fc <- forecast(fit, h=HORIZON)

# Print summary and forecasts
summary(fit)
print(fc)

# Save plot
png("forecast.png", width=800, height=400)
plot(fc, main="Forecast")
dev.off()

# Save forecasts to CSV
write.csv(data.frame(
  point=as.numeric(fc$mean),
  lo80=as.numeric(fc$lower[,1]),
  hi80=as.numeric(fc$upper[,1]),
  lo95=as.numeric(fc$lower[,2]),
  hi95=as.numeric(fc$upper[,2])
), "forecast_output.csv", row.names=FALSE)
'
```

## Parameters

- **FREQUENCY**: Observations per cycle (12=monthly, 4=quarterly, 52=weekly, 365=daily)
- **HORIZON**: Number of periods to forecast ahead
- **INPUT_FILE**: Path to CSV with time series data
- **VALUE_COLUMN**: Name of the numeric column to forecast

## Install R Dependencies

```bash
Rscript -e 'install.packages("forecast", repos="https://cloud.r-project.org")'
```

## When the User Asks

- "Forecast this data..." → Read the data, determine frequency, run auto.arima
- "Predict next N months/quarters..." → Set horizon=N, frequency accordingly
- "What model did it pick?" → Print `summary(fit)` — shows ARIMA(p,d,q) order, AICc, coefficients
- "Show the forecast" → Generate and display the forecast plot
