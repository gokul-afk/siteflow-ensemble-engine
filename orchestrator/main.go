package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"time"
)

// Define the Final Response format for the Frontend
type APIResponse struct {
	SiteID    int             `json:"site_id"`
	Algorithm string          `json:"algorithm"` // "Ensemble"
	Forecast  []ForecastPoint `json:"forecast"`
	Sources   []string        `json:"sources"` // List of models used (Prophet, SARIMA)
	Latency   string          `json:"latency"`
}

func forecastHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()

	// 1. Parse Query Params (e.g., /forecast?site_id=101)
	queryID := r.URL.Query().Get("site_id")
	if queryID == "" {
		http.Error(w, "Missing site_id parameter", http.StatusBadRequest)
		return
	}
	siteID, err := strconv.Atoi(queryID)
	if err != nil {
		http.Error(w, "Invalid site_id", http.StatusBadRequest)
		return
	}

	fmt.Printf("📡 Received request for Site %d\n", siteID)

	// 2. EXECUTOR: Run Python models in parallel
	// We ask for these models specifically
	models := []string{"prophet", "sarima", "xgboost"}
	rawResults := RunEnsemble(siteID, models)

	// 3. AGGREGATOR: Combine the results
	finalForecast, validSources := AggregateForecasts(rawResults)

	// 4. Send Response
	response := APIResponse{
		SiteID:    siteID,
		Algorithm: "Ensemble-Weighted-Average",
		Forecast:  finalForecast,
		Sources:   validSources,
		Latency:   time.Since(start).String(),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/forecast", forecastHandler)

	port := ":8080"
	fmt.Printf("🚀 SitePredict Engine running on port %s\n", port)
	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatal(err)
	}
}
