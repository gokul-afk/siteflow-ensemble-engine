package main

import (
	"fmt"
)

// AggregateForecasts takes raw results and returns the averaged forecast
func AggregateForecasts(results []ModelResult) ([]ForecastPoint, []string) {
	// Map to store sum of values per date: "2023-01-01" -> 300.5
	sums := make(map[string]float64)
	counts := make(map[string]int)
	var validSources []string
	
	// 1. Iterate over every model's result
	for _, res := range results {
		if res.Error != "" {
			continue // Skip failed models
		}
		
		validSources = append(validSources, res.Model)

		for _, point := range res.Forecast {
			sums[point.Date] += point.Value
			counts[point.Date]++
		}
	}

	if len(validSources) == 0 {
		fmt.Println("⚠️ All models failed!")
		return []ForecastPoint{}, []string{}
	}

	// 2. Calculate Averages
	var ensemble []ForecastPoint
	// Note: In production, you would sort keys to ensure date order. 
	// For this MVP, we rely on the map iteration order (or usually input order).
	// Ideally, grab the date keys from the first valid result to keep order.
	
	if len(results) > 0 && len(results[0].Forecast) > 0 {
		// Use the dates from the first model to maintain order
		for _, refPoint := range results[0].Forecast {
			date := refPoint.Date
			if count, exists := counts[date]; exists && count > 0 {
				avg := sums[date] / float64(count)
				ensemble = append(ensemble, ForecastPoint{
					Date:  date,
					Value: avg,
				})
			}
		}
	}

	return ensemble, validSources
}